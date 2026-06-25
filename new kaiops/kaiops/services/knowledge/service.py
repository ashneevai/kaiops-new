from services.knowledge.repository import KnowledgeDocumentRepository


class KnowledgeDocumentService:
    def __init__(self, repository: KnowledgeDocumentRepository):
        self.repository = repository

    def list(self, tenant_id: str):
        return self.repository.list(tenant_id)
