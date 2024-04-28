import json
from src.main import app


class TestHealth():

    def test_health(self):
        with app.test_client() as test_client:
            response = test_client.get('/gestor-productos-servicios/health/ping')
            response_json = json.loads(response.data)

            assert response.status_code == 200
            assert 'result' in response_json
            assert response_json['result'] == 'pong'
