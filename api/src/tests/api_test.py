from fastapi.testclient import TestClient

from api import SERVICE_STATUS_PATH
from main import app

# TODO: test remaing enpoints


def test_get_status_api():
    with TestClient(app) as client:
        response = client.get(SERVICE_STATUS_PATH)
    assert response.status_code == 200
    assert response.json() == {"message": "Backend service is available"}
