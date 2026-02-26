from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
import os

class QdrantStorage:
    def __init__(self, collection_name="rag_collection", dim=3072):
        self.collection_name = collection_name
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL", "http://localhost:6333")
        )
        # Create collection if it doesn't exist
        if self.collection_name not in [c.name for c in self.client.get_collections().collections]:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
            )

    def upsert(self, ids, vectors, payloads):
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                {"id": ids[i], "vector": vectors[i], "payload": payloads[i]}
                for i in range(len(ids))
            ]
        )

    def search(self, query_vector, top_k=5):
        # ✅ Use query_points for qdrant-client v1.17
        result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k
        )
        # Convert Qdrant response to simple dict for contexts/sources
        contexts = [p.payload.get("text", "") for p in result.points]
        sources = [p.payload.get("source", "") for p in result.points]
        return {"contexts": contexts, "sources": sources}