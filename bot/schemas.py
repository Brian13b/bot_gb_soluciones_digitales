"""
Bot Schemas - Compatibility wrapper.

DEPRECATED: All schemas have been consolidated to shared/schemas.py
This file is maintained for backward compatibility only.

Import directly from shared.schemas instead.
"""

from shared.schemas import (
    ChatWebRequest,
    ChatResponse,
    WhatsAppMessage,
    WhatsAppPayload,
    MessageSchema,
    ConversationSchema,
)

__all__ = [
    "ChatWebRequest",
    "ChatResponse",
    "WhatsAppMessage",
    "WhatsAppPayload",
    "MessageSchema",
    "ConversationSchema",
]
