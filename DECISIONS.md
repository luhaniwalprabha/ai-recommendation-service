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