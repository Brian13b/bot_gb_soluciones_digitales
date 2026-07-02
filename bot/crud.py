from sqlalchemy.orm import Session
import uuid
import re
from datetime import datetime

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
    """Valida formato de email con regex tolerando espacios accidentales"""
    if not email:
        return False
    clean_email = email.strip()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, clean_email) is not None


def _validate_phone(phone: str) -> bool:
    """Valida teléfono: mínimo 7 dígitos (con prefijos internacionales)"""
    if not phone:
        return False
    phone_str = str(phone).strip()
    cleaned = re.sub(r'[^\d+]', '', phone_str)
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
    """Guarda contacto extraído con validación básica."""
    
    validated_email = email.strip() if email and _validate_email(email) else None
    validated_phone = str(phone).strip() if phone and _validate_phone(phone) else None
    validated_name = name.strip() if name and isinstance(name, str) else None

    if not (validated_name or validated_email or validated_phone):
        return None

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


# ==========================================
# STATE MACHINE FUNCTIONS (Capture Steps)
# ==========================================

def update_capture_step(db: Session, conversation_id: uuid.UUID, new_step: str) -> Conversation:
    """
    Actualiza el paso de captura en la conversación.

    Pasos válidos: NONE, STEP_1, STEP_2, STEP_3, STEP_4, COMPLETED
    """
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        conversation.capture_step = new_step
        conversation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(conversation)
    return conversation


def extract_name_from_text(text: str) -> str:
    """
    Extrae nombre del texto (búsqueda simple).
    Busca patrones como: "Soy Juan", "Me llamo Juan", "Juan García"

    Retorna el nombre o None si no encuentra algo convincente.
    """
    if not text or len(text) < 2:
        return None

    # Patrones comunes
    patterns = [
        r'(?:soy|me llamo|nombre es|es)\s+([A-Z][a-zá-ú]+(?:\s+[A-Z][a-zá-ú]+)?)',
        r'^([A-Z][a-zá-ú]+(?:\s+[A-Z][a-zá-ú]+)?)$'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def extract_phone_from_text(text: str) -> str:
    """
    Extrae teléfono del texto.
    Busca: +34912345678, +54 9 11 2345 6789, 1234567, etc.
    """
    if not text:
        return None

    # Buscar patrones de teléfono
    phone_pattern = r'(?:\+\d{1,3}[\s-]?)?\d{7,15}'
    match = re.search(phone_pattern, text)

    if match:
        phone = match.group(0)
        # Limpiar espacios y guiones
        cleaned = re.sub(r'[\s-]', '', phone)
        if _validate_phone(cleaned):
            return cleaned

    return None


def extract_email_from_text(text: str) -> str:
    """
    Extrae email del texto.
    Busca: user@domain.com
    """
    if not text:
        return None

    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)

    if match:
        email = match.group(0)
        if _validate_email(email):
            return email

    return None


def save_name_to_conversation(db: Session, conversation_id: uuid.UUID, name: str) -> Conversation:
    """
    Guarda el nombre extraído en contact_name de Conversation (campo legacy).
    """
    if not name or not isinstance(name, str):
        return None

    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        conversation.contact_name = name.strip()
        conversation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(conversation)

    return conversation


def save_phone_to_conversation(db: Session, conversation_id: uuid.UUID, phone: str) -> Conversation:
    """
    Guarda el teléfono extraído en contact_phone de Conversation (campo legacy).
    """
    if not phone:
        return None

    cleaned_phone = re.sub(r'[^\d+]', '', phone)
    if not _validate_phone(cleaned_phone):
        return None

    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        conversation.contact_phone = cleaned_phone
        conversation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(conversation)

    return conversation


def save_email_to_conversation(db: Session, conversation_id: uuid.UUID, email: str) -> Conversation:
    """
    Guarda el email extraído en contact_email de Conversation (campo legacy).
    """
    if not email or not _validate_email(email):
        return None

    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        conversation.contact_email = email
        conversation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(conversation)

    return conversation