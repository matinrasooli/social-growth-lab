import os
import uuid

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.core import User, UploadedFile as UploadedFileModel

router = APIRouter(prefix="/uploads", tags=["uploads"])
settings = get_settings()

ALLOWED_EXTENSIONS = {".csv", ".json", ".txt", ".png", ".jpg", ".jpeg", ".mp4"}


@router.post("")
def upload_file(
    file: UploadFile = File(...),
    purpose: str = Form("other"),
    account_id: int | None = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{ext}"
    stored_path = os.path.join(settings.UPLOAD_DIR, stored_name)

    contents = file.file.read()
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File too large. Max {settings.MAX_UPLOAD_MB}MB")

    with open(stored_path, "wb") as f:
        f.write(contents)

    record = UploadedFileModel(
        account_id=account_id, filename=file.filename, stored_path=stored_path,
        content_type=file.content_type or "application/octet-stream", purpose=purpose,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"id": record.id, "filename": record.filename, "purpose": record.purpose}


@router.get("")
def list_uploads(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(UploadedFileModel).order_by(UploadedFileModel.uploaded_at.desc()).all()
