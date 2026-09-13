from fastapi.testclient import TestClient
import sys
import os

# Add service directory to path for test runner
sys.path.insert(0, os.path.abspath("services/master-data-service"))
from app.main import app

client = TestClient(app)

def test_health_check_returns_200():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "master-data-service"