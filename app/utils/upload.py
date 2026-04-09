import os
import uuid
from pathlib import Path
from typing import Iterable

from fastapi import HTTPException, UploadFile, status

BASE_UPLOAD_DIR = Path("uploads")

ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/jpg",
}

ALLOWED_EXTS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def _ensure_upload_dir(folder_name: str) -> Path:
    if not folder_name or not folder_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="folder_name is required",
        )

    safe_folder = folder_name.strip().replace("\\", "/").strip("/")
    folder_path = BASE_UPLOAD_DIR / safe_folder
    folder_path.mkdir(parents=True, exist_ok=True)
    return folder_path


def _validate_file_type(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: {file.content_type}",
        )


def _validate_file_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension: {ext}",
        )
    return ext


async def _save_single_file(
    file: UploadFile,
    folder_name: str,
    max_file_size: int = MAX_FILE_SIZE,
) -> dict:
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is required",
        )

    _validate_file_type(file)
    ext = _validate_file_extension(file.filename)

    contents = await file.read()
    if len(contents) > max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds the limit of {max_file_size} bytes",
        )

    folder_path = _ensure_upload_dir(folder_name)

    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path = folder_path / unique_name

    with open(save_path, "wb") as f:
        f.write(contents)

    return {
        "file_name": unique_name,
        "original_name": file.filename,
        "content_type": file.content_type,
        "size": len(contents),
        "folder": folder_name,
        "relative_path": f"{folder_name}/{unique_name}",
        "full_path": str(save_path).replace("\\", "/"),
    }


async def upload_one_image(
    file: UploadFile,
    folder_name: str,
    max_file_size: int = MAX_FILE_SIZE,
) -> dict:
    return await _save_single_file(
        file=file,
        folder_name=folder_name,
        max_file_size=max_file_size,
    )


async def upload_many_images(
    files: list[UploadFile],
    folder_name: str,
    max_file_size: int = MAX_FILE_SIZE,
    min_files: int = 1,
    max_files: int | None = None,
) -> list[dict]:
    if not files or len(files) < min_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"At least {min_files} file(s) required",
        )

    if max_files is not None and len(files) > max_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {max_files} file(s) allowed",
        )

    results = []
    for file in files:
        saved = await _save_single_file(
            file=file,
            folder_name=folder_name,
            max_file_size=max_file_size,
        )
        results.append(saved)

    return results
