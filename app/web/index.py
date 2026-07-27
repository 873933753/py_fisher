from fastapi import Depends
from app.schemas.response import ApiResponse
from app.database import get_session
from app.models.gift import Gift
from typing import Annotated
from sqlmodel import Session
from app.web import web_router
from app.view_models.gift import MyGiftData, MyGifts

CurrentSession = Annotated[Session, Depends(get_session)]


# 获取赠送清单
@web_router.get("/home/list", response_model=ApiResponse[MyGiftData])
def get_gifts(session: CurrentSession):
    recent_gifts = Gift.recent_gifts(session)
    # products = [ProductViewModel.from_record(gift.book) for gift in recent_gifts]
    return ApiResponse(data=MyGifts(recent_gifts).to_schema())
