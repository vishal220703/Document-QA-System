from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from QAWithPDF.auth import get_current_user, login_user, signup_user
from QAWithPDF.config import ensure_directories, get_cors_origins
from QAWithPDF.db import init_db
from QAWithPDF.schemas import (
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeyResponse,
    ConversationCreateRequest,
    ConversationDetail,
    ConversationSummary,
    DocumentUploadResponse,
    EvaluationSummaryResponse,
    HealthResponse,
    LoginRequest,
    LoginResponse,
    QueryAutomationCreateRequest,
    QueryAutomationResponse,
    QueryAutomationRunResponse,
    QueryRequest,
    QueryResponse,
    SignupRequest,
    WorkspaceCreateRequest,
    WorkspaceGraphResponse,
    WorkspaceResponse,
)
from QAWithPDF.service import (
    answer_question,
    create_api_key,
    create_conversation,
    create_query_automation,
    create_workspace,
    get_conversation,
    get_evaluation_summary,
    get_workspace_graph,
    ingest_document,
    list_api_keys,
    list_conversations,
    list_query_automations,
    list_workspaces,
    run_query_automation,
)


app = FastAPI(title="DocQuest API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    ensure_directories()
    init_db()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version="2.0.0")


@app.post("/api/v1/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    return login_user(username=payload.username, password=payload.password)


@app.post("/api/v1/auth/signup", response_model=LoginResponse)
def signup(payload: SignupRequest) -> LoginResponse:
    return signup_user(username=payload.username, password=payload.password)


@app.post("/api/v1/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    workspace_id: str | None = None,
    current_user: str = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        return ingest_document(
            file=file,
            content=content,
            workspace_id=workspace_id,
            owner_username=current_user,
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex


@app.post("/api/v1/chat/query", response_model=QueryResponse)
def chat_query(payload: QueryRequest, _: str = Depends(get_current_user)) -> QueryResponse:
    try:
        return answer_question(
            document_id=payload.document_id,
            question=payload.question,
            conversation_id=payload.conversation_id,
            workspace_id=payload.workspace_id,
            retrieval_mode=payload.retrieval_mode,
            output_mode=payload.output_mode,
            verification_required=payload.verification_required,
            top_k=payload.top_k,
        )
    except FileNotFoundError as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex


@app.post("/api/v1/conversations", response_model=ConversationSummary)
def create_conversation_route(
    payload: ConversationCreateRequest, _: str = Depends(get_current_user)
) -> ConversationSummary:
    try:
        return create_conversation(document_id=payload.document_id, title=payload.title)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex


@app.get("/api/v1/conversations", response_model=list[ConversationSummary])
def list_conversations_route(
    document_id: str | None = None, _: str = Depends(get_current_user)
) -> list[ConversationSummary]:
    try:
        return list_conversations(document_id=document_id)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex


@app.get("/api/v1/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation_route(conversation_id: str, _: str = Depends(get_current_user)) -> ConversationDetail:
    try:
        return get_conversation(conversation_id=conversation_id)
    except FileNotFoundError as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex


@app.post("/api/v1/workspaces", response_model=WorkspaceResponse)
def create_workspace_route(payload: WorkspaceCreateRequest, current_user: str = Depends(get_current_user)) -> WorkspaceResponse:
    try:
        return create_workspace(payload=payload, owner_username=current_user)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex


@app.get("/api/v1/workspaces", response_model=list[WorkspaceResponse])
def list_workspaces_route(current_user: str = Depends(get_current_user)) -> list[WorkspaceResponse]:
    try:
        return list_workspaces(owner_username=current_user)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex


@app.get("/api/v1/workspaces/{workspace_id}/graph", response_model=WorkspaceGraphResponse)
def workspace_graph_route(workspace_id: str, current_user: str = Depends(get_current_user)) -> WorkspaceGraphResponse:
    try:
        return get_workspace_graph(workspace_id=workspace_id, owner_username=current_user)
    except FileNotFoundError as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex


@app.post("/api/v1/automations", response_model=QueryAutomationResponse)
def create_automation_route(
    payload: QueryAutomationCreateRequest,
    current_user: str = Depends(get_current_user),
) -> QueryAutomationResponse:
    try:
        return create_query_automation(payload=payload, owner_username=current_user)
    except FileNotFoundError as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex


@app.get("/api/v1/automations", response_model=list[QueryAutomationResponse])
def list_automations_route(
    workspace_id: str,
    current_user: str = Depends(get_current_user),
) -> list[QueryAutomationResponse]:
    try:
        return list_query_automations(workspace_id=workspace_id, owner_username=current_user)
    except FileNotFoundError as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex


@app.post("/api/v1/automations/{automation_id}/run", response_model=QueryAutomationRunResponse)
def run_automation_route(
    automation_id: str,
    current_user: str = Depends(get_current_user),
) -> QueryAutomationRunResponse:
    try:
        return run_query_automation(automation_id=automation_id, owner_username=current_user)
    except FileNotFoundError as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex


@app.get("/api/v1/monitoring/evaluations", response_model=EvaluationSummaryResponse)
def evaluation_summary_route(
    workspace_id: str | None = None,
    _: str = Depends(get_current_user),
) -> EvaluationSummaryResponse:
    try:
        return get_evaluation_summary(workspace_id=workspace_id)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex


@app.post("/api/v1/platform/api-keys", response_model=ApiKeyCreateResponse)
def create_api_key_route(
    payload: ApiKeyCreateRequest,
    current_user: str = Depends(get_current_user),
) -> ApiKeyCreateResponse:
    try:
        return create_api_key(owner_username=current_user, name=payload.name)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex


@app.get("/api/v1/platform/api-keys", response_model=list[ApiKeyResponse])
def list_api_keys_route(current_user: str = Depends(get_current_user)) -> list[ApiKeyResponse]:
    try:
        return list_api_keys(owner_username=current_user)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex
