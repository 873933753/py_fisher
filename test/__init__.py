from fastapi import APIRouter

test_router = APIRouter(prefix="/test")

from test import cookie
