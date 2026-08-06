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


# 根据文件头判定图片 MIME；无法识别则返回 None。
def _detect_image_content_type(data: bytes) -> str | None:
    """根据文件头判定图片 MIME；无法识别则返回 None。"""
    # 目前支持的图片类型：jpg、png、webp、gif
    if len(data) < 12:
        return None
    # JPEG
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    # PNG
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    # GIF
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    # WEBP: RIFF....WEBP
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


# 头像传 prefix="avatars"，商品用 prefix="products"。


# 1、先 read() 得到 data（空/超大仍先校验）
# 2、detected = _detect_image_content_type(data)
# 3、如果 detected 不在 _ALLOWED → AppError("仅支持 jpg / png / webp / gif")（或更明确：「无法识别为合法图片」）
# 4、用 detected 取扩展名、传给 OSS，不要再用客户端的 content_type 决定类型
def save_image(file: UploadFile, *, prefix: str = "uploads") -> str:
    data = file.file.read()
    if not data:
        raise AppError("文件为空")
    if len(data) > _MAX_SIZE:
        raise AppError(f"文件不能超过 {_MAX_IMAGE_SIZE}MB")
    # 校验文件类型，如果 detected 不在 _ALLOWED → 拒绝上传
    detected = _detect_image_content_type(data)
    if detected not in _ALLOWED:
        raise AppError("仅支持 jpg / png / webp / gif")

    declared = (file.content_type or "").lower().split(";")[0].strip()
    if (
        declared
        and declared not in ("application/octet-stream",)
        and declared != detected
    ):
        raise AppError("文件类型与声明不一致")

    prefix = prefix.strip("/")
    ext = _ALLOWED[detected]
    key = f"{prefix}/{uuid.uuid4().hex}{ext}"
    return upload_bytes_to_oss(key, data, detected)
