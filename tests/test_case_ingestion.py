import sys
import os
import uuid
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("services/case-integration-service"))
from app.main import app

client = TestClient(app)

def test_ingest_case_and_idempotency():
    tenant_id = str(uuid.uuid4())
    hospital_id = str(uuid.uuid4())
    case_num = f"CS-{uuid.uuid4().hex[:6]}"
    idem_key = f"idem-{uuid.uuid4().hex[:8]}"
    corr_id = f"corr-{uuid.uuid4().hex[:8]}"

    payload = {
        "case_number": case_num,
        "servicenow_sys_id": "sn-sys-123456",
        "tenant_id": tenant_id,
        "hospital_id": hospital_id,
        "service_code": "CARD-OPD",
        "description": "Automated integration test case"
    }
    headers = {
        "Idempotency-Key": idem_key,
        "X-Correlation-ID": corr_id
    }

    # 1. Successful creation
    res1 = client.post("/api/v1/cases", json=payload, headers=headers)
    assert res1.status_code == 201
    data1 = res1.json()
    assert data1["case_number"] == case_num
    assert data1["status"] == "ACCEPTED"
    assert data1["correlation_id"] == corr_id

    # 2. Idempotent replay returns the exact cached response
    res2 = client.post("/api/v1/cases", json=payload, headers=headers)
    assert res2.status_code == 201
    assert res2.json() == data1

    # 3. Conflict on reused idempotency key with modified payload
    modified_payload = dict(payload, service_code="NEURO-OPD")
    res3 = client.post("/api/v1/cases", json=modified_payload, headers=headers)
    assert res3.status_code == 409
