from fastapi import APIRouter, HTTPException
from app.models.schemas import Order, OrderStatusUpdate
from app.services.google_sheets import GoogleSheetsService

router = APIRouter(prefix="/api/orders", tags=["Orders"])
service = GoogleSheetsService()

@router.get("/")
async def list_orders():
    try:
        return service.get_all_orders()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", status_code=201)
async def create_order(order: Order):
    try:
        # Check for duplicates
        records = service.get_all_orders()
        if any(str(r.get("order_id")) == str(order.order_id) for r in records):
            raise HTTPException(status_code=409, detail="Order ID already exists")
        
        service.add_order_row(order)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{order_id}/status")
async def update_status(order_id: str, body: OrderStatusUpdate):
    # This calls your 'update_order_status_row' function
    success = service.update_order_status_row(order_id, body.status)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"success": "Order status updated"}

@router.delete("/{order_id}")
async def remove_order(order_id: str):
    # This calls your 'delete_order_row' function
    success = service.delete_order_row(order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"success": "Order deleted"}