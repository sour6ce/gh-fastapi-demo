from math import isclose

import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_default():
    # The given command send a JSON with an error putting a comma after the last order, thing that
    # Python dicts allow but not json format.
    #
    # This example is builded with dict so it works well
    data = {
        "orders": [
            {"id": 1, "item": "Laptop", "quantity": 1, "price": 999.99, "status": "completed"},
            {"id": 2, "item": "Smartphone", "quantity": 2, "price": 499.95, "status": "pending"},
            {"id": 3, "item": "Headphones", "quantity": 3, "price": 99.90, "status": "completed"},
            {"id": 4, "item": "Mouse", "quantity": 4, "price": 24.99, "status": "canceled"},
        ],
        "criterion": "completed"
    }

    response = client.post("/solution", json=data)
    assert response.status_code == 200
    assert isclose(response.json(), 1299.69)


def test_good1():
    data = {
        "orders": [
            {"id": 1, "item": "Laptop", "quantity": 1, "price": 999.99, "status": "completed"},
            {"id": 2, "item": "Smartphone", "quantity": 2, "price": 499.95, "status": "pending"},
            {"id": 3, "item": "Headphones", "quantity": 3, "price": 99.90, "status": "completed"},
            {"id": 4, "item": "Mouse", "quantity": 4, "price": 24.99, "status": "canceled"},
            {"id": 13, "item": "Cucumber", "quantity": 10, "price": 1.20, "status": "pending"},
            {"id": 21, "item": "Gold Ingot", "quantity": 3, "price": 125.80, "status": "canceled"}
        ],
        "criterion": "pending"
    }

    response = client.post("/solution", json=data)
    assert response.status_code == 200
    assert isclose(response.json(), 1011.90)


def test_good2():
    data = {
        "orders": [
            {"id": 4, "item": "Mouse", "quantity": 4, "price": 24.99, "status": "canceled"},
            {"id": 21, "item": "Gold Ingot", "quantity": 3, "price": 125.80, "status": "canceled"}
        ],
        "criterion": "all"
    }

    response = client.post("/solution", json=data)
    assert response.status_code == 200
    assert isclose(response.json(), 477.36)


def test_no_match():
    data = {
        "orders": [
            {"id": 1, "item": "Laptop", "quantity": 1, "price": 999.99, "status": "completed"},
            {"id": 2, "item": "Smartphone", "quantity": 2, "price": 499.95, "status": "completed"},
            {"id": 3, "item": "Headphones", "quantity": 3, "price": 99.90, "status": "completed"},
            {"id": 4, "item": "Mouse", "quantity": 4, "price": 24.99, "status": "completed"},
            {"id": 13, "item": "Cucumber", "quantity": 10, "price": 1.20, "status": "completed"},
            {"id": 21, "item": "Gold Ingot", "quantity": 3, "price": 125.80, "status": "completed"}
        ],
        "criterion": "pending"
    }

    response = client.post("/solution", json=data)
    assert response.status_code == 200
    assert isclose(response.json(), 0.0)


def test_no_orders():
    data = {
        "orders": [],
        "criterion": "pending"
    }

    response = client.post("/solution", json=data)
    assert response.status_code == 200
    assert isclose(response.json(), 0.0)


def test_invalid_json():
    # This is literally the oficial test of the project, with JSON syntax error.
    data = '''{
        "orders": [
            {"id": 1, "item": "Laptop", "quantity": 1, "price": 999.99, "status": "completed"},
            {"id": 2, "item": "Smartphone", "quantity": 2, "price": 499.95, "status": "pending"},
            {"id": 3, "item": "Headphones", "quantity": 3, "price": 99.90, "status": "completed"},
            {"id": 4, "item": "Mouse", "quantity": 4, "price": 24.99, "status": "canceled"},
        ],
        "criterion": "completed"
    }'''

    response = client.post("/solution", data=data)
    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'][0] == 'body'
    assert response.json()['detail'][0]['msg'].startswith('Expecting value:')
    assert response.json()['detail'][0]['type'] == 'value_error.jsondecode'


def test_missing_field():
    data = '''{
        "orders": [
            {"id": 1, "item": "Laptop", "quantity": 1, "price": 999.99, "status": "completed"},
            {"id": 2, "item": "Smartphone", "quantity": 2, "status": "pending"}
        ],
        "criterion": "all"
    }'''

    response = client.post("/solution", data=data)
    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'][0] == 'body'
    assert response.json()['detail'][0]['loc'][3] == 'price'
    assert response.json()['detail'][0]['msg'] \
        == 'field required'
    assert response.json()['detail'][0]['type'] == 'value_error.missing'


@pytest.mark.skip(reason="Disabled due to extra fields allowed")
def test_invalid_field():
    data = '''{
        "orders": [
            {"id": 3, "item": "Headphones", "quantity": 3, "price": 99.90, "status": "completed"},
            {"id": 4, "item": "Mouse", "quantity": 4, "price": 24.99, "status": "canceled", "buyer": "Johnny"},
            {"id": 13, "item": "Cucumber", "quantity": 10, "price": 1.20, "status": "pending"}
        ],
        "criterion": "canceled"
    }'''

    response = client.post("/solution", data=data)
    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'][0] == 'body'
    assert response.json()['detail'][0]['msg'] == 'extra fields not permitted'
    assert response.json()['detail'][0]['type'] == 'value_error.extra'
