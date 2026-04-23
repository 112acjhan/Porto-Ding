from pydantic import BaseModel
from typing import Optional, List

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