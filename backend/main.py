from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import inventory, orders, customers

app = FastAPI(title="SME Ops Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(inventory.router)
app.include_router(orders.router)
app.include_router(customers.router)

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Server is running and healthy"}