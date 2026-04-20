# backend/app/services/vector_db.py
import random
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http import models


class VectorDBService:
    def __init__(self, path="http://localhost:6333"):
        self.client = QdrantClient(path)
        self.collection_name = "knowledge_base"
        self.ensure_collection(self.collection_name)


    def ensure_collection(self, collection_name: str):
        collections = self.client.get_collections().collections
        exists = any(c.name == collection_name for c in collections)

        if not exists:
            self.create_sme_orchestrator_collection(collection_name=collection_name)
            print(f"Collection '{collection_name}' created.")
    

    def create_sme_orchestrator_collection(self, collection_name: str):
        self.client.create_collection(
            collection_name=collection_name,

            # 1. Hybrid Search Setup
            vectors_config={
                "dense": models.VectorParams(
                    size=1536,
                    distance=models.Distance.COSINE,
                    on_disk=True
                )
            },
            sparse_vectors_config={
                "text_sparse": models.SparseVectorParams(
                    index=models.SparseIndexParams(on_disk=True)
                )
            },
            # 2. Performance Tuning
            hnsw_config=models.HnswConfigDiff(
                m=16,
                ef_construct=100,
                on_disk=True
            ),
            on_disk_payload=True
        )

        # 3. Create Payload Indexes
        self.client.create_payload_index(
            collection_name=collection_name,
            field_name="client",
            field_schema=models.KeywordIndexParams(
                type="keyword",
                is_tenant=True 
            )
        )

        # Fast filtering for status and intent
        for field in ["status", "intent", "doc_id"]:
            self.client.create_payload_index(
                collection_name, 
                field, 
                models.PayloadSchemaType.KEYWORD
            )

        # Timestamp for sorting
        self.client.create_payload_index(
            collection_name, 
            "timestamp", 
            models.PayloadSchemaType.INTEGER
        )

        # Full-text search for the OCR extracted text
        self.client.create_payload_index(
            collection_name, 
            "text_to_search", 
            models.TextIndexParams(
                type="text",
                tokenizer=models.TokenizerType.WORD,
                lowercase=True
            )
        )
        
        print(f"SME Collection '{collection_name}' initialized.")


    def upsert_vectors(self, dense_vector: list, sparse_indices: list, sparse_values: list, qdrant_id: str, payload: dict):
        
        try:
            uuid.UUID(str(qdrant_id)) # Validate if the provided ID is already a valid UUID
            point_id = qdrant_id
        except ValueError:
            # Fallback: create a UUID based the custom hash string
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, qdrant_id))
        
        
        point = [
            models.PointStruct(
                id=point_id, # Document unique_hash
                vector={
                    "dense": dense_vector,
                    "text_sparse": models.SparseVector(
                        indices=sparse_indices,
                        values=sparse_values
                    )
                },
                payload=payload
            )
        ]
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=point
        )


    def search_vectors(self, query_dense: list, query_sparse_indices: list, query_sparse_values: list, client_id: str, top_k: int = 5):
        # Hybrid Search using query point
        return self.client.query_points(
            collection_name=self.collection_name,
            prefetch=[
                # Attempt 1: Dense Semantic Search
                models.Prefetch(
                    query=query_dense,
                    using="dense",
                    limit=top_k
                ),
                # Attempt 2: Sparse Keyword Search
                models.Prefetch(
                    query=models.SparseVector(
                        indices=query_sparse_indices,
                        values=query_sparse_values
                    ),
                    using="text_sparse",
                    limit=top_k
                ),
            ],
            
            # Logical Filter: Only search data belonging to this specific client
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="client",
                        match=models.MatchValue(value=client_id)
                    )
                ]
            ),

            # RRF (Reciprocal Rank Fusion): Merges the dense and sparse results
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=top_k
        )


if __name__ == "__main__":
    vector_db_service = VectorDBService()
    
    # Testing the upsert functionality with dummy data
    # 1. Create Dummy Data
    dummy_collection = "sme_vault_test"
    dummy_id = "test_doc_001"
    dummy_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, "test_doc_001")) 
    
    # Generate a random 1024-dimension list for the dense vector
    dummy_dense = [random.uniform(-1, 1) for _ in range(1024)]
    
    # Generate dummy sparse data
    dummy_indices = [10, 45, 102]
    dummy_values = [0.8, 0.4, 0.9]
    
    # Match your JSON schema for the payload
    dummy_payload = {
        "doc_id": "DOC_TEST_001",
        "client": "Cafe Ali",
        "text_to_search": "Urgent delivery of 10 boxes of eggs.",
        "intent": "ORDER_PLACEMENT",
        "status": "Archived",
        "timestamp": 1776434400 
    }

    try:
        vector_db_service.upsert_vectors(
            dense_vector=dummy_dense,
            sparse_indices=dummy_indices,
            sparse_values=dummy_values,
            qdrant_id=dummy_id,
            payload=dummy_payload
        )
        print("Dummy data upserted successfully.")
    except Exception as e:
        print(f"Error upserting dummy data: {e}")