import pytest
from httpx import ASGITransport, AsyncClient

from quantforge.api.app import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.mark.asyncio
async def test_health(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_create_session_returns_id_and_ws_url(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/sessions", json={
            "symbols": ["AAPL"],
            "start": "2024-01-01",
            "end": "2024-01-10",
            "capital": 10000,
            "data_adapter": "synthetic",
        })
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert data["ws_url"].startswith("/sessions/")


@pytest.mark.asyncio
async def test_get_session(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create = await client.post("/sessions", json={
            "symbols": ["AAPL"], "start": "2024-01-01", "end": "2024-01-10",
            "capital": 10000, "data_adapter": "synthetic",
        })
        sid = create.json()["session_id"]
        resp = await client.get(f"/sessions/{sid}")
    assert resp.status_code == 200
    assert resp.json()["session_id"] == sid


@pytest.mark.asyncio
async def test_get_nonexistent_session_404(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/sessions/does-not-exist")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_session(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create = await client.post("/sessions", json={
            "symbols": ["AAPL"], "start": "2024-01-01", "end": "2024-01-10",
            "capital": 10000, "data_adapter": "synthetic",
        })
        sid = create.json()["session_id"]
        resp = await client.delete(f"/sessions/{sid}")
    assert resp.status_code == 200
    assert resp.json()["deleted"] == sid


@pytest.mark.asyncio
async def test_portfolio_endpoint(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create = await client.post("/sessions", json={
            "symbols": ["AAPL"], "start": "2024-01-01", "end": "2024-01-10",
            "capital": 10000, "data_adapter": "synthetic",
        })
        sid = create.json()["session_id"]
        resp = await client.get(f"/sessions/{sid}/portfolio")
    assert resp.status_code == 200
    assert "equity" in resp.json()
