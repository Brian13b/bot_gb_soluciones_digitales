from sqlalchemy.orm import Session
import uuid
import re

from shared.models import Conversation, Message, Contact, SourceField, ExtractionMethod, ValidationStatus

def get_or_create_conversation(db: Session, session_id: str, channel: str = "web"):
    """
    Busca la conversación por session_id. Si no existe, la crea.
    Esto permite la 'omnipresencia' del bot en cualquier sesión que envíes.
    """
    conversation = db.query(Conversation).filter(
        Conversation.session_id == session_id,
        Conversation.channel == channel
    ).first()

    if not conversation:
        conversation = Conversation(session_id=session_id, channel=channel)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    return conversation

def update_conversation_state(db: Session, conversation_id: uuid.UUID, contact_info: str = None, estado: str = "B"):
    """
    Actualiza la conversación cuando se detecta un cambio de estado o se captura el lead.
    """
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        if contact_info:
            conversation.contact_info = contact_info
        if estado:
            conversation.estado = estado
        db.commit()
        db.refresh(conversation)
    return conversation

def add_message(db: Session, conversation_id: uuid.UUID, role: str, content: str):
    """
    Guarda un mensaje individual (del usuario o del asistente).
    """
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_conversation_history(db: Session, conversation_id: uuid.UUID, limit: int = 8):
    """
    Trae los últimos mensajes formateados exactamente como los pide OpenAI.
    Limitado a 8 para no gastar tokens innecesarios ni marear a GPT.
    """
    messages = db.query(Message).filter(Message.conversation_id == conversation_id)\
                 .order_by(Message.created_at.asc())\
                 .limit(limit).all()

    history = [{"role": msg.role, "content": msg.content} for msg in messages]
    return history


def _validate_email(email: str) -> bool:
    """Valida formato de email con regex"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def _validate_phone(phone: str) -> bool:
    """Valida teléfono: mínimo 7 dígitos (con prefijos internacionales)"""
    if not phone:
        return False
    # Solo dígitos y símbolos permitidos (+ para código país)
    cleaned = re.sub(r'[^\d+]', '', phone)
    return len(cleaned) >= 7


def save_contact(
    db: Session,
    conversation_id: uuid.UUID,
    name: str = None,
    email: str = None,
    phone: str = None,
    source_field: SourceField = SourceField.FROM_MESSAGE,
    extraction_method: ExtractionMethod = ExtractionMethod.REGEX,
    confidence_score: float = 0.0
) -> Contact:
    """
    Guarda contacto extraído con validación básica.

    Args:
        db: Session de SQLAlchemy
        conversation_id: UUID de la conversación
        name: Nombre del contacto
        email: Email del contacto
        phone: Teléfono del contacto
        source_field: Origen del campo (FROM_MESSAGE, FROM_WHATSAPP_HEADER, etc.)
        extraction_method: Método de extracción (REGEX, EXPLICIT_QUESTION, etc.)
        confidence_score: Confianza de la extracción (0.0-1.0)

    Returns:
        Contact object creado, o None si no hay datos válidos
    """
    # Validar datos
    validated_email = email if _validate_email(email) else None
    validated_phone = phone if _validate_phone(phone) else None
    validated_name = name.strip() if name and isinstance(name, str) else None

    # No guardar si no hay al menos un dato válido
    if not (validated_name or validated_email or validated_phone):
        return None

    # Determinar validation_status basado en calidad
    if confidence_score >= 0.8:
        validation_status = ValidationStatus.PENDING  # Requiere verificación manual si es de alta confianza
    else:
        validation_status = ValidationStatus.PENDING

    contact = Contact(
        conversation_id=conversation_id,
        name=validated_name,
        email=validated_email,
        phone=validated_phone,
        source_field=source_field,
        extraction_method=extraction_method,
        validation_status=validation_status,
        confidence_score=confidence_score,
        captured_by="bot_gpt4"
    )

    db.add(contact)
    db.commit()
    db.refresh(contact)

    return contact