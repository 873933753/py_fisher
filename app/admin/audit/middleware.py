"""
一般接口浅审计 - 中间件：

仅处理：path 以 /admin 开头，且 method ∈ {POST, PUT, PATCH, DELETE}
跳过：login / refresh / logout / ping（以及你不想记的）
执行请求 → 看 status_code
单独开 Session 写一条浅日志（不要用请求里那个可能已结束的 session）
操作者：从 Authorization Bearer 解码 jti/admin_id（能解则记；解不出也可记匿名失败）

"""

from sqlmodel import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.admin.audit.service import write_audit
from app.admin.models import AdminUser
from app.admin.security import decode_admin_access_token
from app.database import engine

_WRITE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})

# 不记浅审计的路径（精确匹配）
_SKIP_PATHS = frozenset(
    {
        "/admin/login",
        "/admin/refresh",
        "/admin/logout",
        # 权限接口，只留深审计
        "/admin/rbac/roles/*/access",
    }
)


# 匹配跳过路径的通配符
def _match_skip_pattern(path: str, pattern: str) -> bool:
    if "*" not in pattern:
        return path == pattern
    if not pattern.startswith("/") or not path.startswith("/"):
        return False
    path_parts = [p for p in path.split("/") if p != ""]
    pat_parts = [p for p in pattern.split("/") if p != ""]
    if len(path_parts) != len(pat_parts):
        return False
    for pp, pat in zip(path_parts, pat_parts):
        if pat == "*":
            continue
        if pp != pat:
            return False
    return True


# 跳过白名单的接口，不记浅审计
def _should_skip(path: str) -> bool:
    for pattern in _SKIP_PATHS:
        if _match_skip_pattern(path, pattern):
            return True
    if path.endswith("/ping"):
        return True
    return False


def _module_from_path(path: str) -> str:
    # /admin/users/1 → users；/admin/admins/create → admins
    parts = [p for p in path.split("/") if p]
    # ["admin", "users", ...]
    if len(parts) >= 2 and parts[0] == "admin":
        return parts[1]
    return "admin"


def _action_from_method(method: str) -> str:
    return {
        "POST": "create",
        "PUT": "update",
        "PATCH": "update",
        "DELETE": "delete",
    }.get(method, method.lower())


def _client_ip(request: Request) -> str | None:
    # 若前面有反代，可再读 X-Forwarded-For；本地先用 client.host
    if request.client:
        return request.client.host
    return None


# 一般接口浅审计 - 中间件
class AdminShallowAuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        method = request.method.upper()
        path = request.url.path

        need_audit = (
            path.startswith("/admin")
            and method in _WRITE_METHODS
            and not _should_skip(path)
        )

        response = await call_next(request)

        if not need_audit:
            return response

        try:
            self._write_shallow(request, response.status_code)
        except Exception:
            # 审计失败不能影响业务响应
            pass

        return response

    def _write_shallow(self, request: Request, status_code: int) -> None:
        method = request.method.upper()
        path = request.url.path
        success = status_code < 400

        operator = None
        auth = request.headers.get("Authorization") or ""
        token = auth[7:].strip() if auth.lower().startswith("bearer ") else None

        # 独立 Session(engine)，不占用业务请求的 session 生命周期纠缠
        with Session(engine) as session:
            if token:
                decoded = decode_admin_access_token(token)
                if decoded:
                    operator = session.get(AdminUser, decoded["admin_id"])

            write_audit(
                session,
                operator=operator,
                module=_module_from_path(path),
                action=_action_from_method(method),
                method=method,
                path=path,
                ip=_client_ip(request),
                user_agent=request.headers.get("user-agent"),
                success=success,
                error_message=None if success else f"HTTP {status_code}",
                use_own_commit=True,
            )
