import uuid  # 生成唯一id

import oss2
from fastapi import UploadFile

from app.libs.exceptions import AppError
from app.secure import oss_settings


def _get_bucket() -> oss2.Bucket:
    auth = oss2.Auth(
        oss_settings.OSS_ACCESS_KEY_ID,
        oss_settings.OSS_ACCESS_KEY_SECRET,
    )
    # endpoint 用主机名，不要带 https://
    return oss2.Bucket(
        auth,
        oss_settings.OSS_ENDPOINT,
        oss_settings.OSS_BUCKET_NAME,
    )


def upload_bytes_to_oss(object_key: str, data: bytes, content_type: str) -> str:
    """
    上传到 OSS，返回可公开访问的完整 URL。
    object_key 示例: avatars/1/uuid.jpg
    """
    if not object_key or object_key.startswith("/"):
        raise AppError("无效的对象键")

    try:
        bucket = _get_bucket()
        bucket.put_object(
            object_key,
            data,
            headers={
                "Content-Type": content_type,
                # "Content-Disposition": "inline",
            },
        )
    except oss2.exceptions.OssError as e:
        raise AppError(f"上传失败: {e}") from e

    return f"{oss_settings.OSS_PUBLIC_BASE_URL}/{object_key}"


_ALLOWED = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
_MAX_IMAGE_SIZE = 2
_MAX_SIZE = _MAX_IMAGE_SIZE * 1024 * 1024


# 头像传 prefix="avatars"，商品用 prefix="products"。
def save_image(file: UploadFile, *, prefix: str = "uploads") -> str:
    """校验并上传图片，返回完整公网 URL。"""
    content_type = (file.content_type or "").lower()
    if content_type not in _ALLOWED:
        raise AppError("仅支持 jpg / png / webp / gif")
    data = file.file.read()
    if not data:
        raise AppError("文件为空")
    if len(data) > _MAX_SIZE:
        raise AppError(f"文件不能超过 {_MAX_IMAGE_SIZE}MB")
    prefix = prefix.strip("/")
    ext = _ALLOWED[content_type]
    key = f"{prefix}/{uuid.uuid4().hex}{ext}"
    return upload_bytes_to_oss(key, data, content_type)
