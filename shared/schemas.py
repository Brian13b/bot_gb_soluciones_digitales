"""
Unified Pydantic schemas for Bot and Admin services.
Single source of truth to avoid duplication and divergence.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime


# ==========================================
# WEB CHAT SCHEMAS (Bot Service)
# ==========================================
class ChatWebRequest(BaseModel):
    """Request payload for web chat endpoint."""
    session_id: str = Field(..., description="El ID único del visitante anónimo")
    mensaje: str = Field(..., description="El texto escrito por el usuario")
    contact_name: Optional[str] = Field(None, description="Nombre del contacto (opcional)")
    contact_phone: Optional[str] = Field(None, description="Teléfono del contacto (opcional)")
    contact_email: Optional[str] = Field(None, description="Email del contacto (opcional)")


class ChatResponse(BaseModel):
    """Response payload from chat endpoint."""
    respuesta: str
    estado_actual: str


# ==========================================
# WHATSAPP WEBHOOK SCHEMAS (Bot Service)
# ==========================================
class WhatsAppMessage(BaseModel):
    """Individual WhatsApp message from Meta Cloud API."""
    from_number: str
    text: str


class WhatsAppPayload(BaseModel):
    """Complete webhook payload from Meta."""
    object: str
    entry: List[dict]


# ==========================================
# MESSAGE SCHEMAS (Admin Service)
# ==========================================
class MessageCreate(BaseModel):
    """Create new message."""
    role: str
    content: str


class MessageSchema(BaseModel):
    """Message detail (for lists and conversation details)."""
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
    """Conversation summary for list views."""
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
    """Conversation with full message history."""
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


# Legacy alias for backward compatibility (Bot service may use this)
class ConversationSchema(ConversationDetailSchema):
    """Backward compatibility alias. Use ConversationDetailSchema instead."""
    pass


# ==========================================
# CONTACT ATTEMPT SCHEMAS (Admin Service)
# ==========================================
class ContactAttemptCreate(BaseModel):
    """Create new contact attempt."""
    method: str = Field(..., description="Contact method: whatsapp, email, call, other")
    notes: Optional[str] = Field(None, description="Additional notes about the attempt")


class ContactAttemptSchema(BaseModel):
    """Contact attempt detail."""
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
    """Create new user (registration)."""
    email: str
    password: str


class UserResponse(BaseModel):
    """User information response."""
    id: UUID
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Login credentials."""
    email: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    email: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str
