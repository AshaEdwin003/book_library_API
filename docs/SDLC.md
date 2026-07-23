# Software Development Life Cycle

## 1. Project overview

The Book Library API is a REST API for managing a personal collection of books. It provides endpoints for creating, reading, updating, and deleting books, together with pagination, genre filtering, sorting, request validation, and interactive OpenAPI documentation.

The current implementation is a lightweight single-service application built with FastAPI and SQLAlchemy. SQLite is used by default so that the project can be run locally without an external database.

## 2. Requirements analysis

### Functional requirements

The API must:

- Create a book with a title, author, genre, optional rating, and optional notes.
- Return all books with pagination controls.
- Return one book by its identifier.
- Update one or more fields on an existing book.
- Delete a book by its identifier.
- Filter books by genre.
- Sort books by rating or date added.
- Reject invalid input with validation errors.
- Expose machine-readable and interactive API documentation.

### Non-functional requirements

- Use a clear separation between routing, validation, business logic, and persistence.
- Keep database sessions scoped to individual requests.
- Provide predictable HTTP status codes and JSON responses.
- Keep configuration, especially the database URL, outside the application code.
- Make the service easy to run locally and straightforward to extend.

### Current scope and assumptions

- The API is intended for a single personal library.
- Authentication, authorization, multi-user ownership, book cover storage, and external metadata integrations are out of scope for the current version.
- SQLite is suitable for local development and small workloads. A production deployment should use a managed relational database.

## 3. System design

### Architecture

The service follows a layered architecture:

```text
HTTP client
    |
    v
FastAPI router (app/routers/books.py)
    |
    v
Pydantic schemas (app/schemas/book.py)
    |
    v
Book service (app/services/book_service.py)
    |
    v
SQLAlchemy model and session (app/models, app/database.py)
    |
    v
SQLite database (media_library.db)
```

Responsibilities are intentionally separated:

- `app/main.py` creates the FastAPI application, configures CORS, creates database tables, and exposes the health endpoint.
- `app/routers/` defines HTTP paths, query parameters, dependency injection, and HTTP errors.
- `app/schemas/` defines request and response contracts and validates field values.
- `app/services/` contains database operations and business behavior.
- `app/models/` defines the SQLAlchemy persistence model and genre enumeration.
- `app/database.py` loads configuration and manages SQLAlchemy engine/session creation.

### Data model

The `books` table contains:

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `id` | Integer | Generated | Primary key |
| `title` | String | Yes | 1–200 characters |
| `author` | String | Yes | 1–100 characters |
| `genre` | Enum | Yes | One of the supported genres |
| `rating` | Float | No | 0–5, rounded to one decimal place on create |
| `notes` | String | No | Maximum 1,000 characters |
| `date_added` | DateTime | Generated | UTC timestamp by default |

Supported genres are `fiction`, `non_fiction`, `mystery`, `sci_fi`, `fantasy`, `biography`, `history`, `science`, and `other`.

## 4. Implementation

The API uses resource-oriented endpoints under `/api/v1/books`:

| Method | Path | Purpose | Success |
| --- | --- | --- | --- |
| `GET` | `/api/v1/books/` | List books; supports `skip`, `limit`, `genre`, and `sort_by` | `200` |
| `POST` | `/api/v1/books/` | Create a book | `201` |
| `GET` | `/api/v1/books/{book_id}` | Retrieve one book | `200` |
| `PATCH` | `/api/v1/books/{book_id}` | Partially update a book | `200` |
| `DELETE` | `/api/v1/books/{book_id}` | Delete a book | `204` |

Missing books return `404`. Invalid request bodies and query parameters are handled by FastAPI/Pydantic validation and return `422` responses.

## 5. Verification and validation

The intended verification strategy is:

1. Validate formatting and imports with `black`, `isort`, and `flake8`.
2. Add unit tests for schema validation and service methods.
3. Add API integration tests for every endpoint and important error path.
4. Test pagination, filtering, sorting, partial updates, and empty results.
5. Run a smoke test against the local server and inspect `/api/docs`.
6. Verify database behavior against SQLite and the target production database before release.

### Current quality status

The repository currently contains no automated test suite, lint configuration, migration tooling, or CI workflow. These are release-readiness tasks, not implemented features, and should be added before production deployment.

## 6. Deployment preparation

For a production deployment:

- Replace the local SQLite database with PostgreSQL or another managed relational database.
- Use a migration tool such as Alembic instead of relying on `Base.metadata.create_all` during application startup.
- Restrict `allow_origins` to approved frontend origins rather than allowing every origin.
- Add authentication and authorization if the service becomes multi-user.
- Run the application behind a reverse proxy with HTTPS.
- Store secrets and environment-specific settings in the deployment platform's secret manager.
- Add structured logging, health/readiness checks, metrics, backups, and alerting.
- Pin and regularly review dependency versions using a vulnerability scanner.

## 7. Maintenance and future roadmap

Recommended next increments are:

1. Add pytest fixtures and endpoint coverage.
2. Add CI for tests, formatting, linting, and dependency checks.
3. Add Alembic migrations and environment-specific configuration.
4. Add authentication and user-owned libraries.
5. Add search by title and author, plus a total-count response for pagination.
6. Add Docker packaging and a deployment workflow.
7. Add observability and API version/deprecation policies.

Each increment should follow the same cycle: define acceptance criteria, implement in the appropriate layer, add tests, update the API documentation, and review operational impact.

