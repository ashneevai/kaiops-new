from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.dependencies import require_tenant
from app.db.session import get_db
from services.knowledge.rag import KnowledgeRAGService
from services.knowledge.repository import KnowledgeDocumentRepository
from services.knowledge.schemas import (
    KnowledgeDocumentResponse,
    KnowledgeIndexRequest,
    KnowledgeIndexResponse,
)
from services.knowledge.service import KnowledgeDocumentService

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("", response_model=list[KnowledgeDocumentResponse], summary="Knowledge management")
def list_items(tenant_id: str = Depends(require_tenant), db: Session = Depends(get_db)):
    service = KnowledgeDocumentService(KnowledgeDocumentRepository(db))
    return service.list(tenant_id)


@router.get("/retrieve", summary="Semantic retrieval with source attribution")
async def retrieve(
    q: str = Query(..., min_length=3),
    limit: int = Query(5, ge=1, le=20),
    tenant_id: str = Depends(require_tenant),
    db: Session = Depends(get_db),
):
    rag = KnowledgeRAGService(db)
    return {"results": await rag.retrieve(tenant_id=tenant_id, query=q, limit=limit)}


@router.post("/index", response_model=KnowledgeIndexResponse, summary="Index knowledge document")
async def index_document(
    request: KnowledgeIndexRequest,
    tenant_id: str = Depends(require_tenant),
    db: Session = Depends(get_db),
):
    rag = KnowledgeRAGService(db)
    try:
        result = await rag.index_document(tenant_id=tenant_id, document_id=request.document_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return KnowledgeIndexResponse(**result)
