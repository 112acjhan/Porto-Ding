import torch
import time
from vector_db import VectorDBService
from fastembed import SparseTextEmbedding


class RAGService:
    def __init__(self):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.vector_db = VectorDBService()
        self.client = zai_sdk.Client(api_key=settings.ZAI_API_KEY)
        self.sparse_model = SparseTextEmbedding(
            model_name="prithivida/Splade_PP_en_v1",
        )


    async def search_memory_tool(self, query: str, client_id: str):
        # 1. Turn query text into a vector using Z.AI
        dense_vec = await self._get_z_ai_embeddings(query)
        
        # 2. Get sparse representation
        sparse_output = next(self.sparse_model.query_embed(query))
        sparse_indices = sparse_output.indices
        sparse_values = sparse_output.values

        # 3. Get relevant memories from vector db
        raw_results = self.vector_db.search_vectors(
            query_dense=dense_vec,
            query_sparse_indices=sparse_indices,
            query_sparse_values=sparse_values,
            client_id=client_id
        )

        # 4. Clean the data for the GLM
        context = []
        for point in raw_results.points:
            context.append(f"Source: {point.payload.get('doc_id')}\nContent: {point.payload.get('text_to_search')}")

        return "\n---\n".join(context) if context else "No relevant memory found."
    

    async def ingest_document(self, ocr_text: str, metadata: dict):        
        # Turn query text into a vector using Z.AI
        dense_vector = await self._get_z_ai_embeddings(ocr_text)

        # 2. Generate Sparse Vector
        sparse_gen = self.sparse_model.embed([ocr_text])
        sparse_output = next(sparse_gen)
        
        # 3. Prepare the Payload
        payload = {
            **metadata,
            "text_to_search": ocr_text,
            "timestamp": int(metadata.get("timestamp") or time.time()) 
        }

        # 4. Push to Vector DB
        self.vector_db.upsert_vectors(
            dense_vector=dense_vector,
            sparse_indices=sparse_output.indices.tolist(),
            sparse_values=sparse_output.values.tolist(),
            qdrant_id=metadata["doc_id"],
            payload=payload
        )
        
        return {"status": "success", "doc_id": metadata["doc_id"]}