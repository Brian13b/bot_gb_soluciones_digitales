import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from bot.database import get_db
from shared.schemas import ChatWebRequest, ChatResponse
from bot import crud
from bot.bot_logic import BotLogic
from bot.core.config import settings
from bot.core.security import verify_webhook_signature

router = APIRouter()
bot = BotLogic()

# ==========================================
# RUTAS PARA LA WEB WIDGET
# ==========================================

@router.post("/chat-web", response_model=ChatResponse)
async def chat_web(request_data: ChatWebRequest, db: Session = Depends(get_db)):
    """
    Endpoint para el chat flotante de React.
    Implementa máquina de estados de 5 pasos para captura de contactos.

    Flujo de estados:
    - NONE: Sin flujo de captura activo
    - STEP_1: Acabo de hacer resumen, esperando respuesta del usuario
    - STEP_2: Pidiendo nombre
    - STEP_3: Pidiendo preferencia (WhatsApp o email)
    - STEP_4: Pidiendo dato específico (teléfono o email)
    - COMPLETED: Flujo terminado
    """
    conversation = crud.get_or_create_conversation(db, request_data.session_id, channel="web")
    current_step = conversation.capture_step

    # Guardar mensaje del usuario
    crud.add_message(db, conversation.id, role="user", content=request_data.mensaje)

    # Obtener historial para el bot
    history = crud.get_conversation_history(db, conversation.id)

    # Procesar con el bot
    respuesta_ia = bot.procesar(request_data.mensaje, history=history, channel="web")

    # ══════════════════════════════════════════════════════════════
    # MÁQUINA DE ESTADOS: Detectar transiciones y extraer datos
    # ══════════════════════════════════════════════════════════════

    if current_step == "NONE":
        # Detectar si la respuesta del bot fue ESTADO B (resumen + pregunta de nombre)
        # El bot debería haber hecho el resumen y preguntado por el nombre
        # Si la respuesta contiene "¿Cuál es tu nombre?" → transicionar a STEP_1
        if "¿cuál es tu nombre?" in respuesta_ia.lower() or "nombre" in respuesta_ia.lower():
            crud.update_capture_step(db, conversation.id, "STEP_1")

    elif current_step == "STEP_1":
        # El usuario respondió al resumen, esperamos nombre
        # Intentar extraer nombre del mensaje del usuario
        nombre = crud.extract_name_from_text(request_data.mensaje)
        if nombre:
            crud.save_name_to_conversation(db, conversation.id, nombre)
            crud.update_capture_step(db, conversation.id, "STEP_2")
        # Si no se extrajo nombre, el bot volverá a preguntar

    elif current_step == "STEP_2":
        # El usuario debería haber respondido al "¿cómo preferís que te contactemos?"
        # Detectar WhatsApp o email en la respuesta
        mensaje_lower = request_data.mensaje.lower()
        if "whatsapp" in mensaje_lower or "teléfono" in mensaje_lower or "telefono" in mensaje_lower:
            crud.update_capture_step(db, conversation.id, "STEP_3_WHATSAPP")
        elif "email" in mensaje_lower or "correo" in mensaje_lower:
            crud.update_capture_step(db, conversation.id, "STEP_3_EMAIL")
        # Si no se detecta preferencia, el bot volverá a preguntar

    elif current_step == "STEP_3_WHATSAPP":
        # El usuario debe proporcionar su teléfono
        telefono = crud.extract_phone_from_text(request_data.mensaje)
        if telefono:
            crud.save_phone_to_conversation(db, conversation.id, telefono)
            crud.update_capture_step(db, conversation.id, "COMPLETED")
            # Transicionar a estado B (lead)
            conversation.estado = "B"
            db.commit()

    elif current_step == "STEP_3_EMAIL":
        # El usuario debe proporcionar su email
        email = crud.extract_email_from_text(request_data.mensaje)
        if email:
            crud.save_email_to_conversation(db, conversation.id, email)
            crud.update_capture_step(db, conversation.id, "COMPLETED")
            # Transicionar a estado B (lead)
            conversation.estado = "B"
            db.commit()

    elif current_step == "COMPLETED":
        # El flujo de captura terminó, no cambiar estado
        pass

    # Guardar respuesta del bot
    crud.add_message(db, conversation.id, role="assistant", content=respuesta_ia)

    return ChatResponse(
        respuesta=respuesta_ia,
        estado_actual=conversation.estado
    )

# ==========================================
# RUTAS PARA WHATSAPP
# ==========================================

@router.get("/webhook")
async def verify_webhook(request: Request):
    """Ruta de verificación para Meta (GET request during webhook setup)"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        print("✅ Webhook verificado exitosamente por Meta!")
        return int(challenge)
    raise HTTPException(status_code=403, detail="❌ Error de verificación del webhook")

@router.post("/webhook")
async def handle_message(request: Request, db: Session = Depends(get_db)):
    """
    Recepción y procesamiento de mensajes de WhatsApp.
    Valida firma HMAC SHA-256 para prevenir webhooks falsificados.
    """
    # Get the raw body for signature verification
    body = await request.body()

    # Get the signature from the header
    x_hub_signature_256 = request.headers.get("X-Hub-Signature-256")

    # Verify webhook signature (prevents spoofed webhooks from Meta)
    if not verify_webhook_signature(body, x_hub_signature_256):
        raise HTTPException(
            status_code=401,
            detail="❌ Firma de webhook inválida. Acceso denegado."
        )

    # Parse JSON after signature validation
    data = await request.json()
    
    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if messages:
            mensaje_obj = messages[0]
            if mensaje_obj.get("type") == "text":
                mensaje_usuario = mensaje_obj.get("text", {}).get("body", "")
                numero_cliente = mensaje_obj.get("from")
                
                print(f"Mensaje entrante de {numero_cliente}: {mensaje_usuario}")
                
                conversation = crud.get_or_create_conversation(db, session_id=numero_cliente, channel="whatsapp")
                
                history = crud.get_conversation_history(db, conversation.id)
                if len(history) == 0:
                    bienvenida = "¡Hola! Soy GiBi, el asistente virtual de GB Soluciones Digitales. ¿En qué te puedo ayudar hoy?"
                    crud.add_message(db, conversation.id, role="assistant", content=bienvenida)
                    await enviar_mensaje_whatsapp(numero_cliente, bienvenida)
                    return {"status": "ok"}
                
                crud.add_message(db, conversation.id, role="user", content=mensaje_usuario)

                current_step = conversation.capture_step

                # Procesar con bot
                respuesta_ia = bot.procesar(mensaje_usuario, history=history, channel="whatsapp")

                # ══════════════════════════════════════════════════════════════
                # MÁQUINA DE ESTADOS: Detectar transiciones y extraer datos
                # ══════════════════════════════════════════════════════════════

                if current_step == "NONE":
                    if "¿cuál es tu nombre?" in respuesta_ia.lower() or "nombre" in respuesta_ia.lower():
                        crud.update_capture_step(db, conversation.id, "STEP_1")

                elif current_step == "STEP_1":
                    nombre = crud.extract_name_from_text(mensaje_usuario)
                    if nombre:
                        crud.save_name_to_conversation(db, conversation.id, nombre)
                        crud.update_capture_step(db, conversation.id, "STEP_2")

                elif current_step == "STEP_2":
                    mensaje_lower = mensaje_usuario.lower()
                    if "whatsapp" in mensaje_lower or "teléfono" in mensaje_lower or "telefono" in mensaje_lower:
                        crud.update_capture_step(db, conversation.id, "STEP_3_WHATSAPP")
                    elif "email" in mensaje_lower or "correo" in mensaje_lower:
                        crud.update_capture_step(db, conversation.id, "STEP_3_EMAIL")

                elif current_step == "STEP_3_WHATSAPP":
                    telefono = crud.extract_phone_from_text(mensaje_usuario)
                    if telefono:
                        crud.save_phone_to_conversation(db, conversation.id, telefono)
                        crud.update_capture_step(db, conversation.id, "COMPLETED")
                        conversation.estado = "B"
                        db.commit()

                elif current_step == "STEP_3_EMAIL":
                    email = crud.extract_email_from_text(mensaje_usuario)
                    if email:
                        crud.save_email_to_conversation(db, conversation.id, email)
                        crud.update_capture_step(db, conversation.id, "COMPLETED")
                        conversation.estado = "B"
                        db.commit()

                crud.add_message(db, conversation.id, role="assistant", content=respuesta_ia)

                await enviar_mensaje_whatsapp(numero_cliente, respuesta_ia)
                
    except Exception as e:
        print(f"Error parseando el webhook de Meta: {e}")
        
    return {"status": "ok"}

async def enviar_mensaje_whatsapp(numero, texto):
    """Ejecuta un POST a la Graph API de Meta para enviar la respuesta"""
    url = f"https://graph.facebook.com/v19.0/{settings.PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texto}
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"Fallo al enviar mensaje. Meta respondió: {response.text}")