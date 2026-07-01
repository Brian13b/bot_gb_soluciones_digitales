import re
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from bot.database import get_db
from shared.schemas import ChatWebRequest, ChatResponse
from shared.models import SourceField, ExtractionMethod
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
    Recibe un session_id (anónimo) y el mensaje.

    Flujo:
    1. Obtiene/crea conversación
    2. Guarda mensaje del usuario
    3. Obtiene historial
    4. Procesa con bot (retorna respuesta + extracción JSON)
    5. Guarda contacto si se extrajo con confianza > 0.7
    6. Actualiza estado de conversación si se capturó contacto
    7. Guarda respuesta del bot
    """
    conversation = crud.get_or_create_conversation(db, request_data.session_id, channel="web")

    crud.add_message(db, conversation.id, role="user", content=request_data.mensaje)

    history = crud.get_conversation_history(db, conversation.id)

    # NUEVO: bot retorna diccionario con respuesta y extracción
    bot_output = bot.procesar(request_data.mensaje, history=history, channel="web")
    respuesta_ia = bot_output["respuesta"]
    extracted_contact = bot_output.get("extracted_contact", {})

    # NUEVO: Guardar contacto extraído si tiene confianza suficiente
    if extracted_contact.get("extraction_confidence", 0) > 0.7:
        extraction_method_str = extracted_contact.get("extraction_method", "none").upper()
        # Mapear a enum
        if extraction_method_str == "EXPLICIT_QUESTION":
            extraction_method = ExtractionMethod.EXPLICIT_QUESTION
        elif extraction_method_str == "REGEX_DETECTED":
            extraction_method = ExtractionMethod.REGEX
        else:
            extraction_method = ExtractionMethod.USER_INPUT

        contact = crud.save_contact(
            db,
            conversation.id,
            name=extracted_contact.get("name"),
            email=extracted_contact.get("email"),
            phone=extracted_contact.get("phone"),
            source_field=SourceField.FROM_MESSAGE,
            extraction_method=extraction_method,
            confidence_score=extracted_contact.get("extraction_confidence", 0.0)
        )

        # NUEVO: Transicionar a estado B si capturó al menos un dato
        if contact:
            conversation.estado = "B"
            db.commit()

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

                # NUEVO: bot retorna diccionario con respuesta y extracción
                bot_output = bot.procesar(mensaje_usuario, history=history, channel="whatsapp")
                respuesta_ia = bot_output["respuesta"]
                extracted_contact = bot_output.get("extracted_contact", {})

                # NUEVO: Guardar contacto extraído si tiene confianza suficiente
                if extracted_contact.get("extraction_confidence", 0) > 0.7:
                    extraction_method_str = extracted_contact.get("extraction_method", "none").upper()
                    # Mapear a enum
                    if extraction_method_str == "EXPLICIT_QUESTION":
                        extraction_method = ExtractionMethod.EXPLICIT_QUESTION
                    elif extraction_method_str == "REGEX_DETECTED":
                        extraction_method = ExtractionMethod.REGEX
                    else:
                        extraction_method = ExtractionMethod.USER_INPUT

                    contact = crud.save_contact(
                        db,
                        conversation.id,
                        name=extracted_contact.get("name"),
                        email=extracted_contact.get("email"),
                        phone=extracted_contact.get("phone"),
                        source_field=SourceField.FROM_WHATSAPP_HEADER,
                        extraction_method=extraction_method,
                        confidence_score=extracted_contact.get("extraction_confidence", 0.0)
                    )

                    # NUEVO: Transicionar a estado B si capturó al menos un dato
                    if contact:
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