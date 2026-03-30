from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import secrets
import time
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import select

from QAWithPDF.config import settings
from QAWithPDF.data_ingestion import load_data_from_bytes
from QAWithPDF.db import get_session
from QAWithPDF.db_models import (
    ApiKey,
    Conversation,
    MemoryEdge,
    MemoryNode,
    Message,
    QueryAutomation,
    QueryEvaluation,
    WebhookEvent,
    Workspace,
    WorkspaceDocument,
)
from QAWithPDF.embedding import build_and_persist_index, load_query_engine
from QAWithPDF.schemas import (
    ApiKeyCreateResponse,
    ApiKeyResponse,
    Citation,
    ConversationDetail,
    ConversationSummary,
    DocumentUploadResponse,
    EvaluationSummaryResponse,
    MemoryEdgeView,
    MemoryNodeView,
    MessageView,
    QueryAutomationCreateRequest,
    QueryAutomationResponse,
    QueryAutomationRunResponse,
    QueryResponse,
    WorkspaceCreateRequest,
    WorkspaceGraphResponse,
    WorkspaceResponse,
)


def _document_storage_dir(document_id: str) -> Path:
    return settings.storage_dir / "indexes" / document_id


def _store_upload(file: UploadFile, content: bytes) -> tuple[str, Path]:
    document_id = uuid4().hex
    file_name = file.filename or "uploaded_document"
    destination = settings.upload_dir / f"{document_id}_{file_name}"
    destination.write_bytes(content)
    return document_id, destination


def _compute_ingestion_quality(documents) -> dict:
    char_count = sum(len((doc.text or "").strip()) for doc in documents)
    empty_chunks = sum(1 for doc in documents if not (doc.text or "").strip())
    pages = sorted(
        {
            int(doc.metadata.get("page"))
            for doc in documents
            if isinstance(doc.metadata, dict) and doc.metadata.get("page")
        }
    )
    table_chunks = sum(
        1
        for doc in documents
        if isinstance(doc.metadata, dict) and doc.metadata.get("source_kind") == "table"
    )
    return {
        "chunk_count": len(documents),
        "character_count": char_count,
        "empty_chunks": empty_chunks,
        "detected_pages": pages,
        "table_chunks": table_chunks,
        "quality_score": round(max(0.0, 1.0 - (empty_chunks / max(len(documents), 1))), 3),
    }


def _workspace_for_owner(session, workspace_id: str, owner_username: str) -> Workspace:
    workspace = (
        session.execute(
            select(Workspace).where(Workspace.id == workspace_id, Workspace.owner_username == owner_username)
        )
        .scalars()
        .first()
    )
    if workspace is None:
        raise FileNotFoundError(f"Workspace not found for user: {workspace_id}")
    return workspace


def ingest_document(
    file: UploadFile,
    content: bytes,
    workspace_id: str | None = None,
    owner_username: str | None = None,
) -> DocumentUploadResponse:
    document_id, saved_path = _store_upload(file, content)
    display_name = file.filename or saved_path.name
    docs = load_data_from_bytes(file_name=file.filename or saved_path.name, file_bytes=content)
    build_and_persist_index(documents=docs, index_dir=_document_storage_dir(document_id))
    ingestion_quality = _compute_ingestion_quality(docs)

    if workspace_id and owner_username:
        with get_session() as session:
            _workspace_for_owner(session=session, workspace_id=workspace_id, owner_username=owner_username)
            link = WorkspaceDocument(
                workspace_id=workspace_id,
                document_id=document_id,
                filename=display_name,
                ingestion_quality_json=json.dumps(ingestion_quality),
            )
            session.add(link)

    return DocumentUploadResponse(
        document_id=document_id,
        filename=display_name,
        size_bytes=len(content),
        indexed_at=datetime.now(timezone.utc),
        ingestion_quality=ingestion_quality,
    )


def _conversation_title(question: str) -> str:
    title = " ".join(question.strip().split())
    return title[:80] if len(title) > 80 else title


def create_conversation(document_id: str, title: str | None = None) -> ConversationSummary:
    with get_session() as session:
        conversation = Conversation(document_id=document_id, title=title or "New Chat")
        session.add(conversation)
        session.flush()
        return ConversationSummary(
            id=conversation.id,
            document_id=conversation.document_id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            last_message_preview=None,
        )


def create_workspace(payload: WorkspaceCreateRequest, owner_username: str) -> WorkspaceResponse:
    with get_session() as session:
        workspace = Workspace(
            name=payload.name.strip(),
            description=(payload.description.strip() if payload.description else None),
            owner_username=owner_username,
        )
        session.add(workspace)
        session.flush()
        return WorkspaceResponse(
            id=workspace.id,
            name=workspace.name,
            description=workspace.description,
            owner_username=workspace.owner_username,
            created_at=workspace.created_at,
            updated_at=workspace.updated_at,
        )


def list_workspaces(owner_username: str) -> list[WorkspaceResponse]:
    with get_session() as session:
        rows = (
            session.execute(
                select(Workspace)
                .where(Workspace.owner_username == owner_username)
                .order_by(Workspace.updated_at.desc())
            )
            .scalars()
            .all()
        )
        return [
            WorkspaceResponse(
                id=row.id,
                name=row.name,
                description=row.description,
                owner_username=row.owner_username,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]


def list_conversations(document_id: str | None = None) -> list[ConversationSummary]:
    with get_session() as session:
        stmt = select(Conversation).order_by(Conversation.updated_at.desc())
        if document_id:
            stmt = stmt.where(Conversation.document_id == document_id)

        rows = session.execute(stmt).scalars().all()
        summaries: list[ConversationSummary] = []
        for conv in rows:
            last_msg_stmt = (
                select(Message)
                .where(Message.conversation_id == conv.id)
                .order_by(Message.created_at.desc())
                .limit(1)
            )
            last_msg = session.execute(last_msg_stmt).scalar_one_or_none()
            summaries.append(
                ConversationSummary(
                    id=conv.id,
                    document_id=conv.document_id,
                    title=conv.title,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    last_message_preview=(last_msg.content[:120] if last_msg else None),
                )
            )
        return summaries


def get_conversation(conversation_id: str) -> ConversationDetail:
    with get_session() as session:
        conv = session.get(Conversation, conversation_id)
        if conv is None:
            raise FileNotFoundError(f"Conversation not found: {conversation_id}")

        msg_stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        rows = session.execute(msg_stmt).scalars().all()

        messages: list[MessageView] = []
        for row in rows:
            parsed_citations: list[Citation] = []
            if row.citations_json:
                try:
                    parsed_citations = [Citation(**item) for item in json.loads(row.citations_json)]
                except Exception:
                    parsed_citations = []
            messages.append(
                MessageView(
                    id=row.id,
                    role=row.role,
                    content=row.content,
                    created_at=row.created_at,
                    citations=parsed_citations,
                )
            )

        return ConversationDetail(
            id=conv.id,
            document_id=conv.document_id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            messages=messages,
        )


def _resolve_conversation(document_id: str, question: str, conversation_id: str | None) -> str:
    with get_session() as session:
        if conversation_id:
            conv = session.get(Conversation, conversation_id)
            if conv is None:
                raise FileNotFoundError(f"Conversation not found: {conversation_id}")
            return conv.id

        conv = Conversation(document_id=document_id, title=_conversation_title(question) or "New Chat")
        session.add(conv)
        session.flush()
        return conv.id


def _append_message(conversation_id: str, role: str, content: str) -> None:
    with get_session() as session:
        conv = session.get(Conversation, conversation_id)
        if conv is None:
            raise FileNotFoundError(f"Conversation not found: {conversation_id}")

        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            citations_json=None,
        )
        conv.updated_at = datetime.utcnow()
        session.add(msg)


def _append_message_with_citations(
    conversation_id: str,
    role: str,
    content: str,
    citations: list[Citation] | None,
) -> None:
    with get_session() as session:
        conv = session.get(Conversation, conversation_id)
        if conv is None:
            raise FileNotFoundError(f"Conversation not found: {conversation_id}")

        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            citations_json=(json.dumps([item.model_dump() for item in citations]) if citations else None),
        )
        conv.updated_at = datetime.utcnow()
        session.add(msg)


def _normalize_sentences(text: str) -> list[str]:
    parts = [chunk.strip() for chunk in re.split(r"(?<=[.!?])\s+", text) if chunk.strip()]
    if parts:
        return parts
    return [text.strip()] if text.strip() else []


def _format_output(answer: str, output_mode: str) -> str:
    sentences = _normalize_sentences(answer)
    if output_mode == "bullet_points":
        if not sentences:
            return "- No content generated"
        return "\n".join(f"- {line}" for line in sentences[:8])

    if output_mode == "executive_brief":
        lead = sentences[0] if sentences else "No summary available."
        actions = sentences[1:4] if len(sentences) > 1 else ["Review document-specific findings."]
        return (
            f"Executive Summary\n\n{lead}\n\n"
            "Key Actions\n"
            + "\n".join(f"- {item}" for item in actions)
        )

    if output_mode == "table":
        rows = sentences[:6] if sentences else ["No content generated"]
        table_lines = ["| # | Insight |", "|---|---|"]
        for idx, row in enumerate(rows, start=1):
            sanitized = row.replace("|", "\\|")
            table_lines.append(f"| {idx} | {sanitized} |")
        return "\n".join(table_lines)

    if output_mode == "json":
        payload = {
            "summary": sentences[0] if sentences else "",
            "highlights": sentences[1:6],
            "confidence": "medium",
        }
        return json.dumps(payload, indent=2)

    return answer


def _extract_citations_from_nodes(source_nodes) -> list[Citation]:
    citations: list[Citation] = []
    for node in source_nodes[:6]:
        text = ""
        metadata = {}
        score = 0.0
        try:
            text = (node.get_content() or "").strip()
            metadata = getattr(node, "metadata", {}) or {}
            score = float(getattr(node, "score", 0.0) or 0.0)
        except Exception:
            text = ""
            metadata = {}
            score = 0.0

        citations.append(
            Citation(
                source=str(metadata.get("filename") or metadata.get("source") or "document"),
                score=round(score, 4),
                excerpt=(text[:280] if text else "No excerpt available"),
                page=(int(metadata.get("page")) if metadata.get("page") else None),
            )
        )
    return citations


def _verify_answer(question: str, answer: str, citations: list[Citation]) -> dict:
    answer_tokens = {
        token.lower()
        for token in re.findall(r"[A-Za-z]{4,}", answer)
        if token and token.lower() not in {"this", "that", "with", "from", "have", "will"}
    }
    support_text = " ".join(item.excerpt for item in citations).lower()
    if not answer_tokens:
        score = 0.0
    else:
        matched = sum(1 for token in answer_tokens if token in support_text)
        score = matched / len(answer_tokens)

    status = "low"
    if score >= 0.7:
        status = "high"
    elif score >= 0.4:
        status = "medium"

    return {
        "status": status,
        "score": round(score, 3),
        "checks": [
            "source_coverage",
            "claim_overlap",
            "citation_presence",
        ],
        "supporting_sources": [item.source for item in citations[:3]],
        "question": question,
    }


def _extract_entities(text: str) -> list[str]:
    candidates = re.findall(r"\b[A-Z][a-zA-Z]{2,}\b", text)
    cleaned: list[str] = []
    for item in candidates:
        normalized = item.strip()
        if normalized and normalized not in cleaned:
            cleaned.append(normalized)
    return cleaned[:20]


def _update_workspace_memory_graph(workspace_id: str, question: str, answer: str) -> None:
    entities = _extract_entities(f"{question} {answer}")
    if len(entities) < 2:
        return

    with get_session() as session:
        label_to_id: dict[str, str] = {}
        for label in entities:
            existing = (
                session.execute(
                    select(MemoryNode).where(MemoryNode.workspace_id == workspace_id, MemoryNode.label == label)
                )
                .scalars()
                .first()
            )
            if existing is None:
                node = MemoryNode(
                    workspace_id=workspace_id,
                    label=label,
                    node_type="entity",
                    attributes_json=json.dumps({"first_seen": datetime.utcnow().isoformat()}),
                )
                session.add(node)
                session.flush()
                label_to_id[label] = node.id
            else:
                label_to_id[label] = existing.id

        for idx in range(len(entities) - 1):
            source_id = label_to_id[entities[idx]]
            target_id = label_to_id[entities[idx + 1]]
            if source_id == target_id:
                continue

            existing_edge = (
                session.execute(
                    select(MemoryEdge).where(
                        MemoryEdge.workspace_id == workspace_id,
                        MemoryEdge.source_node_id == source_id,
                        MemoryEdge.target_node_id == target_id,
                        MemoryEdge.relation == "co_occurs",
                    )
                )
                .scalars()
                .first()
            )
            if existing_edge is None:
                session.add(
                    MemoryEdge(
                        workspace_id=workspace_id,
                        source_node_id=source_id,
                        target_node_id=target_id,
                        relation="co_occurs",
                        weight=1.0,
                    )
                )
            else:
                existing_edge.weight = float(existing_edge.weight) + 1.0


def _log_evaluation(
    document_id: str,
    question: str,
    retrieval_mode: str,
    output_mode: str,
    workspace_id: str | None,
    conversation_id: str | None,
    verification_score: float,
    latency_ms: float,
    success: bool,
    error_message: str | None = None,
) -> None:
    with get_session() as session:
        session.add(
            QueryEvaluation(
                workspace_id=workspace_id,
                conversation_id=conversation_id,
                document_id=document_id,
                question=question,
                retrieval_mode=retrieval_mode,
                output_mode=output_mode,
                verification_score=verification_score,
                latency_ms=latency_ms,
                success=success,
                error_message=error_message,
            )
        )


def _query_with_mode(query_engine, question: str, retrieval_mode: str) -> tuple[str, list, list[str]]:
    source_nodes = []
    retrieval_trace: list[str] = []

    if retrieval_mode == "decompose":
        sub_questions = [
            chunk.strip() for chunk in re.split(r"\band\b|\?|;", question, flags=re.IGNORECASE) if chunk.strip()
        ]
        if not sub_questions:
            sub_questions = [question]
        answers: list[str] = []
        for idx, item in enumerate(sub_questions, start=1):
            response = query_engine.query(item)
            answers.append(f"Part {idx}: {response.response}")
            source_nodes.extend(getattr(response, "source_nodes", []) or [])
            retrieval_trace.append(f"decompose:{item}")
        return "\n".join(answers), source_nodes, retrieval_trace

    if retrieval_mode == "hybrid":
        primary = query_engine.query(question)
        breadth = query_engine.query(f"Provide broader supporting context for: {question}")
        source_nodes.extend(getattr(primary, "source_nodes", []) or [])
        source_nodes.extend(getattr(breadth, "source_nodes", []) or [])
        retrieval_trace.extend(["hybrid:primary", "hybrid:breadth"])
        return f"{primary.response}\n\nAdditional Context:\n{breadth.response}", source_nodes, retrieval_trace

    if retrieval_mode == "rerank":
        response = query_engine.query(question)
        nodes = list(getattr(response, "source_nodes", []) or [])
        nodes.sort(key=lambda n: float(getattr(n, "score", 0.0) or 0.0), reverse=True)
        retrieval_trace.append("rerank:score_desc")
        return response.response, nodes, retrieval_trace

    response = query_engine.query(question)
    retrieval_trace.append("standard:single_pass")
    return response.response, list(getattr(response, "source_nodes", []) or []), retrieval_trace


def answer_question(
    document_id: str,
    question: str,
    conversation_id: str | None = None,
    workspace_id: str | None = None,
    retrieval_mode: str = "hybrid",
    output_mode: str = "standard",
    verification_required: bool = True,
    top_k: int | None = None,
) -> QueryResponse:
    started_at = time.perf_counter()
    resolved_conversation_id: str | None = None
    try:
        query_engine = load_query_engine(_document_storage_dir(document_id), top_k=top_k)

        raw_answer, source_nodes, retrieval_trace = _query_with_mode(
            query_engine=query_engine,
            question=question,
            retrieval_mode=retrieval_mode,
        )

        citations = _extract_citations_from_nodes(source_nodes)
        formatted_answer = _format_output(raw_answer, output_mode=output_mode)
        verification = _verify_answer(question=question, answer=formatted_answer, citations=citations)

        resolved_conversation_id = _resolve_conversation(
            document_id=document_id,
            question=question,
            conversation_id=conversation_id,
        )
        _append_message(conversation_id=resolved_conversation_id, role="user", content=question)
        _append_message_with_citations(
            conversation_id=resolved_conversation_id,
            role="assistant",
            content=formatted_answer,
            citations=citations,
        )

        if workspace_id:
            _update_workspace_memory_graph(workspace_id=workspace_id, question=question, answer=formatted_answer)

        elapsed_ms = (time.perf_counter() - started_at) * 1000.0
        _log_evaluation(
            document_id=document_id,
            question=question,
            retrieval_mode=retrieval_mode,
            output_mode=output_mode,
            workspace_id=workspace_id,
            conversation_id=resolved_conversation_id,
            verification_score=float(verification.get("score", 0.0)),
            latency_ms=elapsed_ms,
            success=True,
        )

        return QueryResponse(
            answer=formatted_answer,
            document_id=document_id,
            conversation_id=resolved_conversation_id,
            citations=citations,
            output_mode=output_mode,
            verification=(verification if verification_required else None),
            retrieval_trace=retrieval_trace,
        )
    except Exception as ex:
        elapsed_ms = (time.perf_counter() - started_at) * 1000.0
        _log_evaluation(
            document_id=document_id,
            question=question,
            retrieval_mode=retrieval_mode,
            output_mode=output_mode,
            workspace_id=workspace_id,
            conversation_id=resolved_conversation_id,
            verification_score=0.0,
            latency_ms=elapsed_ms,
            success=False,
            error_message=str(ex),
        )
        raise


def get_workspace_graph(workspace_id: str, owner_username: str) -> WorkspaceGraphResponse:
    with get_session() as session:
        _workspace_for_owner(session=session, workspace_id=workspace_id, owner_username=owner_username)
        nodes = (
            session.execute(select(MemoryNode).where(MemoryNode.workspace_id == workspace_id))
            .scalars()
            .all()
        )
        edges = (
            session.execute(select(MemoryEdge).where(MemoryEdge.workspace_id == workspace_id))
            .scalars()
            .all()
        )

        node_views = [
            MemoryNodeView(
                id=node.id,
                label=node.label,
                node_type=node.node_type,
                attributes=(json.loads(node.attributes_json) if node.attributes_json else None),
            )
            for node in nodes
        ]
        edge_views = [
            MemoryEdgeView(
                id=edge.id,
                source_node_id=edge.source_node_id,
                target_node_id=edge.target_node_id,
                relation=edge.relation,
                weight=float(edge.weight),
            )
            for edge in edges
        ]
        return WorkspaceGraphResponse(workspace_id=workspace_id, nodes=node_views, edges=edge_views)


def create_query_automation(payload: QueryAutomationCreateRequest, owner_username: str) -> QueryAutomationResponse:
    with get_session() as session:
        _workspace_for_owner(session=session, workspace_id=payload.workspace_id, owner_username=owner_username)
        automation = QueryAutomation(
            workspace_id=payload.workspace_id,
            name=payload.name.strip(),
            document_id=payload.document_id,
            prompt=payload.prompt,
            retrieval_mode=payload.retrieval_mode,
            output_mode=payload.output_mode,
            verification_required=payload.verification_required,
            schedule_cron=payload.schedule_cron,
            is_active=True,
        )
        session.add(automation)
        session.flush()
        return QueryAutomationResponse(
            id=automation.id,
            workspace_id=automation.workspace_id,
            name=automation.name,
            document_id=automation.document_id,
            prompt=automation.prompt,
            retrieval_mode=automation.retrieval_mode,
            output_mode=automation.output_mode,
            verification_required=automation.verification_required,
            schedule_cron=automation.schedule_cron,
            is_active=automation.is_active,
            last_run_at=automation.last_run_at,
            created_at=automation.created_at,
            updated_at=automation.updated_at,
        )


def list_query_automations(workspace_id: str, owner_username: str) -> list[QueryAutomationResponse]:
    with get_session() as session:
        _workspace_for_owner(session=session, workspace_id=workspace_id, owner_username=owner_username)
        rows = (
            session.execute(
                select(QueryAutomation)
                .where(QueryAutomation.workspace_id == workspace_id)
                .order_by(QueryAutomation.updated_at.desc())
            )
            .scalars()
            .all()
        )
        return [
            QueryAutomationResponse(
                id=row.id,
                workspace_id=row.workspace_id,
                name=row.name,
                document_id=row.document_id,
                prompt=row.prompt,
                retrieval_mode=row.retrieval_mode,
                output_mode=row.output_mode,
                verification_required=row.verification_required,
                schedule_cron=row.schedule_cron,
                is_active=row.is_active,
                last_run_at=row.last_run_at,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]


def run_query_automation(automation_id: str, owner_username: str) -> QueryAutomationRunResponse:
    with get_session() as session:
        automation = session.get(QueryAutomation, automation_id)
        if automation is None:
            raise FileNotFoundError(f"Automation not found: {automation_id}")
        _workspace_for_owner(session=session, workspace_id=automation.workspace_id, owner_username=owner_username)

    result = answer_question(
        document_id=automation.document_id,
        question=automation.prompt,
        workspace_id=automation.workspace_id,
        retrieval_mode=automation.retrieval_mode,
        output_mode=automation.output_mode,
        verification_required=automation.verification_required,
    )

    with get_session() as session:
        row = session.get(QueryAutomation, automation_id)
        if row is not None:
            row.last_run_at = datetime.utcnow()
            row.updated_at = datetime.utcnow()

    _record_webhook_event(
        event_type="automation.run.completed",
        payload={
            "automation_id": automation_id,
            "workspace_id": automation.workspace_id,
            "document_id": automation.document_id,
        },
    )

    return QueryAutomationRunResponse(
        automation_id=automation_id,
        run_at=datetime.now(timezone.utc),
        result=result,
    )


def get_evaluation_summary(workspace_id: str | None = None) -> EvaluationSummaryResponse:
    with get_session() as session:
        stmt = select(QueryEvaluation)
        if workspace_id:
            stmt = stmt.where(QueryEvaluation.workspace_id == workspace_id)
        rows = session.execute(stmt).scalars().all()

    if not rows:
        return EvaluationSummaryResponse(
            total_queries=0,
            success_rate=0.0,
            average_latency_ms=0.0,
            average_verification_score=0.0,
            by_retrieval_mode={},
        )

    total = len(rows)
    success_count = sum(1 for row in rows if row.success)
    avg_latency = sum(float(row.latency_ms) for row in rows) / total
    avg_verification = sum(float(row.verification_score) for row in rows) / total
    by_mode: dict[str, int] = {}
    for row in rows:
        by_mode[row.retrieval_mode] = by_mode.get(row.retrieval_mode, 0) + 1

    return EvaluationSummaryResponse(
        total_queries=total,
        success_rate=round(success_count / total, 3),
        average_latency_ms=round(avg_latency, 2),
        average_verification_score=round(avg_verification, 3),
        by_retrieval_mode=by_mode,
    )


def _hash_api_key(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def create_api_key(owner_username: str, name: str) -> ApiKeyCreateResponse:
    raw = f"dqk_{secrets.token_hex(20)}"
    prefix = raw[:12]
    with get_session() as session:
        row = ApiKey(
            owner_username=owner_username,
            name=name.strip(),
            key_hash=_hash_api_key(raw),
            key_prefix=prefix,
            is_active=True,
        )
        session.add(row)
        session.flush()
        return ApiKeyCreateResponse(
            id=row.id,
            name=row.name,
            api_key=raw,
            key_prefix=row.key_prefix,
            created_at=row.created_at,
        )


def list_api_keys(owner_username: str) -> list[ApiKeyResponse]:
    with get_session() as session:
        rows = (
            session.execute(
                select(ApiKey)
                .where(ApiKey.owner_username == owner_username)
                .order_by(ApiKey.created_at.desc())
            )
            .scalars()
            .all()
        )
        return [
            ApiKeyResponse(
                id=row.id,
                name=row.name,
                key_prefix=row.key_prefix,
                is_active=row.is_active,
                created_at=row.created_at,
                last_used_at=row.last_used_at,
            )
            for row in rows
        ]


def _record_webhook_event(event_type: str, payload: dict) -> None:
    with get_session() as session:
        session.add(
            WebhookEvent(
                event_type=event_type,
                payload_json=json.dumps(payload),
                status="queued",
            )
        )
