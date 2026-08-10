"""
Security validation utilities for uploaded log files.
"""

from __future__ import annotations

import os
import re
from fastapi import HTTPException, status

MAX_LOG_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".log", ".txt", ".json"}
ALLOWED_MIME_TYPES = {
    "text/plain",
    "application/json",
    "text/x-log",
    "text/log",
    "application/octet-stream",
    "text/csv",
}


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes filename and prevents directory traversal.
    """
    # Extract only the base name
    base_name = os.path.basename(filename.strip())
    # Remove any dangerous null bytes or path separators
    clean_name = re.sub(r"[^\w\.\-\_]", "_", base_name)
    return clean_name or "uploaded_server.log"


def validate_log_upload(filename: str, content_type: str | None, file_size: int) -> tuple[str, str]:
    """
    Validates file extension, MIME type, and size.
    Returns (sanitized_filename, file_type).
    """
    if file_size > MAX_LOG_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of 10MB (received {file_size / (1024 * 1024):.2f}MB).",
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes).",
        )

    clean_name = sanitize_filename(filename)
    _, ext = os.path.splitext(clean_name.lower())

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported file type '{ext}'. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}.",
        )

    # Validate MIME type if provided
    if content_type:
        clean_mime = content_type.split(";")[0].strip().lower()
        if clean_mime not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported content type '{clean_mime}'. Allowed types: text/plain, application/json, text/x-log.",
            )

    file_type = ext.lstrip(".")
    return clean_name, file_type


def decode_log_bytes(raw_bytes: bytes) -> str:
    """
    Decodes raw bytes into a string with UTF-8 primary and latin-1 fallback.
    """
    try:
        return raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return raw_bytes.decode("utf-8", errors="replace")
        except Exception:
            return raw_bytes.decode("latin-1", errors="replace")
