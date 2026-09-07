"""Tests for file upload and profiling API endpoints."""

from uuid import uuid4

import pytest

from app.data.synthetic_data import (
    generate_multi_sheet_xlsx_bytes,
    generate_retail_csv_bytes,
)
from tests.conftest import TEST_BUSINESS_ID, TEST_USER_ID

TEST_FILE_ID = str(uuid4())
TEST_FILE_RECORD = {
    "id": TEST_FILE_ID,
    "business_id": TEST_BUSINESS_ID,
    "uploaded_by": TEST_USER_ID,
    "original_filename": "retail_data.csv",
    "storage_path": f"/tmp/storage/{TEST_FILE_ID}_retail_data.csv",
    "file_type": "csv",
    "file_size_bytes": 1024,
    "status": "profiled",
    "sheet_count": 1,
    "error_message": "",
    "metadata": {
        "file_id": TEST_FILE_ID,
        "file_name": "retail_data.csv",
        "total_sheets": 1,
        "sheets": [],
        "data_quality_score": 95.0,
        "overall_warnings": [],
    },
    "created_at": "2025-01-01T00:00:00+00:00",
    "updated_at": "2025-01-01T00:00:00+00:00",
}


class TestUploadFile:
    """Tests for POST /api/v1/businesses/{business_id}/uploads."""

    @pytest.mark.asyncio
    async def test_returns_401_without_token(self, client):
        """Unauthenticated upload request should return 401."""
        response = await client.post(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads",
            files={"file": ("test.csv", b"a,b\n1,2", "text/csv")},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_returns_403_for_non_member(self, authenticated_client, mock_supabase):
        """Non-member upload request should return 403."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        response = await authenticated_client.post(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads",
            files={"file": ("test.csv", b"a,b\n1,2", "text/csv")},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_returns_400_for_unsupported_extension(
        self, authenticated_client, mock_supabase
    ):
        """Unsupported file format should return 400."""
        # Membership check passes
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]

        response = await authenticated_client.post(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads",
            files={"file": ("data.pdf", b"dummy pdf content", "application/pdf")},
        )
        assert response.status_code == 400
        assert "Unsupported file format" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_valid_csv_success(
        self, authenticated_client, mock_supabase
    ):
        """Valid CSV upload should profile and save record, returning 201."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            TEST_FILE_RECORD
        ]

        csv_bytes = generate_retail_csv_bytes(num_orders=20)

        response = await authenticated_client.post(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads",
            files={"file": ("retail_data.csv", csv_bytes, "text/csv")},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["original_filename"] == "retail_data.csv"
        assert data["file_type"] == "csv"

    @pytest.mark.asyncio
    async def test_upload_valid_xlsx_success(
        self, authenticated_client, mock_supabase
    ):
        """Valid multi-sheet XLSX upload should profile multiple sheets, returning 201."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {**TEST_FILE_RECORD, "original_filename": "sales.xlsx", "file_type": "xlsx", "sheet_count": 2}
        ]

        xlsx_bytes = generate_multi_sheet_xlsx_bytes(num_orders=15)

        response = await authenticated_client.post(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads",
            files={
                "file": (
                    "sales.xlsx",
                    xlsx_bytes,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["sheet_count"] == 2


class TestGetUploadedFiles:
    """Tests for listing and viewing uploaded files."""

    @pytest.mark.asyncio
    async def test_list_uploaded_files(self, authenticated_client, mock_supabase):
        """Should return list of uploaded files for the business."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = [
            TEST_FILE_RECORD
        ]

        response = await authenticated_client.get(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == TEST_FILE_ID

    @pytest.mark.asyncio
    async def test_get_file_data_profile(self, authenticated_client, mock_supabase):
        """Should retrieve the stored data profile."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "metadata": TEST_FILE_RECORD["metadata"]
        }

        response = await authenticated_client.get(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads/{TEST_FILE_ID}/profile"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["file_id"] == TEST_FILE_ID
        assert data["data_quality_score"] == 95.0

    @pytest.mark.asyncio
    async def test_load_sample_dataset_success(self, authenticated_client, mock_supabase):
        """Should generate, profile, and save sample retail dataset."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"role": "owner"}
        ]
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            TEST_FILE_RECORD
        ]

        response = await authenticated_client.post(
            f"/api/v1/businesses/{TEST_BUSINESS_ID}/uploads/sample"
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == TEST_FILE_ID
