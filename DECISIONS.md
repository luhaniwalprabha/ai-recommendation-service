> This document captures architectural decisions made while building the AI Recommendation Service, including rationale and tradeoffs.

---

## API & Framework Decisions

### Use FastAPI over Flask

Decision:
Use FastAPI to build the recommendation service API.

Why:
Provides native async support, strong typing, automatic validation, and interactive API documentation.

Tradeoff:
Slightly steeper learning curve compared to Flask.

---

### Use Uvicorn with `app.main:app`

Decision:
Run the service using Uvicorn with an explicit ASGI entry point.

Why:
Ensures predictable startup behavior and production readiness.

Tradeoff:
Requires familiarity with ASGI and module paths.

---

### Compose endpoints using routers

Decision:
Organize endpoints using FastAPI routers (health, recommendations).

Why:
Improves modularity, versioning, and scalability.

Tradeoff:
Introduces additional structure upfront.

---

## Architecture & Layering

### Separate domain logic from API layer

Decision:
Keep recommendation logic in the domain layer independent of FastAPI.

Why:
Ensures business logic remains reusable, testable, and transport-agnostic.

Tradeoff:
Adds an additional abstraction layer.

---

### Introduce service layer for orchestration

Decision:
Use a service layer to coordinate repositories, caching, and recommendation generation.

Why:
Separates business intent from implementation details and supports future ML/infra expansion.

Tradeoff:
May feel verbose early in development.

---

### Keep API layer thin

Decision:
Limit API handlers to request parsing, dependency wiring, and response formatting.

Why:
Maintains separation of concerns and prevents HTTP handlers from accumulating business logic.

Tradeoff:
Adds indirection compared to monolithic handlers.

---

## Data & Persistence

### Use SQLAlchemy ORM with PostgreSQL

Decision:
Use SQLAlchemy ORM for database interaction with PostgreSQL.

Why:
Provides a mature abstraction, strong ecosystem support, and clean session handling.

Tradeoff:
Requires understanding ORM patterns and session lifecycle.

---

### Use per-request DB sessions via dependency injection

Decision:
Provide a session per request using `get_db`.

Why:
Prevents connection leaks and ensures transactional safety.

Tradeoff:
Requires correct dependency wiring.

---

### Use repository pattern for data access

Decision:
Encapsulate database queries within repositories.

Why:
Prevents ORM leakage, improves testability, and localizes data access changes.

Tradeoff:
Adds abstraction for simple CRUD operations.

---

### Centralize ORM model registration

Decision:
Import all models via a central registry before metadata creation.

Why:
Ensures foreign keys resolve and tables are created correctly.

Tradeoff:
Requires maintaining a central registry.

---

### Use Dockerized Postgres for local development

Decision:
Run Postgres via Docker for local development.

Why:
Ensures environment consistency and mirrors production.

Tradeoff:
Requires basic Docker familiarity.

---

### Use seed scripts for data initialization

Decision:
Populate sample data via seed scripts.

Why:
Keeps runtime code clean and ensures repeatable setup.

Tradeoff:
Scripts must be maintained with schema changes.

---

## Caching & Performance

### Use Cache-Aside pattern with Redis

Decision:
Implement Redis caching using the cache-aside pattern.

Why:
Improves response latency and reduces database load while keeping refresh control in the application.

Tradeoff:
Requires explicit invalidation and consistency management.

---

### Invalidate cache on feedback events

Decision:
Invalidate recommendation cache when user feedback occurs.

Why:
Ensures personalization reflects latest behavior.

Tradeoff:
Increases cache churn for highly active users.

---

### Graceful cache fallback & Redis failure tolerance

Decision:
Treat Redis as non-critical by falling back to DB or safe responses if cache fails.

Why:
Improves reliability and availability during cache outages.

Tradeoff:
Fallback paths may increase latency.

---

## Recommendation Generation & Consistency

### Generate recommendations asynchronously

Decision:
Run recommendation generation in background tasks.

Why:
Prevents blocking API responses and supports compute-heavy workflows.

Tradeoff:
Adds coordination complexity and state management.

---

### Check cache before scheduling generation

Decision:
Verify cache before scheduling background jobs.

Why:
Prevents redundant computation and reduces resource usage.

Tradeoff:
Relies on correct cache invalidation for freshness.

---

### Prevent duplicate generation using Redis locks

Decision:
Use Redis locks (`lock:recommendations:{user_id}`) to ensure only one generation job runs per user.

Why:
Prevents race conditions, duplicate compute, and cache churn under concurrent requests.

Tradeoff:
Requires TTL safeguards to prevent stale locks.

---

### Ensure idempotent generation

Decision:
Re-check cache state inside workers before recomputation.

Why:
Prevents stale jobs from overwriting fresh results.

Tradeoff:
Adds an extra cache lookup.

---

### Use stale-while-revalidate strategy

Decision:
Return cached recommendations immediately and refresh in background when stale.

Why:
Provides fast responses while improving freshness asynchronously.

Tradeoff:
Users may briefly see slightly outdated recommendations.

---

### Separate read and write paths

Decision:
- GET → serve cached or persisted recommendations  
- POST → schedule async generation  

Why:
Ensures low latency while supporting scalable asynchronous computation.

Tradeoff:
Data may be briefly stale between refresh cycles.

---

### Enforce structured API responses

Decision:
Return structured recommendation objects rather than raw IDs.

Why:
Supports extensibility (scores, explanations) and enforces stable API contracts.

Tradeoff:
Adds a transformation step before response serialization.

---

## ML & Modeling Decisions

### Start with content-based filtering (TF-IDF)

Decision:
Use a content-based recommender built with TF-IDF vectors.

Why:
Works with available product metadata, is simple to implement, and gives deterministic baseline recommendations without requiring user interaction history.

Tradeoff:
Quality depends on metadata quality and does not capture collaborative user behavior.

---

### Use product name + category as feature text

Decision:
Build recommendation documents by combining `name` and `category` fields per product.

Why:
Keeps feature engineering lightweight while capturing basic semantic similarity between products.

Tradeoff:
Ignores richer signals (description, brand, attributes, user behavior) that could improve ranking relevance.

---

### Rank with cosine similarity and exclude anchor item

Decision:
Use cosine similarity over TF-IDF vectors, remove self-match, and return top-K product IDs.

Why:
Cosine similarity is a standard, fast baseline for sparse text vectors and straightforward to reason about in early iterations.

Tradeoff:
Can over-prioritize lexical overlap and may underperform when item similarity requires semantic or behavioral context.

---

### Add local ML bootstrap and smoke-test scripts

Decision:
Include scripts for seeding representative product data and validating recommender output.

Why:
Improves iteration speed and enables quick manual verification of ranking behavior during development.

Tradeoff:
Script-based checks are not a substitute for automated test coverage or offline evaluation metrics.

---

## Observability & Reliability

### Health & readiness endpoints

Decision:
Expose `/health` (liveness) and `/ready` (dependency readiness).

Why:
Prevents traffic routing to instances lacking critical dependencies and aligns with container orchestration best practices.

Tradeoff:
Readiness checks add minor overhead.

---

### Request logging middleware

Decision:
Log request metadata, response status, and latency via centralized middleware.

Why:
Improves observability and debugging without scattering logs.

Tradeoff:
Adds minor overhead and increased log volume.

# Implement soft TTL with background refresh

Decision:
Store generation timestamps in cache and trigger asynchronous refresh when cache becomes stale.

Why:
Ensures low-latency responses while keeping recommendations fresh without blocking user requests.

Tradeoff:
Adds complexity in cache payload structure and refresh coordination.
