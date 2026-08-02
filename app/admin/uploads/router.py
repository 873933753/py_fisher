from fastapi import APIRouter, File, Query, UploadFile

from app.admin.auth.schemas import ApiResponse
from app.admin.dependencies import CurrentAdmin
from app.admin.uploads.schemas import UploadImageResult
from app.libs.oss import save_image

uploads_router = APIRouter(
    tags=["admin-uploads"],
    # dependencies=[Depends(require_permissions(PERM_UPLOAD_MANAGE))],
)


@uploads_router.post(
    "/image",
    response_model=ApiResponse[UploadImageResult],
    summary="上传图片到 OSS",
)
def upload_image(
    current_admin: CurrentAdmin,
    file: UploadFile = File(...),
    prefix: str = Query(default="uploads", min_length=1, max_length=64),
):
    # 可选：限制 prefix 白名单，避免乱写路径
    allowed_prefix = {"uploads", "avatars", "products"}
    if prefix not in allowed_prefix:
        # 或 raise AppError
        prefix = "uploads"

    url = save_image(file, prefix=prefix)
    return ApiResponse(data=UploadImageResult(url=url), message="上传成功")
