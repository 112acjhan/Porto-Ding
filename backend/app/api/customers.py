from fastapi import APIRouter, HTTPException
from app.models.schemas import Customer
from app.services.google_sheets import GoogleSheetsService

router = APIRouter(prefix="/api/customers", tags=["Customers"])
service = GoogleSheetsService()

@router.get("/")
async def list_customers():
    try:
        return service.get_all_customers()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", status_code=201)
async def add_customer(customer: Customer):
    try:
        # Check for duplicates
        records = service.get_all_customers()
        if any(str(r.get("customer_id")) == str(customer.customer_id) for r in records):
            raise HTTPException(status_code=409, detail="Customer ID already exists")
            
        # This calls your 'add_customer_row' function
        service.add_customer_row(customer)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{customer_id}")
async def remove_customer(customer_id: str):
    # This calls your 'delete_customer_row' function
    success = service.delete_customer_row(customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"success": "Customer deleted"}