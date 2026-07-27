from sqlmodel import Field
from typing import Optional, TYPE_CHECKING
from sqlmodel import Relationship
from app.models.base import BaseModel
from sqlmodel import Session, select, func
from app.spider.yushu_product import YuShuProduct
from app.setting import RECENT_GIFT_COUNT
from typing import List
from app.models.wish import Wish
from app.libs.exceptions import AppError

# TYPE_CHECKING - 类型检查，避免循环导入
if TYPE_CHECKING:
    from app.models.user import User


# 礼物模型
class Gift(BaseModel, table=True):
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
    isbn: Optional[str] = Field(default=None, max_length=50)  # ISBN，最大长度15

    # 用isbn去查书籍信息
    # 用@property装饰器，将book方法变成一个属性
    @property
    def book(self):
        yushu_product = YuShuProduct()
        yushu_product.search_by_keyword(self.isbn)
        return yushu_product.first

    # 过滤最近赠送的礼物 - 最近赠送的礼物
    # 用@staticmethod装饰器，将recent_gifts方法变成一个静态方法
    # 静态方法不需要实例化，可以直接使用类名调用
    """ 
    数据过滤:
    1) 只查最近的5条数据
  
  """

    @staticmethod
    def recent_gifts(session: Session):

        # 子查询：每个 isbn 只保留最新一条的 create_time
        subq = (
            select(
                Gift.isbn,
                func.max(Gift.create_time).label("max_create_time"),
            )
            .where(Gift.launched == False)
            .group_by(Gift.isbn)
            .subquery()
        )

        # 查询：用 isbn + create_time 回表，再排序取最近 N 条
        return session.exec(
            select(Gift)
            .join(
                subq,
                (Gift.isbn == subq.c.isbn)
                & (Gift.create_time == subq.c.max_create_time),
            )
            .where(
                Gift.launched == False,
            )
            # 要先按创建时间排序，再取配置的条数
            # 因为如果先取配置的条数，再按创建时间排序，会导致取到的数据不准确
            .order_by(Gift.create_time.desc())  # 按创建时间排序，最近创建的在前
            .limit(RECENT_GIFT_COUNT)  # 只取配置的条数
        ).all()

    # 判断是否是自己的礼物
    def is_yourself_gift(self, user_id: int):
        return True if self.user_id == user_id else False

    # 获取当前用户的赠送清单
    # 用@classmethod装饰器，将my_gifts方法变成一个类方法
    # 与静态方法的区别是：类方法可以访问类属性，而静态方法不能访问类属性
    @classmethod
    def my_gifts(cls, session: Session, user_id: int):
        return session.exec(
            select(cls).where(cls.user_id == user_id).order_by(cls.create_time.desc())
        ).all()

    # 获取每个礼物想要的人数
    # 传入isbn列表，返回每个isbn的想要人数
    @classmethod
    def get_wish_count(cls, session: Session, isbn_list: List[str]):
        if not isbn_list:
            return []
        count_list = session.exec(
            select(
                Wish.isbn,  # 想要的人的isbn
                func.count(Wish.id),  # 想要的人数,count(Wish.id) 会返回一个整数
            )
            .where(
                Wish.launched == False,
                Wish.isbn.in_(isbn_list),  # 想要的人的isbn在isbn_list中
            )
            # 按isbn分组，group_by(Wish.isbn) 会返回一个列表
            # 列表中每个元素是一个元组，元组中第一个元素是isbn，第二个元素是想要的人数
            .group_by(Wish.isbn)
        ).all()
        # [(isbn, count), ...] → [{'isbn': ..., 'count': ...}, ...]
        return [{"isbn": isbn, "count": count} for isbn, count in count_list]

    # 根据id查询礼物 ，且礼物未赠送
    @classmethod
    def get_gift_by_id(cls, session: Session, gift_id: int):
        gift = session.exec(
            select(cls).where(cls.id == gift_id, cls.launched == False)
        ).first()
        if not gift:
            raise AppError("礼物不存在")
        return gift

    # 查用户是否有该isbn的礼物
    @classmethod
    def get_gift_by_user_and_isbn(cls, session: Session, user_id: int, isbn: str):
        gift = session.exec(
            select(cls).where(
                cls.user_id == user_id, cls.isbn == isbn, cls.launched == False
            )
        ).first()
        if not gift:
            raise AppError("礼物不存在")
        return gift
