from fastapi import FastAPI, Cookie, HTTPException
from fastapi.responses import Response
from test import test_router


@test_router.get("/set-cookie")
def set_cookie(response: Response):
    # 设置cookie
    # max_age - 最大年龄，单位：秒
    # path - 路径
    # domain - 域名
    # secure - 是否只通过 HTTPS 访问
    # httponly - 是否只通过 HTTP 访问
    # samesite - 是否只通过同源访问
    # sameparty - 是否只通过同源访问
    # sameorigin - 是否只通过同源访问
    # none - 是否只通过同源访问
    # lax - 是否只通过同源访问
    response.set_cookie(key="test_cookie", value="test_value", max_age=3600)
