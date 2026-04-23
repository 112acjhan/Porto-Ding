from services.google_sheets import GoogleSheetsService
from services.rag_service import RAGService
from core.security import SecurityManager
from models.schemas import Order, IncomingMessage

class PortoDingOrchestrator:
    def __init__(self):
        # Initialize the services once
        self.sheets = GoogleSheetsService()
        self.rag = RAGService()
        self.security = SecurityManager()
        # self.mysql = MySQLService() 

    async def process_request(self, message: IncomingMessage):
        # 1. THE PRE-PROCESS (Regex PII Layer)
        safe_text = self.security.mask_value(message.content)
        
        # 2. THE REASONING (Calling Z.AI GLM)
        extraction = await self.call_glm(safe_text)
        
        # 3. THE TOOL DISPATCHER
        intent = extraction.intent_category
        
        if intent == "ORDER_PLACEMENT":
            # --- TOOL 1: Update Google Sheets ---
            # We call the service directly, exactly like the API does!
            new_order = Order(
                order_id=f"ORD-{message.timestamp}",
                timestamp=message.timestamp,
                customer_name=message.sender_name,
                total_amount=extraction.total_amount,
                status="Pending"
            )
            self.sheets.add_order_row(new_order)
            
            # --- TOOL 2: Update MySQL Ticket ---
            # self.mysql.create_ticket(doc_id=message.sender_id, intent="ORDER")
            
            return "Order logged in Google Sheets!"

        elif intent == "INQUIRY":
            # --- TOOL 3: RAG Search ---
            context = self.rag.search_memory_tool(extraction.formal_summary)
            return self.generate_answer(context)

        # 4. FINAL STATE UPDATE
        # self.mysql.update_status(message.sender_id, "PROCESSED")