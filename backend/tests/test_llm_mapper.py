"""Tests for AI and heuristic mapping proposal service."""

from unittest.mock import AsyncMock, patch

import pytest

from app.data.synthetic_data import generate_retail_dataset
from app.services.llm_mapper import (
    heuristic_mapping_proposal,
    propose_mapping_with_gemini,
)
from app.services.profiler import profile_dataset


def test_heuristic_mapping_on_retail_data():
    """Heuristic mapper should accurately map standard columns from the retail dataset."""
    df = generate_retail_dataset(num_orders=50)
    profile = profile_dataset(file_id="test-file", file_name="sales.csv", sheets_dict={"Sheet1": df})

    proposal = heuristic_mapping_proposal(profile)

    assert proposal.file_id == "test-file"
    assert proposal.suggested_by == "heuristic"
    assert proposal.confidence_score > 0.70

    target_map = {m.target_field: m.source_column for m in proposal.mappings}

    assert target_map.get("order_date") == "order_date"
    assert target_map.get("total_revenue") == "total_revenue"
    assert target_map.get("customer_id") == "customer_id"
    assert target_map.get("product_name") == "product_name"
    assert target_map.get("quantity") == "quantity"


@pytest.mark.asyncio
async def test_propose_mapping_without_api_key_uses_heuristic():
    """When GEMINI_API_KEY is empty, it should use heuristic mapper without errors."""
    df = generate_retail_dataset(num_orders=50)
    profile = profile_dataset(file_id="test-file", file_name="sales.csv", sheets_dict={"Sheet1": df})

    with patch("app.services.llm_mapper.settings.gemini_api_key", ""):
        proposal = await propose_mapping_with_gemini(profile)
        assert proposal.suggested_by == "heuristic"
        assert len(proposal.mappings) > 0


@pytest.mark.asyncio
async def test_propose_mapping_with_mocked_gemini():
    """When Gemini returns a valid mapping payload, it should parse and validate properly."""
    from unittest.mock import MagicMock

    df = generate_retail_dataset(num_orders=50)
    profile = profile_dataset(file_id="test-file", file_name="sales.csv", sheets_dict={"Sheet1": df})

    mock_llm_json = """[
        {"target_field": "order_date", "source_sheet": "Sheet1", "source_column": "order_date", "confidence": 0.98, "reasoning": "Transaction timestamp."},
        {"target_field": "total_revenue", "source_sheet": "Sheet1", "source_column": "total_revenue", "confidence": 0.98, "reasoning": "Monetary sales total."}
    ]"""

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": mock_llm_json}]}}]
    }

    with (
        patch("app.services.llm_mapper.settings.gemini_api_key", "test-key-123"),
        patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp),
    ):
        proposal = await propose_mapping_with_gemini(profile)
        assert proposal.suggested_by == "gemini"
        assert len(proposal.mappings) == 2
        assert proposal.confidence_score >= 0.90


@pytest.mark.asyncio
async def test_gemini_malformed_response_falls_back_safely():
    """If Gemini returns invalid JSON, fallback to heuristic mapper gracefully."""
    from unittest.mock import MagicMock

    df = generate_retail_dataset(num_orders=50)
    profile = profile_dataset(file_id="test-file", file_name="sales.csv", sheets_dict={"Sheet1": df})

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "THIS IS NOT JSON"}]}}]
    }

    with (
        patch("app.services.llm_mapper.settings.gemini_api_key", "test-key-123"),
        patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp),
    ):
        proposal = await propose_mapping_with_gemini(profile)
        assert proposal.suggested_by == "heuristic"
        assert len(proposal.mappings) > 0
