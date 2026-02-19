> This document captures architectural decisions made while building the AI Recommendation Service, along with rationale and tradeoffs.

# Use FastAPI over Flask

Decision:
Use FastAPI to build the recommendation service API.

Why:
Native async support, strong typing, automatic request/response validation, and built-in API docs.

Tradeoff:
Slightly steeper learning curve compared to Flask.

# Use Uvicorn with app.main:app

Decision:
Run the service using Uvicorn pointing to app.main:app.

Why:
Explicit entry point makes the application startup predictable and production-ready.

Tradeoff:
Requires understanding module paths and ASGI concepts.

# Use routers to compose endpoints

Decision:
Split endpoints using FastAPI routers (health, recommendations).

Why:
Keeps APIs modular, versionable, and easy to scale as the service grows.

Tradeoff:
More files and structure upfront.

# Separate domain logic from API layer

Decision:
Place core recommendation logic in the domain layer, independent of FastAPI.

Why:
Business logic stays reusable, testable, and independent of transport concerns.

Tradeoff:
Adds an extra abstraction layer.

# Introduce services for execution logic

Decision:
Move candidate generation into a services layer, orchestrated by the domain.

Why:
Separates what the business wants from how it is implemented (rules, ML, infra).

Tradeoff:
Initial implementation may feel verbose for simple logic.

# Use Pydantic schemas for request/response models

Decision:
Define request and response contracts using Pydantic models.

Why:
Strong typing, automatic validation, and clear API contracts.

Tradeoff:
Requires maintaining schema definitions alongside logic.

# Use domain-specific exceptions

Decision:
Define semantic exceptions in the domain and map them to HTTP errors in the API.

Why:
Keeps business logic free of HTTP concerns and enables consistent error handling.

Tradeoff:
Requires explicit exception handling in API layer.


# Use SQLAlchemy ORM for persistence

Decision:
Use SQLAlchemy ORM to model and interact with the Postgres database.

Why:
Provides a mature, Pythonic abstraction over SQL with strong ecosystem support and clean separation between schema, queries, and sessions.

Tradeoff:
Requires understanding ORM patterns and session lifecycle.

# Use per-request DB sessions via dependency injection

Decision:
Create a `get_db` dependency to provide one database session per API request.

Why:
Prevents connection leaks, ensures transactional safety, and keeps DB lifecycle management out of routes.

Tradeoff:
Adds an extra dependency layer that must be wired correctly.

# Separate database access using repository pattern

Decision:
Introduce repositories (e.g., `ProductRepository`) to encapsulate all database queries.

Why:
Prevents ORM leakage into business logic and APIs, improves testability, and localizes data access changes.

Tradeoff:
Adds an additional abstraction layer for simple CRUD operations.

# Introduce service layer for business use cases

Decision:
Add a service layer (e.g., `ProductService`) to orchestrate repositories and apply business rules.

Why:
Keeps business logic centralized and prevents API handlers from becoming complex or stateful.

Tradeoff:
May feel thin initially until business rules grow.

# Use Postgres via Docker for local development

Decision:
Run Postgres locally using Docker instead of installing it directly on the system.

Why:
Ensures consistent local setup, mirrors production environments, and avoids system-level conflicts.

Tradeoff:
Requires basic Docker familiarity.

# Use seed scripts for initial data population

Decision:
Seed sample data using standalone scripts instead of hardcoding data in APIs or services.

Why:
Keeps runtime code clean and makes local development and testing repeatable.

Tradeoff:
Requires maintaining scripts alongside schema changes.

# Keep API layer thin and orchestration-only

Decision:
Limit API handlers to request parsing, dependency wiring, and response formatting.

Why:
Maintains clear separation of concerns and keeps HTTP as a transport layer only.

Tradeoff:
More indirection compared to monolithic handlers.

# Centralized SQLAlchemy model registration

Decision:
Register all ORM models via a single `app.models` import before metadata creation.

Why:
SQLAlchemy only creates tables it knows about at runtime; centralized imports ensure foreign keys resolve correctly.

Tradeoff:
Requires maintaining a central model registry file.

# Use Cache-Aside pattern for recommendations

Decision:
Implement Redis caching using the cache-aside pattern for recommendation reads.

Why:
Reduces database load, improves response time, and keeps the read path simple and predictable. Cache-aside allows the application to control when data is refreshed and ensures recommendations are recomputed only when necessary.

Tradeoff:
Requires explicit cache invalidation and consistency management when underlying data changes.

# Invalidate cache on feedback events

Decision:
Invalidate user recommendation cache when feedback (click, like, purchase) is recorded.

Why:
Ensures recommendations reflect the latest user behavior and prevents stale personalization.

Tradeoff:
Increases cache churn for highly active users.

# Generate recommendations asynchronously using background tasks

Decision:
Offload recommendation generation to background tasks instead of processing synchronously within the request.

Why:
Prevents blocking API responses, improves responsiveness, and mirrors real-world systems where recommendation computation can be expensive.

Tradeoff:
Adds complexity in job coordination and requires cache/state management for asynchronous results.

# Check cache before scheduling recommendation generation

Decision:
Verify Redis cache before scheduling a background generation task.

Why:
Prevents unnecessary background jobs when recommendations are already available, reducing compute usage and improving performance.

Tradeoff:
Requires reliable cache invalidation to ensure freshness.

# Prevent duplicate recommendation generation using Redis locks

Decision:
Use a Redis-based lock (lock:recommendations:{user_id}) to ensure only one background job generates recommendations per user at a time.

Why:
Multiple rapid requests can schedule duplicate background jobs, causing redundant computation, race conditions, and cache churn. A short-lived lock ensures only one job runs.

Tradeoff:
Requires careful TTL configuration to prevent stale locks if a worker crashes.

# Ensure idempotent recommendation generation

Decision:
Re-check cache state inside the background worker before recomputing recommendations.

Why:
Prevents stale or duplicate background jobs from overwriting fresh results when concurrent requests occur.

Tradeoff:
Adds an extra cache lookup but significantly improves correctness and resilience.

# Use stale-while-revalidate strategy for recommendations

Decision:
Return cached recommendations when available. On cache miss, return the latest stored recommendations while triggering background regeneration.

Why:
Ensures users always receive results immediately while freshness improves asynchronously.

Tradeoff:
Users may briefly see slightly outdated recommendations, and the read path becomes slightly more complex.