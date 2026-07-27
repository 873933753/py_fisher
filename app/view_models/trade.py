from app.schemas.trade import TradeItem, TradeListData
from app.view_models.product import ProductViewModel
from app.schemas.product import HomeGiftItem
from typing import Optional, List
from pydantic import BaseModel


class TradeInfo:
    def __init__(self, items):
        self.total = 0
        self.trades: list[TradeItem] = []
        self.__map_to_list(items)

    def __map_to_list(self, items):
        self.total = len(items)
        self.trades = [self.__map_to_item(single) for single in items]

    def __map_to_item(self, single) -> TradeItem:
        # return TradeItem(
        #     id=single.id,
        #     time=single.create_time,
        #     user_id=single.user_id,
        #     email=single.user.email,
        # )
        # 大部分一致，少数要改名/拼装 → 混合
        data = single.model_dump()  # 将对象转换为字典
        data["time"] = data.pop("create_time")
        data["email"] = single.user.email if single.user else None
        return TradeItem.model_validate(data)

    def to_schema(self, user_type: int | None = None) -> TradeListData:
        return TradeListData(
            total=self.total,
            trades=self.trades,
            user_type=user_type,
        )


class MyGiftData(BaseModel):
    total: int
    items: List[HomeGiftItem]


class MyTrades:
    def __init__(self, trades, wish_count: Optional[dict] = None):
        # [(isbn, count), ...] → [{'isbn': ..., 'count': ...}, ...]
        self.wish_count = wish_count or {}
        self.total = 0
        self.items: list[HomeGiftItem] = []
        self.__parse(trades)

    def __parse(self, trades):
        self.total = len(trades)
        self.items = [self.__map_to_item(trade) for trade in trades]

    def __map_to_item(self, trade) -> HomeGiftItem:
        return HomeGiftItem(
            # * 解包：将ProductViewModel.from_record(gift.book)中的所有字段解包到HomeGiftItem中
            **ProductViewModel.from_record(trade.book).model_dump(),
            create_time=trade.create_time,  # 来自 Gift，不是 book
            # 来自 Gift.get_wish_count(session, isbn_list)
            wish_count=self.wish_count.get(trade.isbn, 0),
            launched=trade.launched,
            wish_id=trade.id,
        )

    def to_schema(self) -> MyGiftData:
        return MyGiftData(total=self.total, items=self.items)
