from fastapi import APIRouter, HTTPException
from app.models.schemas import InventoryItem, InventoryUpdate
from app.services.google_sheets import GoogleSheetsService

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])
service = GoogleSheetsService()

@router.get("/")
async def list_inventory():
    return service.get_all_inventory()

@router.post("/", status_code=201)
async def create_item(item: InventoryItem):
    # Check for duplicates before adding
    records = service.get_all_inventory()
    if any(str(r.get("item_id")) == str(item.item_id) for r in records):
        raise HTTPException(status_code=409, detail="Item ID already exists")
    service.add_inventory_row(item)
    return {"success": True}

@router.put("/{item_id}")
async def update_item(item_id: str, updates: InventoryUpdate):
    success = service.update_inventory_row(item_id, updates)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"success": True}

@router.delete("/{item_id}")
async def remove_item(item_id: str):
    success = service.delete_inventory_row(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"success": True}