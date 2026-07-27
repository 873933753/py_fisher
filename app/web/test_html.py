from fastapi import Request
from . import web_router
from app.libs.templates import templates  # 或你放 templates 实例的位置


@web_router.get("/test_html")
def test_html(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="test.html",  # templates 目录下的文件名
        context={
            "title": "测试页面",
            "content": "这是一个测试页面",
            "user": {
                "is_vip": True,
            },
            "list": [
                {"name": "苹果"},
                {"name": "香蕉"},
                {"name": "橘子"},
            ],
        },  # 传给模板的变量，没有就传空 dict
    )
