from sqlmodel import Field
from typing import Optional, TYPE_CHECKING
from sqlmodel import Relationship
from app.models.base import BaseModel
from sqlmodel import Session, select, func
from typing import List
from app.spider.yushu_product import YuShuProduct
from app.libs.exceptions import AppError

# TYPE_CHECKING - 类型检查，避免循环导入
if TYPE_CHECKING:
    from app.models.user import User


# 心愿清单
class Wish(BaseModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    launched: bool = Field(default=False)  # 是否赠送,默认未赠送

    # 外键关联用户 - 暂时不做反向关联
    # back_populates='gifts' - 反向关联，用于查询礼物时，查询用户时，查询礼物
    user: Optional["User"] = Relationship()
    # 外键关联用户ID
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # 外键关联书籍
    # book:Optional['Book'] = Relationship()
    # # 外键关联书籍ID
    # book_id: Optional[int] = Field(default=None, foreign_key='book.id')

    # 外键关联ISBN - 因为book的isbn是唯一索引，所以可以用isbn关联book
    isbn: Optional[str] = Field(default=None, max_length=15)  # ISBN，最大长度15

    # 与gift的镜像代码
    @property
    def book(self):
        yushu_product = YuShuProduct()
        yushu_product.search_by_keyword(self.isbn)
        return yushu_product.first

    @classmethod
    def my_wishes(cls, session: Session, user_id: int):
        return session.exec(
            select(cls).where(cls.user_id == user_id).order_by(cls.create_time.desc())
        ).all()

    # 获取每个心愿想要的人数
    # 传入isbn列表，返回每个isbn的想要人数
    @classmethod
    def get_wish_count(cls, session: Session, isbn_list: List[str]):
        from app.models.gift import Gift

        if not isbn_list:
            return []
        count_list = session.exec(
            select(
                Gift.isbn,  # 想要的人的isbn
                func.count(Gift.id),  # 想要的人数,count(Wish.id) 会返回一个整数
            )
            .where(
                Gift.launched == False,
                Gift.isbn.in_(isbn_list),  # 想要的人的isbn在isbn_list中
            )
            # 按isbn分组，group_by(Wish.isbn) 会返回一个列表
            # 列表中每个元素是一个元组，元组中第一个元素是isbn，第二个元素是想要的人数
            .group_by(Gift.isbn)
        ).all()
        # [(isbn, count), ...] → [{'isbn': ..., 'count': ...}, ...]
        return [{"isbn": isbn, "count": count} for isbn, count in count_list]

    # 分页查询心愿清单
    # 只拼接查询条件，不执行查询
    @classmethod
    def my_wishes_query(cls, user_id: int):
        return (
            select(cls).where(cls.user_id == user_id).order_by(cls.create_time.desc())
        )

    # 根据id查询心愿清单
    @classmethod
    def get_wish_by_user(cls, session: Session, isbn: str, user_id: int):
        wish = session.exec(
            select(Wish).where(
                Wish.isbn == isbn,
                Wish.user_id == user_id,
                Wish.launched == False,
            )
        ).first()

        if not wish:
            raise AppError("心愿清单不存在")
        return wish

    @classmethod
    def get_wish_by_id(cls, session: Session, wish_id: int):
        wish = session.exec(
            select(Wish).where(
                Wish.id == wish_id,
                Wish.launched == False,
            )
        ).first()
        if not wish:
            raise AppError("心愿清单不存在")
        return wish
