import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import inventory, orders, customers
from app.api import whatsapp, telegram

app = FastAPI(title="SME Ops Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(telegram.router)
app.include_router(whatsapp.router)
app.include_router(inventory.router)
app.include_router(orders.router)
app.include_router(customers.router)

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Server is running and healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)