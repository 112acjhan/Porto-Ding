import json
from openai import OpenAI
from app.core.config import settings
from app.models.schemas import ExtractionResult, Order, InventoryUpdate
from app.services.google_sheets import GoogleSheetsService
from app.services.rag_service import RAGService

class GLMService:
    def __init__(self):
        # 1. Setup the Z.AI Client (OpenAI-Compatible)
        self.client = OpenAI(
            api_key=settings.ZAI_API_KEY,
            base_url="https://api.ilmu.ai/v1"
        )
        self.model = "ilmu-glm-5.1"
        
        # 2. Services for tools
        self.sheets = GoogleSheetsService()
        self.rag = RAGService()

        # 3. Define the Tools Schema (The AI's "Manual")
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "update_inventory_tool",
                    "description": "Updates the Google Sheet inventory when items are sold or added.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item_name": {"type": "string"},
                            "quantity": {"type": "number"},
                            "mode": {"type": "string", "enum": ["ADD", "SUBTRACT"]}
                        },
                        "required": ["item_name", "quantity", "mode"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_rag_tool",
                    "description": "Searches the SME memory for past orders, prices, or client history.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search term or question."}
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    # ─── MAIN REASONING LOGIC ──────────────────────────────────────
    async def process_and_extract(self, user_input: str, client_id: str, user_role: str):
        """Now accepts client_id and user_role to secure the RAG search."""
        
        messages = [
            {"role": "system", "content": "You are the Porto-Ding Orchestrator. Use tools to find info or update sheets."},
            {"role": "user", "content": user_input}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            messages.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                if function_name == "search_rag_tool":
                    # 🔥 INJECTION: We pass the client_id and role from the system, NOT from the AI
                    result = await self.rag.search_memory_tool(
                        query=args['query'], 
                        client_id=client_id, 
                        user_role=user_role
                    )
                
                elif function_name == "update_inventory_tool":
                    result = self.update_inventory_tool(**args)

                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": result,
                })

            # Final call to get the AI to summarize the RAG findings
            final_res = self.client.chat.completions.create(model=self.model, messages=messages)
            return final_res.choices[0].message.content

        return response_message.content


    # ─── TOOL IMPLEMENTATIONS ──────────────────────────────────────
    def update_inventory_tool(self, item_name: str, quantity: float, mode: str):
        """Bridge between AI and GoogleSheetsService."""
        print(f"🚀 Executing Sheet Update: {mode} {quantity} {item_name}")
        
        # Logic: Find item_id by name
        records = self.sheets.get_all_inventory()
        for row in records:
            if row['item_name'].lower() == item_name.lower():
                item_id = row['item_id']
                current_stock = float(row['stock_level'])
                
                # Calculate new stock
                new_stock = current_stock + quantity if mode == "ADD" else current_stock - quantity
                
                self.sheets.update_inventory_row(
                    item_id=item_id, 
                    updates=InventoryUpdate(stock_level=new_stock)
                )
                return f"SUCCESS: {item_name} stock is now {new_stock}."
        
        return f"ERROR: Item '{item_name}' not found in inventory."
