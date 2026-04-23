import mysql_service
import sheets_service
from services.rag_service import RAGService
from security import SecurityManager

class PortoDingOrchestrator:
    def __init__(self):
        self.rag = RAGService()
        self.security = SecurityManager()
        # Add other services here...

    async def process_request(self, raw_input, user_role, source_id):
        # 1. THE PRE-PROCESS (The Regex PII Layer you insisted on)
        safe_text = self.security.regex_scrub(raw_input)
        
        # 2. THE REASONING (Calling Z.AI GLM)
        # We ask the AI: "Based on this text, what is the intent and what data is inside?"
        extraction = await self.call_glm(safe_text)
        
        # 3. THE TOOL DISPATCHER (The Agentic Logic)
        intent = extraction['intent']
        
        if intent == "ORDER_PLACEMENT":
            # Call Tool: Update Google Sheets Inventory
            sheets_service.update_stock(extraction['items'], mode="DECREMENT")
            
            # Call Tool: Update MySQL Ticket
            mysql_service.create_ticket(doc_id=source_id, intent="ORDER")
            
            # Call Tool: Send WhatsApp Confirmation
            await self.send_reply(source_id, "Order received! Packing now.")

        elif intent == "INQUIRY":
            # Call Tool: Search Qdrant for past prices/info
            context = self.rag.search_memory_tool(extraction['query'])
            return self.generate_answer(context)

        # 4. FINAL STATE UPDATE
        mysql_service.update_status(source_id, "PROCESSED")