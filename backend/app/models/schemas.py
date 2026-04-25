from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

# ─── INVENTORY MODELS ───────────────────────────────────────────
class InventoryItem(BaseModel):
    item_id: str
    item_name: str
    stock_level: float
    reorder_point: float
    unit_price: float

class InventoryUpdate(BaseModel):
    item_name: Optional[str] = None
    stock_level: Optional[float] = None
    reorder_point: Optional[float] = None
    unit_price: Optional[float] = None

# ─── SALES / ORDER MODELS ───────────────────────────────────────
class Order(BaseModel):
    order_id: str
    timestamp: str
    customer_name: str
    total_amount: float
    status: str     # e.g., "Pending", "Fulfilled"

class OrderStatusUpdate(BaseModel):
    status: str

# ─── CUSTOMER / CRM MODELS ──────────────────────────────────────
class Customer(BaseModel):
    customer_id: str
    contact_person: str
    masked_bank_details: str
    masked_ic_number: str

# ─── EXTRACTION SCHEMA ──────────────────
# This is what the GLM returns after parsing a document
class ExtractionResult(BaseModel):
    intent_category: str  # ORDER_PLACEMENT, STOCK_PROCUREMENT, etc.
    formal_summary: str
    deadline: Optional[str] = None
    items: List[dict]     # List of {"item": "Eggs", "qty": 10}
    pii_detected: bool
    pii_types: List[str]

class MasterMetadata(BaseModel):
    unique_hash: str
    timestamp: str
    detected_language: str
    confidence_score: float
    source_type: str
    source_url: str

class MasterClassification(BaseModel):
    intent_category: str
    urgency_level: int
    formal_summary: str

class MasterEntities(BaseModel):
    client_name: Optional[str] = None
    items: List[dict] = []
    location: Optional[str] = None
    deadline: Optional[str] = None

class MasterSecurity(BaseModel):
    pii_detected: bool
    pii_types: List[str] = []
    requires_manager_approval: bool = False

class MasterExtractionResult(BaseModel):
    metadata: MasterMetadata
    classification: MasterClassification
    extracted_entities: MasterEntities
    security_flags: MasterSecurity


# ─── ENUMS ──────────────────────────────────────────────────────
class MessageSource(str, Enum):
    WHATSAPP = "WHATSAPP"
    TELEGRAM = "TELEGRAM"
    WEB      = "WEB"

class MessageType(str, Enum):
    TEXT     = "TEXT"
    IMAGE    = "IMAGE"
    DOCUMENT = "DOCUMENT"

# ─── INCOMING COMMUNICATION MODEL ───────────────────────────────
class IncomingMessage(BaseModel):
    message_id: str             # Unique ID from WhatsApp/Telegram
    sender_id: str              # Phone number or Telegram User ID
    sender_name: str            # Display name of the user
    source: MessageSource       # Platform identifier
    msg_type: MessageType       # Text, Image, or File
    content: Optional[str] = None      # The text body (e.g., your filled-in template)
    file_path: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)