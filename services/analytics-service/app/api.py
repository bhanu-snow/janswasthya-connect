from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dependencies import get_analytics_service
from app.services import AnalyticsService


router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


class CaseAnalyticsRequest(BaseModel):
    tenant_id: UUID
    case_reference_id: UUID
    hospital_id: UUID
    service_code: str
    status: str
    case_created_at: datetime
    case_updated_at: datetime


class CaseAnalyticsResponse(BaseModel):
    id: str
    tenant_id: str
    case_reference_id: str
    hospital_id: str
    service_code: str
    status: str
    case_created_at: datetime
    case_updated_at: datetime


@router.post("/cases", response_model=CaseAnalyticsResponse)
def record_case(
    request: CaseAnalyticsRequest,
    service: AnalyticsService = Depends(get_analytics_service),
):
    fact = service.record_case(
        tenant_id=request.tenant_id,
        case_reference_id=request.case_reference_id,
        hospital_id=request.hospital_id,
        service_code=request.service_code,
        status=request.status,
        case_created_at=request.case_created_at,
        case_updated_at=request.case_updated_at,
    )

    

    return CaseAnalyticsResponse(
        id=fact.id,
        tenant_id=fact.tenant_id,
        case_reference_id=fact.case_reference_id,
        hospital_id=fact.hospital_id,
        service_code=fact.service_code,
        status=fact.status,
        case_created_at=fact.case_created_at,
        case_updated_at=fact.case_updated_at,
    )