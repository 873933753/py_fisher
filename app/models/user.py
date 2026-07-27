from sqlmodel import Field
from typing import Optional
from app.models.base import BaseModel
from sqlalchemy import Column, String, func
from sqlmodel import Session, select
from app.models.gift import Gift
from app.models.wish import Wish
from app.spider.yushu_product import YuShuProduct
from app.libs.exceptions import AppError

""" 
适合加索引的场景：
经常作为查询条件的字段（如 isbn、用户 ID）
经常用于 WHERE、ORDER BY、JOIN 的字段
索引也有代价：写入、更新、删除时要维护索引，会稍微慢一点，并多占一点存储。
 """


class User(BaseModel, table=True):
    # 表明默认是user，这里改成user1
    # __tablename__ = 'user1'
    # index=True 索引 索引：解决“查得快不快”-什么时候需要 index=True
    #  - 唯一，unique=True — 避免重复
    # primary_key=True 的主键默认就有索引，一般不需要再写 index=True
    id: Optional[int] = Field(default=None, primary_key=True)
    nickname: Optional[str] = Field(default=None, max_length=24)
    phone_number: Optional[str] = Field(default=None, max_length=18, unique=True)
    email: str = Field(max_length=50, unique=True)
    confirmed: bool = Field(default=False)
    beans: int = Field(default=0)
    send_counter: int = Field(default=0)  # 赠送次数
    receive_counter: int = Field(default=0)  # 索取次数
    wx_open_id: Optional[str] = Field(default=None, max_length=50)
    wx_name: Optional[str] = Field(default=None, max_length=32)
    # 修改password字段为password_hash字段，数据库中是password字段，模型中是password_hash字段
    # nullable=False - 不允许为空,Column中的
    password_hash: str = Field(
        sa_column=Column("password", String(128), nullable=False)
    )

    # 用于展示当前礼物的用户信息
    @property
    def summary(self) -> dict:
        return {
            "nickname": self.nickname,
            "email": self.email,
            "beans": self.beans,
            "send_counter": self.send_counter,
            "receive_counter": self.receive_counter,
        }

    # 判断鱼豆是否 > 1
    def can_request_gift_beans(self) -> bool:
        return True if self.beans > 1 else False

    # 每两次索要必须送出一本
    def can_request_gift_more(self, session: Session) -> bool:
        from app.models.drift import Drift
        from app.libs.enums import DriftStatus

        success_send_counter = session.exec(
            select(func.count())
            .select_from(Gift)
            .where(
                Gift.user_id == self.id,
                Gift.launched == True,
            )
        ).one()
        success_receive_counter = session.exec(
            select(func.count())
            .select_from(Drift)
            .where(
                Drift.requester_id == self.id,  # 索取方是 requester，不是 gifter
                Drift.status == DriftStatus.Success,
            )
        ).one()
        # 还能索取的条件
        # success_receive_counter < (success_send_counter + 1) * 2
        return success_receive_counter < (success_send_counter + 1) * 2

    # 判断是否可以添加到赠送清单或心愿清单
    def can_save_to_list(self, session: Session, isbn: str) -> bool:
        # 1）判断是否存在该商品
        yushu_product = YuShuProduct()
        yushu_product.search_by_keyword(keyword=isbn)
        record = yushu_product.first  # 获取第一条数据
        if not record:
            # return ApiResponse(data={},message='商品不存在',code=400)
            raise AppError(message="商品不存在")

        # 2）判断赠送清单中是否存在该商品,用 user_id + isbn 查 Gift 表
        gift = session.exec(
            select(Gift).where(
                Gift.user_id == self.id,
                # 字典取值用[] 或 .get()
                Gift.isbn == record.get("productName"),
                Gift.launched == False,
            )
            # 执行查询,获取第一条数据
        ).first()

        # 3）判断心愿清单中是否存在该商品
        wish = session.exec(
            select(Wish).where(
                # 这里的self是User模型，id是User模型的id字段
                Wish.user_id == self.id,
                Wish.isbn == record.get("productName"),
                Wish.launched == False,
            )
        ).first()

        # 如果已经在赠送清单或心愿清单中，则不添加
        if wish or gift:
            return False
        return True

    # 按照邮箱查询用户
    @classmethod
    def get_user_by_email(cls, session: Session, email: str) -> Optional[User]:
        return session.exec(
            select(cls).where(cls.email == email)
            # first_or_none() - 如果查询结果为空，则返回 None
            # first() - 如果查询结果为空，则抛出异常
        ).first()

    # 生成token - 链接上的
    def generate_token(self, expiration: int = 300) -> str:
        from app.libs.security import create_reset_token

        return create_reset_token(self.id, expiration)

    # 验证token是否有效
    @classmethod
    def validate_token(cls, session, token):
        from app.libs.security import decode_reset_token

        user_id = decode_reset_token(token)
        if not user_id:
            raise AppError("token无效")
        user = session.get(cls, user_id)
        if not user:
            raise AppError("用户不存在")
        return user

    # 重置密码
    def reset_password(self, new_password: str, session: Session) -> None:
        # 1、验证token是否有效
        from app.database import auto_commit
        from app.libs.security import hash_password

        self.password_hash = hash_password(new_password)
        with auto_commit(session):
            session.add(self)

    # 按照id查询用户
    @classmethod
    def get_user_by_id(cls, session: Session, user_id: int) -> Optional[User]:
        user = session.get(cls, user_id)
        if not user:
            raise AppError("用户不存在")
        return user
