from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str = Field(..., description="A mensagem ou pergunta enviada pelo usuário")
    stream: bool = Field(True, description="Se deseja que a resposta seja em streaming usando Server-Sent Events (SSE)")
    active_document: Optional[str] = Field(None, description="Opcional: O conteúdo do documento que o usuário está visualizando no momento")
    session_id: Optional[int] = Field(None, description="Opcional: ID da sessão SQLite para vincular a conversa a um histórico existente")

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
    messages: List[ChatMessageModel] = []
    
    class Config:
        from_attributes = True
