# Babelix

Babelix is a **BabelNet-like, independently sourced lexical knowledge graph**.
It models concepts and named entities as multilingual synsets, records their
lexical senses and provenance, and exposes the graph through a versioned
FastAPI service. Babelix does not scrape or redistribute BabelNet data.

## First vertical slice

This repository contains the initial project template and **STEP 01: the
canonical data model**. PostgreSQL is the source of truth. Search, cache,
workers, and a graph projection are deliberately deferred until the canonical
records and their lineage are stable.

### Local development

```bash
uv sync --extra dev
uv run pytest
uv run uvicorn app.main:app --reload
```

The service exposes `GET /health` and starts at `http://127.0.0.1:8000`.

## Layout

```text
app/                  FastAPI application and canonical SQLAlchemy models
docs/                 Architecture and data-model decisions
etl/                  Source-specific extraction and transformation boundary
tests/                Unit tests
```

See [STEP 01 — Data Model](docs/step-01-data-model.md) for the ERD, invariants,
and the example graph for the University of Zanjan.
