import pytest
from fastapi.testclient import TestClient
from server.main import app
import server.mcp as mcp

client = TestClient(app)


def test_list_models():
    response = client.post('/mcp', json={'action': 'list_models'})
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    assert isinstance(data['data']['models'], list)


def test_switch_model_and_current():
    response = client.post('/mcp', json={'action': 'switch_model', 'parameters': {'model': 'lightgbm'}})
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
    response = client.post('/mcp', json={'action': 'current_model'})
    assert response.json()['data']['current_model'] == 'LightGBM'


def test_switch_model_invalid():
    response = client.post('/mcp', json={'action': 'switch_model', 'parameters': {'model': 'unknown'}})
    assert response.status_code == 200
    assert response.json()['status'] == 'error'
