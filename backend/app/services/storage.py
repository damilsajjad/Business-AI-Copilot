"""Local and cloud storage abstraction for uploaded files."""

import os
from pathlib import Path

# Default storage directory under backend
DEFAULT_STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "uploads"


class StorageService:
    """Handles persistence and retrieval of raw uploaded files."""

    def __init__(self, base_dir: Path | str | None = None):
        self.base_dir = Path(base_dir) if base_dir else DEFAULT_STORAGE_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_destination_path(self, business_id: str, file_id: str, filename: str) -> Path:
        """Construct secure partitioned storage path."""
        business_dir = self.base_dir / str(business_id)
        business_dir.mkdir(parents=True, exist_ok=True)
        safe_filename = os.path.basename(filename)
        return business_dir / f"{file_id}_{safe_filename}"

    def save_file(
        self,
        business_id: str,
        file_id: str,
        filename: str,
        content: bytes,
    ) -> str:
        """Save raw file bytes to disk and return absolute/relative storage path."""
        target_path = self.get_destination_path(business_id, file_id, filename)
        with open(target_path, "wb") as f:
            f.write(content)
        return str(target_path)

    def read_file(self, storage_path: str) -> bytes:
        """Read file contents from storage."""
        path = Path(storage_path)
        if not path.exists():
            raise FileNotFoundError(f"Stored file not found at: {storage_path}")
        with open(path, "rb") as f:
            return f.read()

    def delete_file(self, storage_path: str) -> bool:
        """Delete file if it exists."""
        path = Path(storage_path)
        if path.exists():
            path.unlink()
            return True
        return False


storage_service = StorageService()
