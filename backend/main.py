from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import gspread
from google.oauth2.service_account import Credentials

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Google Sheets Setup ────────────────────────────────────────────────────────
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "semiotic-vial-479900-f1-fd82833f6af5.json",
    scopes=scope
)

client = gspread.authorize(creds)
spreadsheet     = client.open("Operational Ledger")
inventory_sheet = spreadsheet.worksheet("Inventory")
orders_sheet    = spreadsheet.worksheet("Sales / Orders")
customers_sheet = spreadsheet.worksheet("Customer")


# ── Pydantic Models ────────────────────────────────────────────────────────────
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

class Order(BaseModel):
    order_id: str
    timestamp: str
    customer_name: str
    total_amount: float
    status: str

class OrderStatusUpdate(BaseModel):
    status: str

class Customer(BaseModel):
    customer_id: str
    contact_person: str
    masked_bank_details: str
    masked_ic_number: str


# ── Health ─────────────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "sheet": "Operational Ledger"}


# ── Inventory ──────────────────────────────────────────────────────────────────
@app.get("/api/inventory")
def get_inventory():
    try:
        return inventory_sheet.get_all_records()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/inventory", status_code=201)
def add_inventory(item: InventoryItem):
    try:
        records = inventory_sheet.get_all_records()
        if any(str(r.get("item_id")) == str(item.item_id) for r in records):
            raise HTTPException(status_code=409, detail=f"item_id '{item.item_id}' already exists")
        inventory_sheet.append_row([
            item.item_id, item.item_name,
            item.stock_level, item.reorder_point, item.unit_price
        ])
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/inventory/{item_id}")
def update_inventory(item_id: str, updates: InventoryUpdate):
    try:
        records = inventory_sheet.get_all_records()
        for i, row in enumerate(records):
            if str(row.get("item_id")) == str(item_id):
                sheet_row = i + 2
                inventory_sheet.update_cell(sheet_row, 2, updates.item_name      if updates.item_name      is not None else row["item_name"])
                inventory_sheet.update_cell(sheet_row, 3, updates.stock_level    if updates.stock_level    is not None else row["stock_level"])
                inventory_sheet.update_cell(sheet_row, 4, updates.reorder_point  if updates.reorder_point  is not None else row["reorder_point"])
                inventory_sheet.update_cell(sheet_row, 5, updates.unit_price     if updates.unit_price     is not None else row["unit_price"])
                return {"success": True}
        raise HTTPException(status_code=404, detail=f"item_id '{item_id}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/inventory/{item_id}")
def delete_inventory(item_id: str):
    try:
        records = inventory_sheet.get_all_records()
        for i, row in enumerate(records):
            if str(row.get("item_id")) == str(item_id):
                inventory_sheet.delete_rows(i + 2)
                return {"success": True}
        raise HTTPException(status_code=404, detail=f"item_id '{item_id}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Orders ─────────────────────────────────────────────────────────────────────
@app.get("/api/orders")
def get_orders():
    try:
        return orders_sheet.get_all_records()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/orders", status_code=201)
def add_order(order: Order):
    try:
        records = orders_sheet.get_all_records()
        if any(str(r.get("order_id")) == str(order.order_id) for r in records):
            raise HTTPException(status_code=409, detail=f"order_id '{order.order_id}' already exists")
        orders_sheet.append_row([
            order.order_id, order.timestamp,
            order.customer_name, order.total_amount, order.status
        ])
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/orders/{order_id}/status")
def update_order_status(order_id: str, body: OrderStatusUpdate):
    try:
        records = orders_sheet.get_all_records()
        for i, row in enumerate(records):
            if str(row.get("order_id")) == str(order_id):
                orders_sheet.update_cell(i + 2, 5, body.status)
                return {"success": True}
        raise HTTPException(status_code=404, detail=f"order_id '{order_id}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/orders/{order_id}")
def delete_order(order_id: str):
    try:
        records = orders_sheet.get_all_records()
        for i, row in enumerate(records):
            if str(row.get("order_id")) == str(order_id):
                orders_sheet.delete_rows(i + 2)
                return {"success": True}
        raise HTTPException(status_code=404, detail=f"order_id '{order_id}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Customers ──────────────────────────────────────────────────────────────────
@app.get("/api/customers")
def get_customers():
    try:
        return customers_sheet.get_all_records()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/customers", status_code=201)
def add_customer(customer: Customer):
    try:
        records = customers_sheet.get_all_records()
        if any(str(r.get("customer_id")) == str(customer.customer_id) for r in records):
            raise HTTPException(status_code=409, detail=f"customer_id '{customer.customer_id}' already exists")
        customers_sheet.append_row([
            customer.customer_id, customer.contact_person,
            customer.masked_bank_details, customer.masked_ic_number
        ])
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/customers/{customer_id}")
def delete_customer(customer_id: str):
    try:
        records = customers_sheet.get_all_records()
        for i, row in enumerate(records):
            if str(row.get("customer_id")) == str(customer_id):
                customers_sheet.delete_rows(i + 2)
                return {"success": True}
        raise HTTPException(status_code=404, detail=f"customer_id '{customer_id}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)