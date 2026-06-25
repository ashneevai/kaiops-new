from sqlalchemy.orm import Session

from app.db import models
from app.platform.embeddings import chunk_text, cosine_similarity, embedding_client


class KnowledgeRAGService:
    def __init__(self, db: Session):
        self.db = db

    async def index_document(self, tenant_id: str, document_id: str) -> dict:
        document = (
            self.db.query(models.KnowledgeDocument)
            .filter(
                models.KnowledgeDocument.tenant_id == tenant_id,
                models.KnowledgeDocument.id == document_id,
            )
            .first()
        )
        if not document:
            raise ValueError("Knowledge document not found")

        chunks = chunk_text(document.content)
        self.db.query(models.KnowledgeEmbedding).filter(
            models.KnowledgeEmbedding.document_id == document.id
        ).delete()

        for idx, chunk in enumerate(chunks):
            embedding = await embedding_client.embed(chunk)
            row = models.KnowledgeEmbedding(
                tenant_id=document.tenant_id,
                document_id=document.id,
                chunk_index=idx,
                content=chunk,
                embedding=embedding,
            )
            self.db.add(row)

        document.embedding_ref = "indexed"
        self.db.add(document)
        self.db.commit()
        return {"document_id": str(document.id), "chunks_indexed": len(chunks)}

    async def retrieve(self, tenant_id: str, query: str, limit: int = 5) -> list[dict]:
        query_embedding = await embedding_client.embed(query)

        docs = (
            self.db.query(models.KnowledgeDocument)
            .filter(models.KnowledgeDocument.tenant_id == tenant_id)
            .order_by(models.KnowledgeDocument.updated_at.desc())
            .limit(limit * 4)
            .all()
        )

        doc_ids = [doc.id for doc in docs]
        embeddings = (
            self.db.query(models.KnowledgeEmbedding)
            .filter(models.KnowledgeEmbedding.tenant_id == tenant_id)
            .filter(models.KnowledgeEmbedding.document_id.in_(doc_ids) if doc_ids else False)
            .all()
        )

        chunk_best_score: dict[str, tuple[float, str]] = {}
        for row in embeddings:
            semantic = cosine_similarity(query_embedding, row.embedding)
            lexical = self._lexical_score(query, row.content)
            score = (semantic * 0.8) + (lexical * 0.2)
            doc_key = str(row.document_id)
            existing = chunk_best_score.get(doc_key)
            if existing is None or score > existing[0]:
                chunk_best_score[doc_key] = (score, row.content)

        ranked = []
        for doc in docs:
            best_score, best_chunk = chunk_best_score.get(str(doc.id), (0.0, doc.content[:300]))
            ranked.append(
                {
                    "id": str(doc.id),
                    "title": doc.title,
                    "source": doc.source,
                    "source_ref": doc.source_ref,
                    "snippet": best_chunk[:300],
                    "score": round(best_score, 4),
                    "query": query,
                }
            )

        ranked.sort(key=lambda item: item["score"], reverse=True)
        return ranked[:limit]

    @staticmethod
    def _lexical_score(query: str, content: str) -> float:
        query_terms = {term for term in query.lower().split() if term}
        if not query_terms:
            return 0.0
        content_terms = set(content.lower().split())
        overlap = len(query_terms.intersection(content_terms))
        return overlap / len(query_terms)
