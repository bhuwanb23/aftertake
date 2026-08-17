"""Output file-serving endpoints (Phase 0 Step 10 API contract).

GET /output/video/{filename}      — serve a rendered MP4 (Phase 3+). Until then,
                                    returns a clear 404 the frontend handles by
                                    showing a placeholder.
GET /output/thumbnail/{filename}  — serve a rendered PNG, or a generated
                                    placeholder PNG so <img> tags never break.

Phase 1 Step 3: the thumbnail stub returns a real PNG (solid color, generated
with the stdlib — no image library needed) so the ThumbnailPicker component has
something to render.
"""
import struct
import zlib
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response

from backend.db.database import BASE_DIR

router = APIRouter(prefix="/output", tags=["output"])

OUTPUT_DIR = BASE_DIR / "output"
VIDEO_DIR = OUTPUT_DIR / "videos"
THUMBNAIL_DIR = OUTPUT_DIR / "thumbnails"

# Solid dark-blue placeholder (matches the stub thumbnail palette).
_PLACEHOLDER_COLOR = (11, 37, 69)


def _safe_name(filename: str) -> str:
    """Strip any path components — the param is a filename, not a path."""
    return Path(filename).name


def _solid_png(width: int = 320, height: int = 180, color: tuple = _PLACEHOLDER_COLOR) -> bytes:
    """Build a solid-color PNG with the stdlib (zlib + struct)."""
    r, g, b = color

    def chunk(chunk_type: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + chunk_type
            + data
            + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
        )

    # Scanlines: each row prefixed with filter byte 0 (None).
    raw = b"".join(b"\x00" + bytes([r, g, b]) * width for _ in range(height))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8-bit RGB
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


@router.get("/video/{filename}")
def get_video(filename: str):
    path = VIDEO_DIR / _safe_name(filename)
    if path.is_file():
        return FileResponse(path, media_type="video/mp4")
    # Phase 1: rendering is not implemented yet. Frontend VideoPreview handles
    # this 404 by showing a placeholder.
    raise HTTPException(
        status_code=404,
        detail="Video rendering not implemented yet (Phase 3).",
    )


@router.get("/thumbnail/{filename}")
def get_thumbnail(filename: str):
    path = THUMBNAIL_DIR / _safe_name(filename)
    if path.is_file():
        return FileResponse(path, media_type="image/png")
    # Phase 1 stub: a real (if boring) PNG so image tags render and the
    # ThumbnailPicker can be built against a working <img>.
    return Response(content=_solid_png(), media_type="image/png")
