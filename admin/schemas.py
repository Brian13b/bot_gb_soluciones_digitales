"""
Admin Schemas - Compatibility wrapper.

DEPRECATED: All schemas have been consolidated to shared/schemas.py
This file is maintained for backward compatibility only.

Import directly from shared.schemas instead.
"""

from shared.schemas import (
    # Auth Schemas
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    # User Schemas
    UserCreate,
    UserResponse,
    # Message Schemas
    MessageCreate,
    MessageSchema,
    # Conversation Schemas
    ConversationListSchema,
    ConversationDetailSchema,
    ConversationSchema,
    # Contact Attempt Schemas
    ContactAttemptCreate,
    ContactAttemptSchema,
    # Bot Schemas (for compatibility)
    ChatWebRequest,
    ChatResponse,
    WhatsAppMessage,
    WhatsAppPayload,
)

__all__ = [
    # Auth Schemas
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    # User Schemas
    "UserCreate",
    "UserResponse",
    # Message Schemas
    "MessageCreate",
    "MessageSchema",
    # Conversation Schemas
    "ConversationListSchema",
    "ConversationDetailSchema",
    "ConversationSchema",
    # Contact Attempt Schemas
    "ContactAttemptCreate",
    "ContactAttemptSchema",
    # Bot Schemas
    "ChatWebRequest",
    "ChatResponse",
    "WhatsAppMessage",
    "WhatsAppPayload",
]
