import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from app.core.auth import get_current_user


router = APIRouter(prefix="/media", tags=["media"])

UPLOAD_DIR = Path(
    os.getenv(
        "UPLOAD_DIR",
        str(Path(__file__).resolve().parents[3] / "uploads"),
    )
)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class DeleteMediaPayload(BaseModel):
    file_url: str = Field(min_length=1)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_media(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    if not file.content_type or not (
        file.content_type.startswith("image/") or file.content_type.startswith("video/")
    ):
        raise HTTPException(status_code=400, detail="Only image and video uploads are supported")

    suffix = Path(file.filename or "").suffix
    file_name = f"{uuid4().hex}{suffix}"
    target_path = UPLOAD_DIR / file_name
    content = await file.read()
    target_path.write_bytes(content)

    return {
        "file_name": file_name,
        "file_url": f"/uploads/{file_name}",
        "content_type": file.content_type,
        "size": len(content),
    }


@router.delete("")
def delete_media(
    payload: DeleteMediaPayload,
    user=Depends(get_current_user),
):
    file_name = payload.file_url.rsplit("/", maxsplit=1)[-1]
    target_path = (UPLOAD_DIR / file_name).resolve()
    if not str(target_path).startswith(str(UPLOAD_DIR.resolve())):
        raise HTTPException(status_code=400, detail="Invalid file path")
    if target_path.exists():
        target_path.unlink()
    return {"status": "ok"}
