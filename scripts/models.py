"""
MARS Pydantic Data Models
Defines Pydantic v2 models corresponding to MARS JSON schemas:
- SearchFindings (search.json)
- AnalysisTaxonomy (analysis.json)
- SynthesisReport (report.json)
"""

from typing import List, Literal
from pydantic import BaseModel, Field, TypeAdapter


class SearchFinding(BaseModel):
    claim: str
    source_url: str
    excerpt: str
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    timestamp: str
    agent_id: str


class SourceRelation(BaseModel):
    source_url: str
    reliability: Literal["high", "medium", "low"]
    conflict_tags: List[str]


class AnalysisTaxonomy(BaseModel):
    categories: List[str]
    source_relations: List[SourceRelation]
    agent_id: str


class Provenance(BaseModel):
    source_url: str
    excerpt: str
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    timestamp: str
    agent_id: str


class Finding(BaseModel):
    claim: str
    agreement_type: Literal["well-established", "contested", "single-source"]
    provenance: List[Provenance]


class ReportSection(BaseModel):
    category_name: str
    findings: List[Finding]


class SynthesisReport(BaseModel):
    title: str
    summary: str
    sections: List[ReportSection]
    agent_id: str


# TypeAdapters for direct JSON / dict validation
SEARCH_ADAPTER = TypeAdapter(List[SearchFinding])
ANALYSIS_ADAPTER = TypeAdapter(AnalysisTaxonomy)
REPORT_ADAPTER = TypeAdapter(SynthesisReport)

MODEL_MAP = {
    "search": SEARCH_ADAPTER,
    "search.json": SEARCH_ADAPTER,
    "analysis": ANALYSIS_ADAPTER,
    "analysis.json": ANALYSIS_ADAPTER,
    "report": REPORT_ADAPTER,
    "report.json": REPORT_ADAPTER,
    "synthesis": REPORT_ADAPTER,
}
