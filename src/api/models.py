from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship, synonym
from datetime import datetime, timezone
from .database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), default="Nova Conversa")
    folder_name = Column(String(100), nullable=True, default=None)
    tags = Column(JSON, default=list)
    tenant_id = Column(String(50), nullable=False, index=True, default="default")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relacionamento 1:N com as mensagens
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(String(50), nullable=False, index=True, default="default")
    
    role = Column(String(50), nullable=False) # 'user' ou 'assistant' ou 'system'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Sistema de Feedback do Usuário para Fine-Tuning futuro
    thumbs_up = Column(Boolean, default=False)
    thumbs_down = Column(Boolean, default=False)
    feedback_text = Column(Text, nullable=True) # Ex: O usuário corrigindo a IA dizendo "Você mentiu sobre X"

    session = relationship("ChatSession", back_populates="messages")

class DocumentCache(Base):
    __tablename__ = "document_cache"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(1024), nullable=False, unique=True)
    sha256 = Column(String(64), nullable=False, index=True)
    file_size = Column(Integer, nullable=False) # em bytes
    tenant_id = Column(String(50), nullable=False, index=True, default="default")
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class SensusDocumentModel(Base):
    __tablename__ = "sensus_documents"

    id = Column(String(36), primary_key=True, index=True) # UUID
    tenant_id = Column(String(50), nullable=False, index=True, default="default")
    file_path = Column(String(1024), nullable=False, unique=True, index=True)
    
    # Deterministic Data (The Mom)
    frontmatter = Column(JSON, default=dict)
    extracted_todos = Column(JSON, default=list)
    extracted_tags = Column(JSON, default=list)
    extracted_links = Column(JSON, default=list)
    
    # Semantic Data (The Dad)
    vector_id = Column(String(100), nullable=True) # ID no Chroma
    semantic_summary = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), nullable=False, index=True) # REMOVED UNIQUE=True
    _setting_value = Column("setting_value", Text, nullable=True)
    tenant_id = Column(String(50), nullable=False, index=True, default="default")
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @property
    def setting_value(self):
        if self._setting_value is None:
            return None
        k = self.setting_key.upper() if self.setting_key else ""
        if "API_KEY" in k or "TOKEN" in k:
            from src.core.security import decrypt_value
            return decrypt_value(self._setting_value)
        return self._setting_value

    @setting_value.setter
    def setting_value(self, val):
        if val is None:
            self._setting_value = None
            return
        k = self.setting_key.upper() if self.setting_key else ""
        if "API_KEY" in k or "TOKEN" in k:
            from src.core.security import encrypt_value
            self._setting_value = encrypt_value(val)
        else:
            self._setting_value = val

    setting_value = synonym("_setting_value", descriptor=setting_value)

class QuarantineLog(Base):
    __tablename__ = "quarantine_logs"

    id = Column(Integer, primary_key=True, index=True)
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False, index=True, default="default")
    file_path = Column(String(1024), nullable=False)
    file_name = Column(String(255), nullable=False)
    reason = Column(String(255), nullable=False)
    ai_confidence = Column(String(50), nullable=True)
    content_snippet = Column(Text, nullable=True)
    status = Column(String(50), default="QUARANTINED") # QUARANTINED, RELEASED, DELETED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

# --- THE GOD MODE COCKPIT ---

class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, index=True) # UUID
    tenant_id = Column(String(50), nullable=False, index=True, default="default")
    name = Column(String(255), nullable=False)
    purpose = Column(Text, nullable=True) # Definition of Done / "Why?"
    traction_status = Column(String(50), default="Ideation") # Ideation, Flowing, Blocked, Hibernating, Done
    next_action = Column(Text, nullable=True) # The single next micro-step
    energy_level = Column(String(20), default="Med") # High, Med, Low
    progress_percent = Column(Integer, default=0)
    friction_radar = Column(Text, nullable=True) # Why is it blocked?
    deadline = Column(String(100), nullable=True) # ISO Date string or description
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    links = relationship("ProjectLinkModel", back_populates="project", cascade="all, delete-orphan")
    logs = relationship("ProjectLogModel", back_populates="project", cascade="all, delete-orphan")

class ProjectLinkModel(Base):
    __tablename__ = "project_links"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"))
    url = Column(String(1024), nullable=False)
    label = Column(String(255), nullable=False) # e.g. "Figma", "Notion", "GitHub"

    project = relationship("ProjectModel", back_populates="links")

class ProjectLogModel(Base):
    __tablename__ = "project_logs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("ProjectModel", back_populates="logs")
