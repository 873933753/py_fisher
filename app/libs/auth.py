from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.database import get_session
from app.libs.exceptions import AppError
from app.libs.security import decode_access_token
from app.models.user import User

# tokenUrl 用于 Swagger 文档，填你的登录路径
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/web/login", auto_error=False)


# 获取当前用户 ，如果未登录或登录已过期，返回401状态码
def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    user_id = decode_access_token(token)
    if user_id is None:
        raise AppError("未登录或登录已过期", code=401, http_status=401)

    user = session.get(User, user_id)
    if user is None:
        raise AppError("用户不存在", code=401, http_status=401)

    return user
