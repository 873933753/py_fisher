from sqlmodel import Session, select

from app.models.gift import Gift
from app.models.wish import Wish


# 获取交易列表,业务逻辑
def get_trade_list(session: Session, user_id: int, isbn: str):
    user_type = 0
    # 判断该用户是否已经赠送过该商品,如果赠送过，则返回True，否则返回False
    has_gift = session.exec(
        select(Gift).where(
            Gift.user_id == user_id,
            Gift.isbn == isbn,
            Gift.launched == False,
        )
    ).first()
    # 判断该用户是否是索要者
    has_wish = session.exec(
        select(Wish).where(
            Wish.user_id == user_id,
            Wish.isbn == isbn,
            Wish.launched == False,
        )
    ).first()
    if has_gift:
        user_type = 1
    elif has_wish:
        user_type = 2
    # 默认显示赠送者名单
    # 如果是赠送者,返回索取者名单
    # 如果是索要者,返回赠送者名单

    list = session.exec(
        select(Gift).where(
            Gift.isbn == isbn,
            Gift.launched == False,
        )
    ).all()
    if user_type == 1:
        list = session.exec(
            select(Wish).where(
                Wish.isbn == isbn,
                Wish.launched == False,
            )
        ).all()

    return user_type, list
