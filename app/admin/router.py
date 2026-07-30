from fastapi import APIRouter

import app.admin.session_filters  # noqa: F401
from app.admin.auth.router import auth_router
from app.admin.uploads.router import uploads_router
from app.admin.users.router import users_router

admin_router = APIRouter()
admin_router.include_router(auth_router)
admin_router.include_router(users_router, prefix="/users")
admin_router.include_router(uploads_router, prefix="/uploads")
