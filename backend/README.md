# Ariescan backend

FastAPI service for importing OpenAPI 3.x specifications, generating rule-based checks, running them against a permitted target, and retaining results in SQLite.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8081
```

Open Swagger UI at `http://localhost:8081/docs`. The API reference is also available at `/redoc` and its OpenAPI document at `/openapi.json`.

Run backend checks with `pip install -r requirements-dev.txt`, then `pytest` and `ruff check .`.

For local development `ALLOW_PRIVATE_TARGETS=true` permits localhost and private targets. Set it to `false` for shared deployments; cloud metadata hosts are always blocked. Destructive DELETE requests are deliberately not generated unless `ALLOW_DESTRUCTIVE_TESTS=true` is explicitly set.

Reports can be exported as JSON (`/report.json`), CSV (`/report.csv`), or HTML (`/report.html`) beneath a test-run route.

## API workflow

1. `POST /api/projects` creates a target API project.
2. `POST /api/projects/{project_id}/specs/import` imports OpenAPI 3.x JSON/YAML from `document_url` or inline `content`.
3. `POST /api/projects/{project_id}/test-cases/generate` creates rule-based checks.
4. `POST /api/projects/{project_id}/test-runs` starts execution in the background.
5. `GET /api/test-runs/{run_id}/results` retrieves detailed PASS, FAIL, or ERROR results.

All endpoints, request/response models, and example payload fields are available interactively in Swagger UI.
