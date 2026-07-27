from typing import List, Optional

from pydantic import BaseModel

from app.schemas.product import HomeGiftItem
from app.view_models.product import ProductViewModel


class MyGiftData(BaseModel):
    total: int
    items: List[HomeGiftItem]


class MyGifts:
    def __init__(self, gifts, wish_count: Optional[dict] = None):
        # [(isbn, count), ...] → [{'isbn': ..., 'count': ...}, ...]
        self.wish_count = wish_count or {}
        self.total = 0
        self.items: list[HomeGiftItem] = []
        self.__parse(gifts)

    def __parse(self, gifts):
        self.total = len(gifts)
        self.items = [self.__map_to_item(gift) for gift in gifts]

    def __map_to_item(self, gift) -> HomeGiftItem:
        return HomeGiftItem(
            # * 解包：将ProductViewModel.from_record(gift.book)中的所有字段解包到HomeGiftItem中
            **ProductViewModel.from_record(gift.book).model_dump(),
            create_time=gift.create_time,  # 来自 Gift，不是 book
            # 来自 Gift.get_wish_count(session, isbn_list)
            wish_count=self.wish_count.get(gift.isbn, 0),
            launched=gift.launched,
            gift_id=gift.id,
        )

    def to_schema(self) -> MyGiftData:
        return MyGiftData(total=self.total, items=self.items)
