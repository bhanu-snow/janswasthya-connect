from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class InboundCaseCreate(BaseModel):
    case_number: str = Field(..., description="ServiceNow Case Number, e.g. CS0001001")
    servicenow_sys_id: Optional[str] = Field(None, description="ServiceNow record sys_id")
    tenant_id: str = Field(..., description="Hospital Group ID")
    hospital_id: str = Field(..., description="Hospital ID")
    service_code: str = Field(..., description="Master Data Service Code, e.g. CARD-OPD")
    description: Optional[str] = None

class InboundCaseResponse(BaseModel):
    case_reference_id: str
    case_number: str
    status: str
    correlation_id: str
    message: str