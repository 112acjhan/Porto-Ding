import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import inventory, orders, customers, tickets, intake, whatsapp, auth
from app.api.tickets import database_engine, metadata

app = FastAPI(title="SME Ops Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth.router)
app.include_router(intake.router)
app.include_router(whatsapp.router)
app.include_router(inventory.router)
app.include_router(orders.router)
app.include_router(customers.router)
app.include_router(tickets.router)

@app.on_event("startup")
async def startup() -> None:
    async with database_engine.begin() as connection:
        # metadata now contains documents, audit_logs, and external_entities
        await connection.run_sync(metadata.create_all)

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Server is running and healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)