# Architecture Overview

```
/backend
  app/
    main.py            FastAPI app, router registration, CORS, startup table creation
    core/               config (env settings), database (SQLAlchemy engine/session), security (JWT/bcrypt)
    api/                one routes_*.py per feature area + shared deps/compliance helper
    models/             SQLAlchemy ORM models, grouped by domain
    schemas/            Pydantic request/response schemas
    services/           business logic: scoring, generation, analytics, comments, strategy
    parsers/            Instagram Insights CSV/JSON/text/manual-form normalizers
    llm/                provider abstraction (OpenAI/Anthropic/Ollama/mock) + prompt templates
    simulation/         closed virality simulator (network graphs, entities, engine)
    compliance/         the guardrail engine (see docs/compliance_philosophy.md)
    tests/              pytest suite
  alembic/              migrations (optional -- create_all() also runs on startup for local dev)
  scripts/              sample data generator
/frontend
  src/
    pages/              one component per nav item
    components/         Sidebar, TopBar, shared UI bits
    api/                fetch-based API client
    store/               auth context
    tests/              Vitest + Testing Library suite
/sample_data             generated demo CSV/JSON files (see scripts/seed_sample_data.py)
/docs                    this file + compliance philosophy
```

## Request lifecycle for a "generate" endpoint

Using `POST /content/hooks` as an example:

1. FastAPI validates the request body against `HookGenerateRequest`.
2. `enforce_compliance()` runs the guardrail over the free-text fields
   (topic, niche, audience). If blocked, a 400 is returned immediately with
   the guardrail's explanation and alternative -- nothing else executes.
3. `services/generation.generate_hooks()` calls `llm/client.call_llm_json()`,
   which applies rate limiting + bounded retries and asks the configured
   provider (OpenAI/Anthropic/Ollama/mock) for strict JSON.
4. If the LLM call fails or returns malformed JSON, a deterministic
   template-based fallback produces a still-useful result instead of a
   500 error -- this is what runs by default with `DEFAULT_LLM_PROVIDER=mock`.
5. Results are persisted (as `HookAsset` rows) and returned to the frontend.

## Why SQLite + Alembic

SQLite keeps local setup to zero external services. Alembic is included so
the schema can be migrated cleanly if you move to Postgres/MySQL for a
shared/team deployment -- update `DATABASE_URL` and run
`alembic upgrade head` instead of relying on `Base.metadata.create_all()`.

## Why a rules+LLM blend for scoring

`services/scoring.py` always computes a cheap, transparent rules-based score
first (word counts, urgency-language detection, presence of a hook/CTA,
etc.), so the feature works with zero LLM configuration. When an LLM
provider is configured, its critique is blended in by averaging per-field
scores and taking the more conservative (higher) retention-risk assessment
of the two -- the system is designed to never be more optimistic than either
input alone.
