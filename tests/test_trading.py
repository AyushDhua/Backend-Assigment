from unittest.mock import MagicMock
from backend.trading.utils import TradingExecutionError

def test_market_order_success(client, auth_headers, mocker):
    mock_binance = mocker.patch("backend.trading.orders.get_client")
    mock_client_instance = MagicMock()
    mock_client_instance.futures_create_order.return_value = {
        "orderId": 12345,
        "status": "FILLED",
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "MARKET",
        "origQty": "0.01"
    }
    mock_binance.return_value = mock_client_instance

    res = client.post("/api/v1/trades/order", json={
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "MARKET",
        "quantity": 0.01
    }, headers=auth_headers)

    assert res.status_code == 201
    data = res.get_json()["data"]
    assert data["order_id"] == "12345"

def test_limit_order_requires_price(client, auth_headers):
    res = client.post("/api/v1/trades/order", json={
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "LIMIT",
        "quantity": 0.01
    }, headers=auth_headers)
    assert res.status_code == 400
    json_res = res.get_json()
    assert "price" in str(json_res.get("details", "")).lower() or "price" in str(json_res).lower()

def test_invalid_quantity(client, auth_headers):
    res = client.post("/api/v1/trades/order", json={
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "MARKET",
        "quantity": -0.01
    }, headers=auth_headers)
    assert res.status_code == 400

def test_invalid_symbol(client, auth_headers):
    res = client.post("/api/v1/trades/order", json={
        "symbol": "INVALID",
        "side": "BUY",
        "type": "MARKET",
        "quantity": 0.01
    }, headers=auth_headers)
    assert res.status_code == 400
