from fastapi import APIRouter

# 创建一个web路由器 - 模块化拆分路由再挂到主app，web_router 统一管理 web/ 下所有路由
# prefix - 设置前缀 /web，所有路由都会以 /web 开头
web_router = APIRouter(prefix="/web")


# 导入book路由
from app.web import book
from app.web import product
from app.web import test_html

# 导入auth路由
from app.web import auth

# 导入gift路由
from app.web.gift import gift_router

# 将gift路由挂到web_router
web_router.include_router(gift_router)

# 导入wish路由
from app.web.wish import wish_router

# 将wish路由挂到web_router
web_router.include_router(wish_router)

# 导入index路由
from app.web import index

# 导入drift路由
from app.web.drift import drift_router

# 将drift路由挂到web_router
web_router.include_router(drift_router)
