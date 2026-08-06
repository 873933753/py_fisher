import pytest

""" 测中间件，app/api/middleware.py 的 request_id 生成与传递 """


# 网关传入应回传；未传入应生成——这是日志串联的基础。
@pytest.mark.asyncio
async def test_generates_request_id_when_missing(client):
    resp = await client.get("/openapi.json")
    assert resp.status_code == 200
    rid = resp.headers.get("X-Request-ID")
    assert rid
    assert len(rid) >= 8


@pytest.mark.asyncio
async def test_echoes_incoming_request_id(client):
    resp = await client.get(
        "/openapi.json",
        headers={"X-Request-ID": "fixed-id-from-gateway"},
    )
    assert resp.headers.get("X-Request-ID") == "fixed-id-from-gateway"
