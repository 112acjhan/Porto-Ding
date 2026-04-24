import torch
import time
from openai import OpenAI
from app.core.config import settings
from vector_db import VectorDBService
from fastembed import SparseTextEmbedding
from sentence_transformers import SentenceTransformer


class RAGService:
    def __init__(self):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.vector_db = VectorDBService()
        self.client = OpenAI(
            api_key=settings.ZAI_API_KEY,
            base_url="https://api.ilmu.ai/v1"
        )
        self.model = "ilmu-glm-5.1"
        self.dense_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.sparse_model = SparseTextEmbedding(
            model_name="prithivida/Splade_PP_en_v1",
        )
    

    async def search_memory_tool(self, query: str, client_id: str, user_role: str):
        # 1. Turn query text into a vector
        dense_vec = self.dense_model.encode([query])[0].tolist()

        # 2. Get sparse representation
        sparse_output = next(self.sparse_model.query_embed(query))
        sparse_indices = sparse_output.indices
        sparse_values = sparse_output.values

        # 3. Get relevant memories from vector db
        raw_results = self.vector_db.search_vectors(
            query_dense=dense_vec,
            query_sparse_indices=sparse_indices,
            query_sparse_values=sparse_values,
            client_id=client_id,
            user_role=user_role
        )

        # 4. Clean the data for the GLM
        context = []
        for point in raw_results.points:
            source = point.payload.get('source_url', 'Unknown')
            text = point.payload.get('text_to_search')
            context.append(f"Source Link: {source}\nContent: {text}")

        return "\n---\n".join(context) if context else "No relevant memory found."
    

    async def ingest_document(self, master_json: dict):        
        # Turn query text into a vector using Z.AI
        search_text = master_json["classification"]["formal_summary"]
        dense_vector = await self.dense_model.encode([search_text])

        # 2. Generate Sparse Vector
        sparse_gen = self.sparse_model.embed([search_text])
        sparse_output = next(sparse_gen)
        
        # 3. Prepare the Payload
        payload = {
            "doc_id": master_json["metadata"]["unique_hash"],
            "text_to_search": search_text,
            "raw_ocr": master_json["metadata"].get("raw_text"),
            "source_url": master_json["metadata"]["source_url"],
            "intent": master_json["classification"]["intent_category"],
            "authorized_roles": "MANAGER" if master_json["security_flags"]["pii_detected"] else "STAFF"
        }

        # 4. Push to Vector DB
        self.vector_db.upsert_vectors(
            dense_vector=dense_vector,
            sparse_indices=sparse_output.indices.tolist(),
            sparse_values=sparse_output.values.tolist(),
            qdrant_id=payload["doc_id"],
            payload=payload
        )
        
        return {"status": "success", "doc_id": payload["doc_id"]}