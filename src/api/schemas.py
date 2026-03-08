from pydantic import BaseModel, Field, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)

class SessionResponse(BaseModel):
    id: int
    title: str
    folder_name: Optional[str] = None
    tags: List[str] = []
    messages: List[ChatMessageModel] = []
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

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
    
    # --- Multi-LLM BYOK ---
    openai_api_key: Optional[str] = ""
    anthropic_api_key: Optional[str] = ""
    gemini_api_key: Optional[str] = ""
    custom_ollama_url: Optional[str] = ""
    
    # --- Global Workspace Architecture ---
    default_intake_vault: Optional[str] = ""
    workspaces: Optional[List[str]] = Field(default_factory=list)
    
    # --- Local-First Agnosticism ---
    remote_integration_enabled: bool = Field(True, description="Habilita ou desabilita conexões com o nó da Oracle e APIs externas")

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
    
    # --- Multi-LLM BYOK ---
    openai_api_key: Optional[str] = ""
    anthropic_api_key: Optional[str] = ""
    gemini_api_key: Optional[str] = ""
    custom_ollama_url: Optional[str] = ""
    
    # --- Global Workspace Architecture ---
    default_intake_vault: Optional[str] = ""
    workspaces: Optional[List[str]] = Field(default_factory=list)
    
    # --- Local-First Agnosticism ---
    remote_integration_enabled: bool = True

# --- THE GOD MODE COCKPIT ---

class ProjectLinkSchema(BaseModel):
    id: Optional[int] = None
    url: str
    label: str

    model_config = ConfigDict(from_attributes=True)

class ProjectLogSchema(BaseModel):
    id: Optional[int] = None
    content: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ProjectCreateRequest(BaseModel):
    name: str = Field(..., description="Nome do projeto abstrato ou real")
    purpose: Optional[str] = Field(None, description="Definição de Concluído / O Por Quê")
    traction_status: Optional[str] = Field("Ideation", description="Ideation, Flowing, Blocked, Hibernating, Done")
    next_action: Optional[str] = Field(None, description="A single tangible micro-step")
    energy_level: Optional[str] = Field("Med", description="High, Med, Low")
    progress_percent: Optional[int] = Field(0)
    friction_radar: Optional[str] = Field(None, description="Explanation if Blocked")
    deadline: Optional[str] = Field(None)
    links: Optional[List[ProjectLinkSchema]] = Field(default_factory=list)

class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = None
    purpose: Optional[str] = None
    traction_status: Optional[str] = None
    next_action: Optional[str] = None
    energy_level: Optional[str] = None
    progress_percent: Optional[int] = None
    friction_radar: Optional[str] = None
    deadline: Optional[str] = None
    links: Optional[List[ProjectLinkSchema]] = None

class ProjectResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    purpose: Optional[str] = None
    traction_status: str
    next_action: Optional[str] = None
    energy_level: str
    progress_percent: int
    friction_radar: Optional[str] = None
    deadline: Optional[str] = None
    file_path: Optional[str] = None
    last_synced_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    links: List[ProjectLinkSchema] = []
    logs: List[ProjectLogSchema] = []

    model_config = ConfigDict(from_attributes=True)

class TaskCreateRequest(BaseModel):
    title: str = Field(..., description="O título prático da Tarefa")
    description: Optional[str] = None
    status: Optional[str] = "TODO"
    priority: Optional[str] = "Medium"
    deadline: Optional[str] = None

class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    order_index: Optional[int] = None
    deadline: Optional[str] = None

class TaskResponse(BaseModel):
    id: str
    project_id: str
    tenant_id: str
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    order_index: int
    deadline: Optional[str] = None
    file_path: Optional[str] = None
    last_synced_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class NoteCreateRequest(BaseModel):
    title: str
    content: Optional[str] = None
    is_pinned: Optional[bool] = False
    tags: Optional[List[str]] = Field(default_factory=list)

class NoteUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_pinned: Optional[bool] = None
    tags: Optional[List[str]] = None

class NoteResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    tenant_id: str
    title: str
    content: Optional[str] = None
    is_pinned: bool
    tags: List[str] = []
    file_path: Optional[str] = None
    last_synced_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ActivityLogResponse(BaseModel):
    id: int
    tenant_id: str
    agent_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- OPENAI COMPATIBLE ENDPOINT (OpenCode / Cursor / Cline Proxy) ---

class OpenAIChatMessage(BaseModel):
    role: str
    content: str
    name: Optional[str] = None

class OpenAIChatRequest(BaseModel):
    model: str
    messages: List[OpenAIChatMessage]
    temperature: Optional[float] = 0.5
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Any] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    user: Optional[str] = None

class OpenAIChatChoiceMessage(BaseModel):
    role: str
    content: str
    
class OpenAIChatChoice(BaseModel):
    index: int
    message: OpenAIChatChoiceMessage
    finish_reason: Optional[str] = None

class OpenAITokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class OpenAIChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[OpenAIChatChoice]
    usage: Optional[OpenAITokenUsage] = None

# --- SSE Stream Chunk Models ---

class OpenAIChatChunkDelta(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None

class OpenAIChatChunkChoice(BaseModel):
    index: int
    delta: OpenAIChatChunkDelta
    finish_reason: Optional[str] = None

class OpenAIChatChunkResponse(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[OpenAIChatChunkChoice]
