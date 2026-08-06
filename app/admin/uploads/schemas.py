from pydantic import BaseModel


class UploadImageResult(BaseModel):
    url: str
