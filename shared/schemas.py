from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime


# ==========================================
# WEB CHAT SCHEMAS (Bot Service)
# ==========================================
class ChatWebRequest(BaseModel):
    session_id: str = Field(..., description="El ID único del visitante anónimo")
    mensaje: str = Field(..., description="El texto escrito por el usuario")
    contact_name: Optional[str] = Field(None, description="Nombre del contacto (opcional)")
    contact_phone: Optional[str] = Field(None, description="Teléfono del contacto (opcional)")
    contact_email: Optional[str] = Field(None, description="Email del contacto (opcional)")


class ChatResponse(BaseModel):
    respuesta: str
    estado_actual: str


# ==========================================
# WHATSAPP WEBHOOK SCHEMAS (Bot Service)
# ==========================================
class WhatsAppMessage(BaseModel):
    from_number: str
    text: str


class WhatsAppPayload(BaseModel):
    object: str
    entry: List[dict]


# ==========================================
# MESSAGE SCHEMAS (Admin Service)
# ==========================================
class MessageCreate(BaseModel):
    role: str
    content: str


class MessageSchema(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# CONVERSATION SCHEMAS (Admin Service)
# ==========================================
class ConversationListSchema(BaseModel):
    id: UUID
    session_id: str
    channel: str
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    estado: str
    message_count: int = 0
    last_message_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationDetailSchema(BaseModel):
    id: UUID
    session_id: str
    channel: str
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    estado: str
    messages: List[MessageSchema] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationSchema(ConversationDetailSchema):
    pass


# ==========================================
# CONTACT ATTEMPT SCHEMAS (Admin Service)
# ==========================================
class ContactAttemptCreate(BaseModel):
    method: str = Field(..., description="Contact method: whatsapp, email, call, other")
    notes: Optional[str] = Field(None, description="Additional notes about the attempt")


class ContactAttemptSchema(BaseModel):
    id: UUID
    developer_id: UUID
    method: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# USER & AUTH SCHEMAS (Admin Service)
# ==========================================
class UserCreate(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    email: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
