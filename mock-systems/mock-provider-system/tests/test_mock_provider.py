from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_mock_provider():
    res = client.get('/health')
    assert res.status_code == 200
    assert res.json()['service'] == 'mock-provider-system'

def test_create_and_get_appointment():
    payload = {
        'patient_identifier': 'SYNTH-PAT-001',
        'hospital_id': 'hosp-kanpur-01',
        'department_code': 'CARD-OPD',
        'preferred_slot': '2026-09-15T10:00:00Z',
        'reason': 'Routine checkup'
    }
    res = client.post('/api/v1/appointments', json=payload)
    assert res.status_code == 201
    data = res.json()
    assert 'APPT-' in data['appointment_id']
    assert data['status'] == 'CONFIRMED'

    # Retrieve by ID
    appointment_id = data["appointment_id"]
    get_res = client.get(f"/api/v1/appointments/{appointment_id}")                                                      
    assert get_res.status_code == 200
    assert get_res.json()['appointment_id'] == data['appointment_id']

def test_simulated_fault_modes():
    payload = {
        'patient_identifier': 'SYNTH-PAT-002',
        'hospital_id': 'hosp-kanpur-01',
        'department_code': 'CARD-OPD',
        'preferred_slot': '2026-09-15T11:00:00Z'
    }
    # Test 500 error injection
    res_500 = client.post('/api/v1/appointments', json=payload, headers={'X-Simulate-Mode': '500'})
    assert res_500.status_code == 500

    # Test 409 conflict injection
    res_409 = client.post('/api/v1/appointments', json=payload, headers={'X-Simulate-Mode': '409'})
    assert res_409.status_code == 409
