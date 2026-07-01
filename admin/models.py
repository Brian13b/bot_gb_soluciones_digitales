from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid
 
Base = declarative_base()
 
# ==========================================
# MODEL: User (Admin Panel)
# ==========================================
class User(Base):
    __tablename__ = "users"
 
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
 
    # Relaciones
    contact_attempts = relationship("ContactAttempt", back_populates="developer")
 
    def __repr__(self):
        return f"<User(email='{self.email}', is_active={self.is_active})>"
 
 
# ==========================================
# MODEL: Conversation (Bot Visitors)
# ==========================================
class Conversation(Base):
    __tablename__ = "conversations"
 
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    channel = Column(String(50), nullable=False)
    contact_name = Column(String(255))
    contact_phone = Column(String(20))
    contact_email = Column(String(255))
    estado = Column(String(50), default="abierta", index=True)
    proyecto_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
 
    # Relaciones
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    contact_attempts = relationship("ContactAttempt", back_populates="conversation", cascade="all, delete-orphan")
 
    def __repr__(self):
        return f"<Conversation(session_id='{self.session_id}', canal='{self.channel}', estado='{self.estado}')>"
 
 
# ==========================================
# MODEL: Message
# ==========================================
class Message(Base):
    __tablename__ = "messages"
 
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
 
    # Relaciones
    conversation = relationship("Conversation", back_populates="messages")
 
    def __repr__(self):
        return f"<Message(conversation_id='{self.conversation_id}', role='{self.role}')>"
 
 
# ==========================================
# MODEL: ContactAttempt (Historial de contactos)
# ==========================================
class ContactAttempt(Base):
    __tablename__ = "contact_attempts"
 
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    developer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    method = Column(String(50), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
 
    # Relaciones
    conversation = relationship("Conversation", back_populates="contact_attempts")
    developer = relationship("User", back_populates="contact_attempts")
 
    def __repr__(self):
        return f"<ContactAttempt(developer_id='{self.developer_id}', method='{self.method}', created_at='{self.created_at}')>"