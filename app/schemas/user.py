from pydantic import BaseModel

from app.libs.helper import FormattedDateTime


# 返回的用户信息模型
class UserInfo(BaseModel):
    id: int
    email: str
    nickname: str
    beans: int
    create_time: FormattedDateTime

    model_config = {"from_attributes": True}  # 允许从 ORM 对象构造 Pydantic 模型


# 登录结果模型
"""
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "token": "eyJhbG...",
    "user": { "id": 1, "email": "...", "nickname": "..." }
  }
}
"""


class LoginResult(BaseModel):
    token: str
    user: UserInfo
