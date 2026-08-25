"""Canonical model for Babelix's lexical knowledge graph.

Synset is the graph node. Senses provide multilingual lexicalizations and
SynsetRelation provides typed, provenance-aware directed graph edges.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class SynsetType(StrEnum):
    CONCEPT = "CONCEPT"
    ENTITY = "ENTITY"


class PartOfSpeech(StrEnum):
    NOUN = "NOUN"
    VERB = "VERB"
    ADJECTIVE = "ADJECTIVE"
    ADVERB = "ADVERB"
    OTHER = "OTHER"


class Language(Base):
    __tablename__ = "languages"

    code: Mapped[str] = mapped_column(String(16), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    version: Mapped[str | None] = mapped_column(String(128))
    license: Mapped[str | None] = mapped_column(String(512))
    url: Mapped[str | None] = mapped_column(String(2048))


class RelationType(Base):
    __tablename__ = "relation_types"

    code: Mapped[str] = mapped_column(String(64), primary_key=True)
    label: Mapped[str] = mapped_column(String(256), nullable=False)
    inverse_code: Mapped[str | None] = mapped_column(ForeignKey("relation_types.code"))
    directed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    symmetric: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    transitive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Synset(Base):
    __tablename__ = "synsets"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    canonical_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    type: Mapped[SynsetType] = mapped_column(String(16), nullable=False)
    pos: Mapped[PartOfSpeech] = mapped_column(String(16), default=PartOfSpeech.OTHER, nullable=False)
    main_lemma: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Sense(Base):
    __tablename__ = "senses"
    __table_args__ = (UniqueConstraint("synset_id", "language_code", "normalized_lemma", name="uq_sense_normalized_lemma"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    synset_id: Mapped[UUID] = mapped_column(ForeignKey("synsets.id", ondelete="CASCADE"), nullable=False, index=True)
    language_code: Mapped[str] = mapped_column(ForeignKey("languages.code"), nullable=False, index=True)
    lemma: Mapped[str] = mapped_column(String(512), nullable=False)
    full_lemma: Mapped[str | None] = mapped_column(Text)
    normalized_lemma: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    source_id: Mapped[UUID | None] = mapped_column(ForeignKey("sources.id"))
    source_sense_id: Mapped[str | None] = mapped_column(String(256))


class ExternalIdentifier(Base):
    __tablename__ = "external_identifiers"
    __table_args__ = (UniqueConstraint("source_id", "external_id", name="uq_source_external_identifier"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    synset_id: Mapped[UUID] = mapped_column(ForeignKey("synsets.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id: Mapped[UUID] = mapped_column(ForeignKey("sources.id"), nullable=False)
    external_id: Mapped[str] = mapped_column(String(512), nullable=False)
    external_url: Mapped[str | None] = mapped_column(String(2048))


class SynsetRelation(Base):
    __tablename__ = "synset_relations"
    __table_args__ = (
        CheckConstraint("source_synset_id <> target_synset_id", name="ck_relation_not_self_referential"),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_relation_confidence_range"),
        UniqueConstraint("source_synset_id", "target_synset_id", "relation_type_code", "source_id", name="uq_relation_provenance"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_synset_id: Mapped[UUID] = mapped_column(ForeignKey("synsets.id", ondelete="CASCADE"), nullable=False, index=True)
    target_synset_id: Mapped[UUID] = mapped_column(ForeignKey("synsets.id", ondelete="CASCADE"), nullable=False, index=True)
    relation_type_code: Mapped[str] = mapped_column(ForeignKey("relation_types.code"), nullable=False, index=True)
    language_code: Mapped[str | None] = mapped_column(ForeignKey("languages.code"))
    weight: Mapped[float | None] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    source_id: Mapped[UUID] = mapped_column(ForeignKey("sources.id"), nullable=False)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB)
