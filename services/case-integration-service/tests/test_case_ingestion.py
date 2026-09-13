import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.database import SessionLocal

client = TestClient(app)

@pytest.fixture
def valid_hierarchy_ids():
    db = SessionLocal()
    try:
        # Retrieve an existing hospital and its associated hospital_group from seed data
        row = db.execute(
            text('SELECT id, hospital_group_id FROM hospital LIMIT 1')
        ).fetchone()
        if not row:
            pytest.fail('No hospital records found in database. Ensure app.seed has run.')
        return {'hospital_id': row[0], 'tenant_id': row[1]}
    finally:
        db.close()

def test_ingest_case_and_idempotency(valid_hierarchy_ids):
    tenant_id = valid_hierarchy_ids['tenant_id']
    hospital_id = valid_hierarchy_ids['hospital_id']
    case_num = f'CS-{uuid.uuid4().hex[:6]}'
    idem_key = f'idem-{uuid.uuid4().hex[:8]}'
    corr_id = f'corr-{uuid.uuid4().hex[:8]}'

    payload = {
        'case_number': case_num,
        'servicenow_sys_id': 'sn-sys-123456',
        'tenant_id': tenant_id,
        'hospital_id': hospital_id,
        'service_code': 'CARD-OPD',
        'description': 'Automated integration test case'
    }
    headers = {
        'Idempotency-Key': idem_key,
        'X-Correlation-ID': corr_id
    }

    # 1. Successful creation
    res1 = client.post('/api/v1/cases', json=payload, headers=headers)
    assert res1.status_code == 201
    data1 = res1.json()
    assert data1['case_number'] == case_num
    assert data1['status'] == 'ACCEPTED'
    assert data1['correlation_id'] == corr_id

    # 2. Idempotent replay returns the exact cached response
    res2 = client.post('/api/v1/cases', json=payload, headers=headers)
    assert res2.status_code == 201
    assert res2.json() == data1

    # 3. Conflict on reused idempotency key with modified payload
    modified_payload = dict(payload, service_code='NEURO-OPD')
    res3 = client.post('/api/v1/cases', json=modified_payload, headers=headers)
    assert res3.status_code == 409
