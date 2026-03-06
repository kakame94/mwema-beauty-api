from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict


class WhatsAppMessageText(BaseModel):
    body: str

class WhatsAppMessageImage(BaseModel):
    id: str
    mime_type: str
    sha256: Optional[str] = None
    caption: Optional[str] = None

class WhatsAppMessage(BaseModel):
    from_: str = Field(..., alias="from")
    id: str
    timestamp: str
    type: str
    text: Optional[WhatsAppMessageText] = None
    image: Optional[WhatsAppMessageImage] = None

class WhatsAppValue(BaseModel):
    messaging_product: str
    metadata: Dict[str, Any]
    contacts: Optional[List[Dict[str, Any]]] = None
    messages: Optional[List[WhatsAppMessage]] = None

class WhatsAppChange(BaseModel):
    value: WhatsAppValue
    field: str

class WhatsAppEntry(BaseModel):
    id: str
    changes: List[WhatsAppChange]

class WhatsAppWebhookPayload(BaseModel):
    object: str
    entry: List[WhatsAppEntry]
