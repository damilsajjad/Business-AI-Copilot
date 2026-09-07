"""AI-powered and heuristic schema mapping proposal generator."""

import json
import logging
import re

import httpx

from app.core.config import settings
from app.schemas.mapping import (
    ColumnMappingItem,
    MappingProposalResponse,
)
from app.schemas.profiler import DataProfileResponse
from app.services.canonical_schema import CANONICAL_FIELDS
from app.services.mapping_validator import validate_mapping

logger = logging.getLogger(__name__)


def _normalize_name(name: str) -> str:
    """Normalize string for fuzzy header comparison."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def heuristic_mapping_proposal(profile: DataProfileResponse) -> MappingProposalResponse:
    """Pure deterministic rule-based mapping generator based on column names and semantic types."""
    mappings: list[ColumnMappingItem] = []
    mapped_source_cols: set[tuple[str, str]] = set()
    mapped_targets: set[str] = set()

    for sheet in profile.sheets:
        for target in CANONICAL_FIELDS:
            if target.name in mapped_targets:
                continue

            best_match = None
            best_score = 0.0
            best_reason = ""

            norm_examples = [_normalize_name(ex) for ex in target.example_column_names]
            norm_target = _normalize_name(target.name)

            for col in sheet.columns:
                if (sheet.sheet_name, col.name) in mapped_source_cols:
                    continue

                norm_col = _normalize_name(col.name)

                # 1. Exact match with example column names or target name
                if norm_col == norm_target or norm_col in norm_examples:
                    score = 0.95
                    reason = f"Exact header match with known {target.label} alias."
                # 2. Substring match
                elif any(ex in norm_col or norm_col in ex for ex in norm_examples if len(ex) > 3):
                    score = 0.80
                    reason = f"Close header pattern match with {target.label}."
                # 3. Semantic fallback for core fields
                elif target.name == "order_date" and col.is_likely_date:
                    score = 0.75
                    reason = "Inferred as primary date column."
                elif target.name == "total_revenue" and col.is_likely_metric and "id" not in norm_col:
                    score = 0.70
                    reason = "Inferred as primary revenue/amount metric."
                else:
                    score = 0.0
                    reason = ""

                if score > best_score:
                    best_score = score
                    best_match = col
                    best_reason = reason

            if best_match and best_score >= 0.70:
                mappings.append(
                    ColumnMappingItem(
                        target_field=target.name,
                        source_sheet=sheet.sheet_name,
                        source_column=best_match.name,
                        confidence=best_score,
                        reasoning=best_reason,
                    )
                )
                mapped_source_cols.add((sheet.sheet_name, best_match.name))
                mapped_targets.add(target.name)

    # Collect unmapped columns
    unmapped = []
    for sheet in profile.sheets:
        for col in sheet.columns:
            if (sheet.sheet_name, col.name) not in mapped_source_cols:
                unmapped.append(f"{sheet.sheet_name}.{col.name}")

    avg_conf = sum(m.confidence for m in mappings) / len(mappings) if mappings else 0.0

    return MappingProposalResponse(
        file_id=profile.file_id,
        mappings=mappings,
        unmapped_columns=unmapped,
        confidence_score=round(avg_conf, 2),
        suggested_by="heuristic",
    )


async def propose_mapping_with_gemini(profile: DataProfileResponse) -> MappingProposalResponse:
    """Generate mapping proposal using Google Gemini API with fallback to heuristic mapper."""
    if not settings.gemini_api_key or settings.gemini_api_key.strip() == "":
        logger.info("No GEMINI_API_KEY configured. Using deterministic heuristic mapper.")
        return heuristic_mapping_proposal(profile)

    # Build structured metadata payload for LLM prompt
    sheets_summary = []
    for sheet in profile.sheets:
        cols_summary = [
            {
                "name": c.name,
                "type": c.detected_type,
                "null_pct": c.null_percentage,
                "sample_values": c.sample_values[:3],
                "is_likely_id": c.is_likely_id,
                "is_likely_metric": c.is_likely_metric,
                "is_likely_date": c.is_likely_date,
            }
            for c in sheet.columns
        ]
        sheets_summary.append({"sheet": sheet.sheet_name, "columns": cols_summary})

    canonical_summary = [
        {"name": f.name, "label": f.label, "type": f.expected_type, "required": f.required, "description": f.description}
        for f in CANONICAL_FIELDS
    ]

    prompt = f"""You are a data mapping specialist for an SME business analytics copilot.
Map the source columns from the uploaded dataset to the target canonical fields.

Target Canonical Fields:
{json.dumps(canonical_summary, indent=2)}

Uploaded Dataset Profile:
{json.dumps(sheets_summary, indent=2)}

Instructions:
1. Match each relevant source column to a target canonical field.
2. Ensure data types match (e.g., date fields must map to datetime columns, revenue/quantity to numeric).
3. Output a valid JSON list of mappings matching this structure:
[
  {{
    "target_field": "order_date",
    "source_sheet": "Sheet1",
    "source_column": "Date",
    "confidence": 0.95,
    "reasoning": "Column 'Date' contains transaction timestamps."
  }}
]
Do not include markdown or formatting other than raw JSON."""

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.llm_model}:generateContent?key={settings.gemini_api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"},
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                logger.warning(f"Gemini API returned status {response.status_code}: {response.text}")
                return heuristic_mapping_proposal(profile)

            data = response.json()
            raw_text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            items = json.loads(raw_text)

            mappings = [ColumnMappingItem(**item) for item in items if isinstance(item, dict)]

            # Deterministic validation of LLM output
            validation = validate_mapping(mappings, profile)
            if not validation.is_valid:
                logger.warning(f"Gemini mapping failed validation: {validation.errors}. Falling back to heuristic.")
                return heuristic_mapping_proposal(profile)

            avg_conf = sum(m.confidence for m in mappings) / len(mappings) if mappings else 0.0

            return MappingProposalResponse(
                file_id=profile.file_id,
                mappings=mappings,
                confidence_score=round(avg_conf, 2),
                suggested_by="gemini",
            )

    except Exception as e:
        logger.warning(f"Gemini LLM call failed ({e}). Falling back to heuristic mapper.")
        return heuristic_mapping_proposal(profile)
