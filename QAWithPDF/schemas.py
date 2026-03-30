from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    size_bytes: int
    indexed_at: datetime
    ingestion_quality: dict | None = None


class QueryRequest(BaseModel):
    document_id: str = Field(..., description="ID returned by upload endpoint")
    question: str = Field(..., min_length=2)
    conversation_id: str | None = None
    workspace_id: str | None = None
    retrieval_mode: Literal["standard", "hybrid", "decompose", "rerank"] = "hybrid"
    output_mode: Literal["standard", "bullet_points", "executive_brief", "table", "json"] = "standard"
    verification_required: bool = True
    top_k: int | None = None


class Citation(BaseModel):
    source: str
    score: float
    excerpt: str
    page: int | None = None


class QueryResponse(BaseModel):
    answer: str
    document_id: str
    conversation_id: str
    citations: list[Citation]
    output_mode: str = "standard"
    verification: dict | None = None
    retrieval_trace: list[str] = []


class HealthResponse(BaseModel):
    status: str
    version: str


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class SignupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    username: str


class ConversationCreateRequest(BaseModel):
    document_id: str
    title: str | None = None


class MessageView(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime
    citations: list[Citation] = []


class ConversationSummary(BaseModel):
    id: str
    document_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    last_message_preview: str | None = None


class ConversationDetail(BaseModel):
    id: str
    document_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageView]


class WorkspaceCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    description: str | None = None


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    owner_username: str
    created_at: datetime
    updated_at: datetime


class MemoryNodeView(BaseModel):
    id: str
    label: str
    node_type: str
    attributes: dict | None = None


class MemoryEdgeView(BaseModel):
    id: str
    source_node_id: str
    target_node_id: str
    relation: str
    weight: float


class WorkspaceGraphResponse(BaseModel):
    workspace_id: str
    nodes: list[MemoryNodeView]
    edges: list[MemoryEdgeView]


class QueryAutomationCreateRequest(BaseModel):
    workspace_id: str
    name: str = Field(..., min_length=2, max_length=120)
    document_id: str
    prompt: str = Field(..., min_length=3)
    retrieval_mode: Literal["standard", "hybrid", "decompose", "rerank"] = "hybrid"
    output_mode: Literal["standard", "bullet_points", "executive_brief", "table", "json"] = "executive_brief"
    verification_required: bool = True
    schedule_cron: str = "0 9 * * 1-5"


class QueryAutomationResponse(BaseModel):
    id: str
    workspace_id: str
    name: str
    document_id: str
    prompt: str
    retrieval_mode: str
    output_mode: str
    verification_required: bool
    schedule_cron: str
    is_active: bool
    last_run_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class QueryAutomationRunResponse(BaseModel):
    automation_id: str
    run_at: datetime
    result: QueryResponse


class EvaluationSummaryResponse(BaseModel):
    total_queries: int
    success_rate: float
    average_latency_ms: float
    average_verification_score: float
    by_retrieval_mode: dict[str, int]


class ApiKeyCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)


class ApiKeyResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    is_active: bool
    created_at: datetime
    last_used_at: datetime | None = None


class ApiKeyCreateResponse(BaseModel):
    id: str
    name: str
    api_key: str
    key_prefix: str
    created_at: datetime
