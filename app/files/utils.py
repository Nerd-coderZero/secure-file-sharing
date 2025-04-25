# app/files/utils.py
from fastapi import UploadFile, HTTPException
from app.config import settings

async def validate_file_size(file: UploadFile):
    # Read a chunk to check file size
    chunk_size = 1024 * 1024  # 1MB
    total_size = 0
    
    chunk = await file.read(chunk_size)
    while chunk:
        total_size += len(chunk)
        if total_size > settings.MAX_UPLOAD_SIZE:
            # Reset file position
            await file.seek(0)
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE / (1024 * 1024)}MB"
            )
        chunk = await file.read(chunk_size)
    
    # Reset file position
    await file.seek(0)
    return True

# Use in the upload endpoint:
@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_ops_user),
    db: Session = Depends(get_db)
):
    # Validate file size
    await validate_file_size(file)
    
    # Rest of the implementation...