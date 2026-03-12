# AI Recommendation Service

Production-style recommendation microservice built with FastAPI.

## Goal
Demonstrate backend system design, clean architecture, and scalable patterns
for building a low-latency recommendation service.

## Architecture (high-level)
- FastAPI (stateless API)
- PostgreSQL (persistence)
- Redis (caching)
- Async workers (event processing)

## Recommendation Pipeline
- Stage 1 (ML): content-based similarity (TF-IDF + cosine similarity) produces top candidates.
- Stage 2 (LLM, optional): if `OPENAI_API_KEY` is set and the user has enough feedback history, the service calls an LLM (`gpt-4o`) to re-rank candidates and attach short reasons.
- Fallback: if the LLM is skipped or errors (timeouts/quota/etc.), the service returns the ML ranking (no reasons).

## Configuration
- Secrets: put `OPENAI_API_KEY` in `.env` (not committed) or in runtime environment variables.
- Template: copy `.env.example` to `.env` and fill values locally.
