from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str = Field(..., description="A mensagem ou pergunta enviada pelo usuário")
    stream: bool = Field(True, description="Se deseja que a resposta seja em streaming usando Server-Sent Events (SSE)")

class Citation(BaseModel):
    source: str = Field(..., description="O caminho ou URL da fonte")
    
class ChatResponse(BaseModel):
    response: str
    sources: List[Citation] = []
