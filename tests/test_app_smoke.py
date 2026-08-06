import pytest


@pytest.mark.asyncio
async def test_openapi_available_in_dev(client):
    """dev 环境应暴露 OpenAPI（Step 2：prod 才关闭）。"""
    resp = await client.get("/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    assert "openapi" in data
    assert "paths" in data


@pytest.mark.asyncio
async def test_docs_available_in_dev(client):
    resp = await client.get("/docs")
    assert resp.status_code == 200
