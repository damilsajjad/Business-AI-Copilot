"""Pydantic schemas for Multi-Agent AI Core & Interactive Copilot."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DomainInsight(BaseModel):
    """Deep-dive insight generated for a specific business operational domain."""

    domain: str  # "executive", "sales", "products", "customers", "demand"
    headline: str
    summary: str
    key_metrics: dict[str, Any] = {}
    positives: list[str] = []
    concerns: list[str] = []


class ExecutiveBriefReport(BaseModel):
    """Complete multi-agent executive briefing report."""

    file_id: str
    business_id: str
    generated_at: datetime
    executive_summary: str
    health_score: int  # 0 to 100
    domain_insights: list[DomainInsight]
    key_risks: list[str]
    strategic_opportunities: list[str]
    recommended_initiatives: list[str]
    synthesized_by: str


class ChatMessage(BaseModel):
    """Conversational chat message."""

    role: str  # "user", "assistant", "system"
    content: str
    created_at: datetime | None = None


class CopilotChatRequest(BaseModel):
    """Request payload for Copilot interactive Q&A."""

    message: str
    history: list[ChatMessage] = []


class CopilotChatResponse(BaseModel):
    """Response from AI Business Copilot grounded strictly in verified business data."""

    reply: str
    cited_metrics: dict[str, Any] = {}
    suggested_follow_ups: list[str] = []
