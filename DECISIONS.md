1. Use FastAPI instead of Flask

# Why

Native async support (better for I/O-heavy services)

Strong typing with Python type hints

Automatic request validation via Pydantic

Built-in OpenAPI docs

Tradeoff

Slightly steeper learning curve than Flask

2. Run app using uvicorn app.main:app

Why

Uvicorn is an ASGI server designed for async frameworks

app.main:app explicitly defines the application entry point

Same startup pattern works for local, Docker, and production

Tradeoff

Requires understanding Python module imports

3. Use APIRouter for endpoint composition

Why

Clean separation of API domains

Easy versioning (/v1, /v2)

Scales well as the codebase grows

Tradeoff

More files and indirection

4. Use pydantic-settings for configuration

Why

Separates config from data models

Aligns with Pydantic v2 design

Cleaner and more maintainable config handling

Tradeoff

Extra dependency