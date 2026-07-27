from fastapi import APIRouter, Depends
from app.schemas.response import ApiResponse
from typing import Any, Annotated
from app.libs.auth import get_current_user
from app.models.gift import Gift
from pydantic import BaseModel, Field
from app.view_models.gift import MyGiftData, MyGifts

from app.deps import CurrentSession, CurrentUser, get_own_active_gift_from_path
from app.services.gift import redraw_gift, add_gift_to_list_service

# 子路由：/gift 前缀 + 全局鉴权
gift_router = APIRouter(
    prefix="/gift",
    # 可以在该 router 下所有接口添加依赖，如：Depends(get_current_user)
    # 路由级：整组接口都要登录
    dependencies=[Depends(get_current_user)],  # 该 router 下所有接口都要登录
)


# 添加商品到赠送清单请求体
class SaveGiftBody(BaseModel):
    isbn: str = Field(..., min_length=1, max_length=50)


# 将商品添加到赠送清单
@gift_router.post("/product", response_model=ApiResponse[Any])
def save_to_gifts(
    body: SaveGiftBody, current_user: CurrentUser, session: CurrentSession
):
    add_gift_to_list_service(session, current_user, body.isbn)
    return ApiResponse(data={}, message="添加成功")


# 获取当前用户的赠送清单
@gift_router.get("/myList", response_model=ApiResponse[MyGiftData])
def get_gifts(session: CurrentSession, current_user: CurrentUser):
    gifts = Gift.my_gifts(session, current_user.id)
    # 获取每个礼物的isbn列表
    isbn_list = [gift.isbn for gift in gifts]
    # 获取每个礼物的想要人数
    wish_counts_list = Gift.get_wish_count(session, isbn_list)
    wish_count = {item["isbn"]: item["count"] for item in wish_counts_list}
    return ApiResponse(data=MyGifts(gifts, wish_count).to_schema())


# 撤销礼物
@gift_router.post("/request/redraw/{gift_id}", response_model=ApiResponse[dict])
def request_redraw(
    gift: Annotated[Gift, Depends(get_own_active_gift_from_path)],
    session: CurrentSession,
    current_user: CurrentUser,
):
    redraw_gift(session, gift, current_user)
    return ApiResponse(data={}, message="撤销成功")
