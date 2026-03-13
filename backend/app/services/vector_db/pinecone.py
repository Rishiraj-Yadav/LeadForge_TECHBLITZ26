"""Pinecone vector DB for conversation memory."""

from pinecone import Pinecone, ServerlessSpec

from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class PineconeService:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME

    def ensure_index(self, dimension: int = 1536):
        existing = [index["name"] for index in self.pc.list_indexes()]
        if self.index_name not in existing:
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region=settings.PINECONE_ENVIRONMENT),
            )
            logger.info(f"Created Pinecone index: {self.index_name}")

    def upsert_conversation(self, conversation_id: str, embedding: list[float], metadata: dict):
        index = self.pc.Index(self.index_name)
        index.upsert(vectors=[(conversation_id, embedding, metadata)])

    def search_similar(self, embedding: list[float], top_k: int = 5):
        index = self.pc.Index(self.index_name)
        return index.query(vector=embedding, top_k=top_k, include_metadata=True)


def get_vector_store() -> PineconeService:
    return PineconeService()
