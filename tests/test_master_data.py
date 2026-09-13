import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("services/master-data-service"))
from app.main import app

client = TestClient(app)

def test_get_hospital_groups():
    response = client.get("/api/v1/hospital-groups")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    codes = [g["code"] for g in data]
    assert "SUNRISE" in codes
    assert "APOLLO" in codes

def test_tenant_isolation_filter():
    # 1. Fetch Sunrise group
    groups = client.get("/api/v1/hospital-groups").json()
    sunrise = next(g for g in groups if g["code"] == "SUNRISE")
    
    # 2. Filter hospitals by Sunrise tenant ID
    response = client.get(f"/api/v1/hospitals?tenant_id={sunrise['id']}")
    assert response.status_code == 200
    hospitals = response.json()
    assert len(hospitals) == 2
    for h in hospitals:
        assert h["hospital_group_id"] == sunrise["id"]
