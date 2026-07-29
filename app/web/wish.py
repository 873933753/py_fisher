from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.deps import CurrentSession, CurrentUser, get_own_active_wish_from_path
from app.libs.auth import get_current_user
from app.models.wish import Wish
from app.schemas.pagination import Page, PageData, PageSize, paginate
from app.schemas.product import HomeGiftItem
from app.schemas.response import ApiResponse
from app.services.wish import add_wish_to_list_service, redraw_wish
from app.setting import DEFAULT_PAGE_SIZE
from app.view_models.trade import MyTrades

# 子路由：/gift 前缀 + 全局鉴权
wish_router = APIRouter(
    prefix="/wish",
    tags=["wish"],
    # 可以在该 router 下所有接口添加依赖，如：Depends(get_current_user)
    # 路由级：整组接口都要登录
    dependencies=[Depends(get_current_user)],  # 该 router 下所有接口都要登录
)


# 添加商品到心愿清单请求体
class SaveGiftBody(BaseModel):
    isbn: str = Field(..., min_length=1, max_length=50)


# 将商品添加到心愿清单
@wish_router.post("/product", response_model=ApiResponse[Any])
def save_to_gifts(
    body: SaveGiftBody, current_user: CurrentUser, session: CurrentSession
):
    add_wish_to_list_service(session, current_user, body.isbn)
    return ApiResponse(data={}, message="添加成功")


# 获取当前用户的心愿清单
@wish_router.get("/myList", response_model=ApiResponse[PageData[HomeGiftItem]])
def get_wishes(
    session: CurrentSession,
    current_user: CurrentUser,
    page: Page = 1,
    size: PageSize = DEFAULT_PAGE_SIZE,
):
    # 分页查询心愿清单
    # stmt: 查询心愿清单的语句
    stmt = Wish.my_wishes_query(current_user.id)  # 方案 A
    wishes, total = paginate(session, stmt, page, size)

    # wishes = Wish.my_wishes_query(current_user.id)
    isbn_list = [wish.isbn for wish in wishes]
    wish_counts_list = Wish.get_wish_count(session, isbn_list)
    wish_count = {item["isbn"]: item["count"] for item in wish_counts_list}
    my_trades = MyTrades(wishes, wish_count)
    return ApiResponse(
        data=PageData.build(my_trades.items, total, page, size),
        message="获取心愿清单成功",
    )


# 撤销心愿
@wish_router.post("/request/redraw/{wish_id}", response_model=ApiResponse[dict])
def request_redraw(
    wish: Annotated[Wish, Depends(get_own_active_wish_from_path)],
    session: CurrentSession,
):
    redraw_wish(session, wish)
    return ApiResponse(data={}, message="撤销成功")
