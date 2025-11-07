
from sqlalchemy import ForeignKey, String, Index, func, Text, TIMESTAMP, Table, Column, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Any
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, CITEXT
from pgvector.sqlalchemy import Vector

class Base(DeclarativeBase):
    pass

class Job(Base):
    __tablename__ = "jobs"
    
    id: Mapped[str] = mapped_column(Text(), primary_key=True)
    source: Mapped[str] = mapped_column(Text())
    source_id: Mapped[str | None] = mapped_column(Text())
    company: Mapped[str] = mapped_column(CITEXT())
    title: Mapped[str] = mapped_column(Text())
    locations: Mapped[dict] = mapped_column(JSONB, server_default='[]')
    remote: Mapped[bool | None]
    posted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), index=True)
    url: Mapped[str | None] = mapped_column(Text())
    description_html: Mapped[str | None] = mapped_column(Text())
    description_text: Mapped[str | None] = mapped_column(Text())
    tags: Mapped[list | None] = mapped_column(ARRAY(Text()), server_default='[]')
    compensation: Mapped[dict | None] = mapped_column(JSONB)
    is_active: Mapped[bool] = mapped_column(default=True)
    inserted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    embeddings: Mapped[list["JobEmbedding"]] = relationship(
    back_populates="job",
    cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index('jobs_posted_at_idx', 'posted_at', postgresql_using='btree'),
        Index('jobs_company_idx', 'company'),
    )
    
    def __repr__(self) -> str:
        return f"Job(id={self.id!r}, company={self.company!r}, title={self.title!r})"

    
class JobEmbedding(Base):
    __tablename__ = "job_embeddings"

    job_id: Mapped[str] = mapped_column(Text(), ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True) 
    model_name: Mapped[str] = mapped_column(Text())
    embedding: Mapped[list] = mapped_column(Vector(384), nullable=False, default=list)
    embedded_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    job: Mapped["Job"] = relationship(back_populates="embeddings")
    
    __table_args__ = (
        Index(
            'job_embeddings_ivfflat_cos',
            'embedding',
            postgresql_using='ivfflat',
            postgresql_with={'lists': 100},
            postgresql_ops={'embedding': 'vector_cosine_ops'}
        ),
    )
    
    def __repr__(self) -> str:
        return f"JobEmbedding(job_id={self.job_id!r}, model={self.model_name!r})"
    

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    auth_provider: Mapped[str] = mapped_column(
        String(20), 
        default="local",
        nullable=False
    )
    
    username: Mapped[str | None] = mapped_column(String(50), unique=True, index=True)
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    roles: Mapped[list["Role"]] = relationship(
        secondary=user_roles,
        back_populates="users"
    )
    
    __table_args__ = (
        CheckConstraint(
            "(auth_provider = 'local' AND hashed_password IS NOT NULL) OR "
            "(auth_provider = 'google' AND google_id IS NOT NULL)",
            name="auth_provider_fields_check"
        ),
    )
    
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r})"


class Role(Base):
    __tablename__ = "roles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )
    
    users: Mapped[list["User"]] = relationship(
        secondary=user_roles,
        back_populates="roles"
    )
    
    def __repr__(self) -> str:
        return f"Role(id={self.id!r}, name={self.name!r})"