# app/files/router.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from pathlib import Path
from pydantic import BaseModel
from app.database import get_db
from app.auth.dependencies import get_ops_user, get_client_user
from app.auth.models import User
from app.files.models import File as FileModel
from app.utils.security import create_download_token, verify_download_token
from app.config import settings

router = APIRouter()

UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {".pptx", ".docx", ".xlsx"}

# ✅ Renamed to avoid conflict with FastAPI's FileResponse
class FileMetaResponse(BaseModel):
    id: int
    filename: str
    file_type: str

class DownloadResponse(BaseModel):
    download_link: str
    message: str

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_ops_user),
    db: Session = Depends(get_db)
):
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Only {', '.join(ALLOWED_EXTENSIONS)} files are allowed"
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_file = FileModel(
        filename=file.filename,
        file_path=str(file_path),
        file_type=file_extension,
        uploaded_by=current_user.id
    )

    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return {"id": db_file.id, "filename": db_file.filename, "message": "File uploaded successfully"}

@router.get("/files", response_model=List[FileMetaResponse])  # ✅ Updated
async def list_files(
    current_user: User = Depends(get_client_user),
    db: Session = Depends(get_db)
):
    files = db.query(FileModel).all()
    return [
        {"id": file.id, "filename": file.filename, "file_type": file.file_type}
        for file in files
    ]

@router.get("/download-file/{file_id}", response_model=DownloadResponse)
async def get_download_link(
    file_id: int,
    current_user: User = Depends(get_client_user),
    db: Session = Depends(get_db)
):
    file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    download_token = create_download_token({
        "file_id": file_id,
        "user_id": current_user.id
    })

    # ✅ Make sure this uses the correct route
    download_link = f"{settings.BASE_URL}/api/download/{download_token}"

    return {"download_link": download_link, "message": "success"}

@router.get("/download/{token}")
async def download_file(
    token: str,
    current_user: User = Depends(get_client_user),
    db: Session = Depends(get_db)
):
    try:
        payload = verify_download_token(token)
        file_id = payload.get("file_id")
        user_id = payload.get("user_id")

        if user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this file")

        file = db.query(FileModel).filter(FileModel.id == file_id).first()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            path=file.file_path,
            filename=file.filename,
            media_type="application/octet-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid or expired download link: {str(e)}")
