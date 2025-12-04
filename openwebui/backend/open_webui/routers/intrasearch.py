"""
IntraSearch API Router - AI-Powered Enterprise Search
Handles enterprise internal search with AI integration using OpenAI
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import os
import json
from dotenv import load_dotenv

from open_webui.utils.auth import get_verified_user
from open_webui.integrations.google_drive import google_drive

load_dotenv()

router = APIRouter()

# ========================================
# OpenAI Configuration
# ========================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "") 
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # (gpt-4o-mini, gpt-4o, etc)
# ========================================

# Pydantic models for IntraSearch
class SearchRequest(BaseModel):
    query: str
    sources: Optional[List[str]] = None
    max_results: Optional[int] = 10
    search_depth: Optional[str] = "detailed"  # basic, detailed, comprehensive
    include_attachments: Optional[bool] = True
    language: Optional[str] = "auto"
    stream: Optional[bool] = False

class SearchResult(BaseModel):
    id: str
    title: str
    content: str
    source: str
    score: float
    metadata: Dict[str, Any] = {}

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    search_time_ms: int
    suggestions: Optional[List[str]] = None

class IntraSearchMessage(BaseModel):
    id: Optional[str] = None
    role: str  # user, assistant, system
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class IntraSearchSession(BaseModel):
    id: str
    title: str
    messages: List[IntraSearchMessage] = []
    created_at: datetime
    updated_at: datetime

class IntraSearchSettings(BaseModel):
    search_depth: str = "detailed"
    search_sources: List[str] = ["documents", "wiki", "knowledge_base"]
    max_results: int = 10
    include_attachments: bool = True
    language: str = "auto"

# Mock data for development
MOCK_SEARCH_RESULTS = [
    SearchResult(
        id="doc_001",
        title="Corporate Security Policy",
        content="This document describes the core principles of the company's information security, including rules for handling confidential information, password requirements, and system access procedures.",
        source="Corporate Wiki",
        score=0.95,
        metadata={
            "document_type": "policy",
            "author": "Security Team",
            "created_at": "2024-01-15",
            "tags": ["security", "policy", "compliance"]
        }
    ),
    SearchResult(
        id="kb_002",
        title="CRM System User Guide",
        content="Comprehensive guide for using the corporate CRM system, including customer creation, deal management, report configuration, and integration with other systems.",
        source="Knowledge Base",
        score=0.88,
        metadata={
            "document_type": "manual",
            "author": "IT Department",
            "created_at": "2024-02-10",
            "tags": ["crm", "manual", "sales"]
        }
    ),
    SearchResult(
        id="db_003",
        title="Department Contact Directory",
        content="Database containing contact information for all company departments, including phone numbers, email addresses, office locations, and responsible personnel.",
        source="Employee Database",
        score=0.82,
        metadata={
            "document_type": "directory",
            "author": "HR Department",
            "created_at": "2024-03-01",
            "tags": ["contacts", "directory", "hr"]
        }
    )
]

# In-memory storage for demo
sessions_storage: Dict[str, IntraSearchSession] = {}
user_settings: Dict[str, IntraSearchSettings] = {}


async def generate_ai_response_stream(prompt: str, model: str = None):
    """Generate streaming AI response using OpenAI"""
    import httpx

    if model is None:
        model = OPENAI_MODEL

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                "https://api.openai.com/v1/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": True
                },
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {OPENAI_API_KEY}"
                }
            ) as response:
                if response.status_code == 200:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data.strip() == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue
                else:
                    yield f"Error: Unable to generate AI response (status {response.status_code})"
    except Exception as e:
        yield f"Error generating AI response: {str(e)}"


@router.post("/search")
async def perform_search(
    request: SearchRequest,
    user=Depends(get_verified_user)
):
    """Perform AI-powered enterprise search using Google Drive"""

    import time
    start_time = time.time()

    # Handle streaming response
    if request.stream:
        return StreamingResponse(
            perform_search_stream(request, user, start_time),
            media_type="text/event-stream"
        )

    # Non-streaming response
    return await perform_search_sync(request, user, start_time)


async def perform_search_sync(request: SearchRequest, user, start_time: float):
    """Synchronous search with AI response"""
    try:
        # 1. Search files in Google Drive
        files = await google_drive.search_files(
            user_id=user.id,
            query=request.query,
            file_types=None,
            limit=min(request.max_results or 10, 10),
            include_content=False
        )

        if not files:
            return await perform_mock_search(request, start_time)

        # 2. Get content from top files
        file_contents = []
        for idx, file in enumerate(files[:5]):
            try:
                content = await google_drive.get_file_content(
                    user_id=user.id,
                    file_id=file.id,
                    max_size=5*1024*1024
                )

                if content and content.strip():
                    file_contents.append({
                        "file_name": file.name,
                        "file_url": file.web_view_link if hasattr(file, 'web_view_link') else "",
                        "file_id": file.id,
                        "content": content[:3000]
                    })
            except Exception as e:
                print(f"Failed to get content for file {file.id}: {e}")
                continue

        if not file_contents:
            results = []
            for idx, file in enumerate(files):
                results.append(SearchResult(
                    id=file.id,
                    title=file.name,
                    content=f"File: {file.name} ({file.mime_type})",
                    source="Google Drive",
                    score=1.0 - (idx * 0.05),
                    metadata={
                        "document_type": file.mime_type,
                        "url": file.web_view_link if hasattr(file, 'web_view_link') else "",
                    }
                ))

            search_time = int((time.time() - start_time) * 1000)
            return SearchResponse(
                query=request.query,
                results=results,
                total_results=len(results),
                search_time_ms=search_time,
                suggestions=[]
            )

        # 3. Create AI prompt
        context_parts = []
        for fc in file_contents:
            context_parts.append(f"**File: {fc['file_name']}**\n{fc['content']}\n---")

        context = "\n\n".join(context_parts)

        prompt = f"""You are an intelligent assistant helping answer questions based on documents from Google Drive.

Question: {request.query}

Here are the relevant documents:

{context}

Please provide a clear, comprehensive answer to the question based on the information in these documents. If the documents don't contain enough information to answer the question, say so clearly."""

        # 4. Call OpenAI LLM
        try:
            import httpx

            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    json={
                        "model": OPENAI_MODEL,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False
                    },
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {OPENAI_API_KEY}"
                    }
                )

                if response.status_code == 200:
                    ai_response = response.json()
                    ai_answer = ai_response["choices"][0]["message"]["content"]
                else:
                    ai_answer = f"Unable to generate AI answer (status {response.status_code})"

        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            ai_answer = f"Error generating AI response: {str(e)}"

        # 5. Build results
        results = [
            SearchResult(
                id="ai_answer",
                title="🤖 AI Answer",
                content=ai_answer,
                source="AI Analysis",
                score=1.0,
                metadata={
                    "document_type": "ai_generated",
                    "query_type": "agentic_search",
                    "sources_count": len(file_contents)
                }
            )
        ]

        # Add source documents
        for idx, fc in enumerate(file_contents):
            file = next((f for f in files if f.id == fc['file_id']), None)
            if file:
                results.append(SearchResult(
                    id=file.id,
                    title=f"📄 {file.name}",
                    content=fc['content'][:500],
                    source="Google Drive",
                    score=0.95 - (idx * 0.05),
                    metadata={
                        "document_type": file.mime_type,
                        "url": fc['file_url'],
                        "modified_time": file.modified_time if hasattr(file, 'modified_time') else "",
                    }
                ))

        search_time = int((time.time() - start_time) * 1000)

        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            search_time_ms=search_time,
            suggestions=[]
        )

    except ValueError as e:
        print(f"Google Drive not authorized for user {user.id}: {e}")
        return await perform_mock_search(request, start_time)

    except Exception as e:
        print(f"Error in agentic search: {e}")
        import traceback
        traceback.print_exc()
        return await perform_mock_search(request, start_time)


async def perform_search_stream(request: SearchRequest, user, start_time: float):
    """Streaming search response"""
    try:
        # Send initial status
        yield f"data: {json.dumps({'type': 'status', 'message': 'Searching Google Drive...'})}\n\n"

        # 1. Search files
        files = await google_drive.search_files(
            user_id=user.id,
            query=request.query,
            file_types=None,
            limit=min(request.max_results or 10, 10),
            include_content=False
        )

        if not files:
            yield f"data: {json.dumps({'type': 'error', 'message': 'No files found'})}\n\n"
            yield "data: [DONE]\n\n"
            return

        yield f"data: {json.dumps({'type': 'status', 'message': f'Found {len(files)} files, reading content...'})}\n\n"

        # 2. Get content
        file_contents = []
        for idx, file in enumerate(files[:5]):
            try:
                content = await google_drive.get_file_content(
                    user_id=user.id,
                    file_id=file.id,
                    max_size=5*1024*1024
                )

                if content and content.strip():
                    file_contents.append({
                        "file_name": file.name,
                        "file_url": file.web_view_link if hasattr(file, 'web_view_link') else "",
                        "file_id": file.id,
                        "content": content[:3000]
                    })
                    yield f"data: {json.dumps({'type': 'status', 'message': f'Read {file.name}'})}\n\n"
            except Exception as e:
                print(f"Failed to get content for file {file.id}: {e}")
                continue

        if not file_contents:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Could not read file contents'})}\n\n"
            yield "data: [DONE]\n\n"
            return

        yield f"data: {json.dumps({'type': 'status', 'message': 'Generating AI response...'})}\n\n"

        # 3. Create prompt
        context_parts = []
        for fc in file_contents:
            context_parts.append(f"**File: {fc['file_name']}**\n{fc['content']}\n---")

        context = "\n\n".join(context_parts)

        prompt = f"""You are an intelligent assistant helping answer questions based on documents from Google Drive.

Question: {request.query}

Here are the relevant documents:

{context}

Please provide a clear, comprehensive answer to the question based on the information in these documents."""

        # 4. Stream AI response from OpenAI
        yield f"data: {json.dumps({'type': 'ai_start'})}\n\n"

        async for chunk in generate_ai_response_stream(prompt, OPENAI_MODEL):
            yield f"data: {json.dumps({'type': 'ai_chunk', 'content': chunk})}\n\n"

        yield f"data: {json.dumps({'type': 'ai_end'})}\n\n"

        # 5. Send source files
        for fc in file_contents:
            file = next((f for f in files if f.id == fc['file_id']), None)
            if file:
                yield f"data: {json.dumps({'type': 'source', 'file': {'id': file.id, 'name': file.name, 'url': fc['file_url']}})}\n\n"

        search_time = int((time.time() - start_time) * 1000)
        yield f"data: {json.dumps({'type': 'complete', 'search_time_ms': search_time})}\n\n"
        yield "data: [DONE]\n\n"

    except Exception as e:
        print(f"Error in streaming search: {e}")
        import traceback
        traceback.print_exc()
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        yield "data: [DONE]\n\n"


async def perform_mock_search(request: SearchRequest, start_time: float):
    """Fallback mock search implementation"""
    import time

    query_lower = request.query.lower()
    filtered_results = []

    for result in MOCK_SEARCH_RESULTS:
        if (query_lower in result.title.lower() or
            query_lower in result.content.lower() or
            any(query_lower in tag for tag in result.metadata.get("tags", []))):
            filtered_results.append(result)

    limited_results = filtered_results[:request.max_results]

    suggestions = []
    if query_lower:
        base_suggestions = [
            "security policy",
            "crm system guide",
            "department contacts",
            "document workflow",
            "corporate standards",
            "employee handbook",
            "it support portal"
        ]
        suggestions = [s for s in base_suggestions if query_lower not in s.lower()][:3]

    search_time = int((time.time() - start_time) * 1000)

    return SearchResponse(
        query=request.query,
        results=limited_results,
        total_results=len(filtered_results),
        search_time_ms=search_time,
        suggestions=suggestions
    )

@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., description="Search query"),
    user=Depends(get_verified_user)
):
    """Get search suggestions based on query"""

    suggestions = [
        f"{q} policy",
        f"{q} guide",
        f"{q} contacts",
        f"how to {q}",
        f"{q} documents"
    ]

    return {"suggestions": suggestions[:5]}

@router.post("/sessions", response_model=IntraSearchSession)
async def create_session(
    title: Optional[str] = "IntraSearch Session",
    user=Depends(get_verified_user)
):
    """Create new IntraSearch session"""

    session_id = str(uuid.uuid4())
    now = datetime.now()

    session = IntraSearchSession(
        id=session_id,
        title=title or f"IntraSearch Session {now.strftime('%Y-%m-%d %H:%M')}",
        messages=[],
        created_at=now,
        updated_at=now
    )

    sessions_storage[f"{user.id}_{session_id}"] = session
    return session

@router.get("/sessions", response_model=List[IntraSearchSession])
async def get_sessions(user=Depends(get_verified_user)):
    """Get all IntraSearch sessions for user"""

    user_sessions = [
        session for key, session in sessions_storage.items()
        if key.startswith(f"{user.id}_")
    ]

    return sorted(user_sessions, key=lambda x: x.updated_at, reverse=True)

@router.get("/sessions/{session_id}", response_model=IntraSearchSession)
async def get_session(
    session_id: str,
    user=Depends(get_verified_user)
):
    """Get specific IntraSearch session"""

    session_key = f"{user.id}_{session_id}"
    if session_key not in sessions_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return sessions_storage[session_key]

@router.post("/sessions/{session_id}/messages", response_model=IntraSearchMessage)
async def save_message(
    session_id: str,
    message: IntraSearchMessage,
    user=Depends(get_verified_user)
):
    """Save message to IntraSearch session"""

    session_key = f"{user.id}_{session_id}"
    if session_key not in sessions_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    if not message.id:
        message.id = str(uuid.uuid4())
    if not message.timestamp:
        message.timestamp = datetime.now()

    sessions_storage[session_key].messages.append(message)
    sessions_storage[session_key].updated_at = datetime.now()

    return message

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    user=Depends(get_verified_user)
):
    """Delete IntraSearch session"""

    session_key = f"{user.id}_{session_id}"
    if session_key not in sessions_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    del sessions_storage[session_key]
    return {"message": "Session deleted successfully"}

@router.get("/settings", response_model=IntraSearchSettings)
async def get_settings(user=Depends(get_verified_user)):
    """Get IntraSearch settings for user"""

    return user_settings.get(user.id, IntraSearchSettings())

@router.put("/settings")
async def update_settings(
    settings: IntraSearchSettings,
    user=Depends(get_verified_user)
):
    """Update IntraSearch settings for user"""

    user_settings[user.id] = settings
    return {"message": "Settings updated successfully"}

@router.get("/sources")
async def get_search_sources(user=Depends(get_verified_user)):
    """Get available search sources"""

    sources = [
        "documents",
        "wiki",
        "knowledge_base",
        "databases",
        "repositories",
        "email_archives",
        "project_files",
        "policies"
    ]

    return {"sources": sources}
