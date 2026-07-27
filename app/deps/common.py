# 公共依赖：当前用户、当前会话

from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.database import get_session
from app.libs.auth import get_current_user
from app.models.user import User


CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentSession = Annotated[Session, Depends(get_session)]
