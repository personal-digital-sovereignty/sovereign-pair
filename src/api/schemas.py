from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class SensusDocument(BaseModel):
    id: UUID
    tenant_id: str
    file_path: str
    content: str
    
    # Deterministic Extraction (The Mom)
    frontmatter: Dict[str, Any] = Field(default_factory=dict)
    extracted_todos: List[str] = Field(default_factory=list)
    extracted_tags: List[str] = Field(default_factory=list)
    extracted_links: List[str] = Field(default_factory=list)
    
    # Semantic Extraction (The Dad)
    vector_id: Optional[str] = None
    semantic_summary: Optional[str] = None

class DocumentUpdateRequest(BaseModel):
    content: str = Field(..., description="Novo conteúdo Markdown raw")

class ChatRequest(BaseModel):
    message: str = Field(..., description="A mensagem ou pergunta enviada pelo usuário")
    stream: bool = Field(True, description="Se deseja que a resposta seja em streaming usando Server-Sent Events (SSE)")
    active_document: Optional[str] = Field(None, description="Opcional: O conteúdo do documento que o usuário está visualizando no momento")
    session_id: Optional[int] = Field(None, description="Opcional: ID da sessão SQLite para vincular a conversa a um histórico existente")
    provider: Optional[str] = Field(None, description="Opcional: ID do provedor na Nuvem (openai, anthropic, ollama, groq)")
    model: Optional[str] = Field(None, description="Opcional: Nome do modelo do LLM a ser invocado na Nuvem")

class Citation(BaseModel):
    source: str = Field(..., description="O caminho ou URL da fonte")
    
class ChatResponse(BaseModel):
    response: str
    sources: List[Citation] = []

class FeedbackRequest(BaseModel):
    message_id: int = Field(..., description="ID da mensagem da IA a ser avaliada")
    thumbs_up: bool = Field(False)
    thumbs_down: bool = Field(False)
    feedback_text: Optional[str] = Field(None)

class ChatMessageModel(BaseModel):
    id: int
    role: str
    content: str
    thumbs_up: bool
    thumbs_down: bool

    class Config:
        from_attributes = True

class SessionResponse(BaseModel):
    id: int
    title: str
    folder_name: Optional[str] = None
    tags: List[str] = []
    messages: List[ChatMessageModel] = []
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SessionUpdateRequest(BaseModel):
    title: Optional[str] = None
    folder_name: Optional[str] = None
    tags: Optional[List[str]] = None

class UploadResponse(BaseModel):
    status: str
    message: str
    file_path: Optional[str] = None
    sha256: Optional[str] = None
    require_action: Optional[str] = None

class SettingsRequest(BaseModel):
    llm_provider: str
    llm_model: str
    temperature: float
    system_prompt: str
    theme: str = "dark"
    persona: str = "default"
    formality: str = "neutral"
    ai_name: Optional[str] = ""
    nickname: Optional[str] = ""
    occupation: Optional[str] = ""
    about_user: Optional[str] = ""
    language: Optional[str] = "Português (BR)"
    geolocation: Optional[str] = ""

class SettingsResponse(BaseModel):
    llm_provider: str
    llm_model: str
    temperature: float
    system_prompt: str
    theme: str = "dark"
    persona: str = "default"
    formality: str = "neutral"
    ai_name: Optional[str] = ""
    nickname: Optional[str] = ""
    occupation: Optional[str] = ""
    about_user: Optional[str] = ""
    language: Optional[str] = "Português (BR)"
    geolocation: Optional[str] = ""
