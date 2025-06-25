import pkg_resources
import pytest
import httpx

from server.main import app

@pytest.mark.asyncio
async def test_status_endpoint():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/status")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["status"] == "ok"
    assert payload["version"] == pkg_resources.get_distribution("evoagentx").version
