from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
 
# ==========================================
# AUTH SCHEMAS
# ==========================================
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
 
 
# ==========================================
# USER SCHEMAS
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
 
 
# ==========================================
# MESSAGE SCHEMAS
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
# CONVERSATION SCHEMAS
# ==========================================
class ConversationListSchema(BaseModel):
    id: UUID
    session_id: str
    channel: str
    contact_name: Optional[str]
    contact_phone: Optional[str]
    contact_email: Optional[str]
    estado: str
    message_count: int = 0
    last_message_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
 
    class Config:
        from_attributes = True
 
class ConversationDetailSchema(BaseModel):
    id: UUID
    session_id: str
    channel: str
    contact_name: Optional[str]
    contact_phone: Optional[str]
    contact_email: Optional[str]
    estado: str
    messages: List[MessageSchema] = []
    created_at: datetime
    updated_at: datetime
 
    class Config:
        from_attributes = True
 
 
# ==========================================
# CONTACT ATTEMPT SCHEMAS
# ==========================================
class ContactAttemptCreate(BaseModel):
    method: str = Field(..., description="whatsapp, email, other")
    notes: Optional[str] = None
 
class ContactAttemptSchema(BaseModel):
    id: UUID
    developer_id: UUID
    method: str
    notes: Optional[str]
    created_at: datetime
 
    class Config:
        from_attributes = True
 
 
# ==========================================
# BOT SCHEMAS (Mantener compatibilidad)
# ==========================================
class ChatWebRequest(BaseModel):
    session_id: str = Field(..., description="El ID único del visitante anónimo")
    mensaje: str = Field(..., description="El texto escrito por el usuario")
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
 
class ChatResponse(BaseModel):
    respuesta: str
    estado_actual: str
 
class WhatsAppMessage(BaseModel):
    from_number: str
    text: str
 
class WhatsAppPayload(BaseModel):
    object: str
    entry: List[dict]