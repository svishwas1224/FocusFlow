import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app import monitor


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_session_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        create_resp = await client.post("/sessions", json={"focus_score": 88.5})
        assert create_resp.status_code == 200
        created = create_resp.json()
        assert created["focus_score"] == 88.5
        assert created["end"] is None

        session_id = created["id"]
        close_resp = await client.put(f"/sessions/{session_id}/close", json={"focus_score": 70.0})
        assert close_resp.status_code == 200
        closed = close_resp.json()
        assert closed["focus_score"] == 70.0
        assert closed["end"] is not None

        list_resp = await client.get("/sessions")
        assert list_resp.status_code == 200
        assert any(item["id"] == session_id for item in list_resp.json())


@pytest.mark.asyncio
async def test_settings_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        get_resp = await client.get("/settings")
        assert get_resp.status_code == 200
        original = get_resp.json()
        assert isinstance(original["blocked_urls"], list)

        update_data = {"blocked_urls": ["example.com", "test.com"], "aggressive_mode": True}
        update_resp = await client.post("/settings", json=update_data)
        assert update_resp.status_code == 200
        updated = update_resp.json()
        assert updated["blocked_urls"] == ["example.com", "test.com"]
        assert updated["aggressive_mode"] is True


def test_monitor_categorization():
    assert monitor.categorize_window("YouTube - distraction") == "distractor"
    assert monitor.categorize_window("Visual Studio Code") == "focus"
    assert monitor.categorize_window("Random name") == "neutral"
