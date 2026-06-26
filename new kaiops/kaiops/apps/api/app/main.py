import logging

from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.router import api_router
from app.platform.messaging import kafka_publisher
from app.platform.rbac import EXEMPT_PATHS, EXEMPT_PATH_PREFIXES, PERMISSION_RULES, RBACMiddleware
from app.platform.telemetry import setup_observability

logger = logging.getLogger(__name__)

app = FastAPI(title="KaiOps API", version="1.0.0")
app.add_middleware(
    RBACMiddleware,
    permission_rules=PERMISSION_RULES,
    exempt_paths=EXEMPT_PATHS,
    exempt_path_prefixes=EXEMPT_PATH_PREFIXES,
)
app.include_router(api_router, prefix="/api/v1")
setup_observability(app)


@app.on_event("startup")
async def startup_event() -> None:
    try:
        await kafka_publisher.start()
    except Exception:
        if settings.kafka_required:
            raise
        logger.warning("Kafka is unavailable; continuing without event publishing")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    try:
        await kafka_publisher.stop()
    except Exception:
        logger.warning("Kafka shutdown was skipped because producer was unavailable")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
