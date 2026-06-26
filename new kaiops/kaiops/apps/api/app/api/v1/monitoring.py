from fastapi import APIRouter

from app.platform.monitoring import MonitoringOverviewResponse, PrometheusMonitoringClient

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/overview", response_model=MonitoringOverviewResponse, summary="Prometheus monitoring overview")
async def monitoring_overview():
    client = PrometheusMonitoringClient()
    return await client.get_overview()
