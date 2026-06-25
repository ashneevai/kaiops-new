import pytest

from services.knowledge.rag import KnowledgeRAGService


class FakeEmbeddingClient:
    def __init__(self, vector):
        self.vector = vector

    async def embed(self, text: str):
        return self.vector


class FakeQuery:
    def __init__(self, rows):
        self.rows = rows

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def all(self):
        return self.rows

    def first(self):
        return self.rows[0] if self.rows else None

    def delete(self):
        return 0


class FakeSession:
    def __init__(self, documents, embeddings):
        self.documents = documents
        self.embeddings = embeddings
        self.added = []
        self.committed = False

    def query(self, model):
        if model.__name__ == "KnowledgeDocument":
            return FakeQuery(self.documents)
        if model.__name__ == "KnowledgeEmbedding":
            return FakeQuery(self.embeddings)
        return FakeQuery([])

    def add(self, row):
        self.added.append(row)

    def commit(self):
        self.committed = True


@pytest.mark.asyncio
async def test_retrieve_ranks_by_similarity(monkeypatch):
    class Doc:
        def __init__(self, doc_id, title, content):
            self.id = doc_id
            self.tenant_id = "tenant-1"
            self.title = title
            self.source = "confluence"
            self.source_ref = "ref"
            self.content = content

    class Embedding:
        def __init__(self, doc_id, content, embedding):
            self.document_id = doc_id
            self.tenant_id = "tenant-1"
            self.content = content
            self.embedding = embedding

    docs = [
        Doc("doc-1", "Runbook A", "db saturation and connection pool exhaustion"),
        Doc("doc-2", "Runbook B", "cache tuning for read traffic"),
    ]
    embeddings = [
        Embedding("doc-1", "db saturation and connection pool exhaustion", [1.0, 0.0]),
        Embedding("doc-2", "cache tuning for read traffic", [0.0, 1.0]),
    ]
    session = FakeSession(docs, embeddings)
    service = KnowledgeRAGService(session)
    monkeypatch.setattr("services.knowledge.rag.embedding_client", FakeEmbeddingClient([1.0, 0.0]))

    results = await service.retrieve("tenant-1", "database saturation", limit=1)
    assert results[0]["id"] == "doc-1"
    assert results[0]["score"] > 0
