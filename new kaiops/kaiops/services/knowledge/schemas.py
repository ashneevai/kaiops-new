from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class KnowledgeDocumentResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeIndexRequest(BaseModel):
    document_id: str


class KnowledgeIndexResponse(BaseModel):
    document_id: str
    chunks_indexed: int
