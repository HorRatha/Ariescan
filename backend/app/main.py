import csv
import html
import io
import json
import time
from datetime import datetime, timezone

import httpx
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from jsonschema import SchemaError, ValidationError, validate
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .core.config import settings
from .db import Base, SessionLocal, engine, get_db
from .models import ApiSpec, Endpoint, Project, TestCase, TestResult, TestRun
from .schemas import (
    EndpointOut,
    ImportSpec,
    ProjectCreate,
    ProjectOut,
    ProjectUpdate,
    TestCaseOut,
    TestResultOut,
    TestRunOut,
)
from .services.generator import generate
from .services.openapi import extract_endpoints, parse_document
from .services.security import redact, validate_target_url

app = FastAPI(
    title="Ariescan API",
    version="1.0.0",
    description="Local-first, OpenAPI-driven automated API testing.",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


def one(db, model, id):
    value = db.get(model, id)
    if not value:
        raise HTTPException(404, f"{model.__name__} not found")
    return value


class ResponseTooLargeError(Exception):
    pass


def response_body(response: httpx.Response):
    chunks = []
    total = 0
    for chunk in response.iter_bytes():
        total += len(chunk)
        if total > settings.max_response_bytes:
            raise ResponseTooLargeError(f"Response exceeded {settings.max_response_bytes} bytes")
        chunks.append(chunk)
    raw = b"".join(chunks)
    try:
        return json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return raw.decode(errors="replace")


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "service": "ariescan"}


@app.get("/api/projects", response_model=list[ProjectOut], tags=["Projects"])
def list_projects(db: Session = Depends(get_db)):
    return db.scalars(select(Project).order_by(Project.created_at.desc())).all()


@app.post("/api/projects", response_model=ProjectOut, status_code=201, tags=["Projects"])
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(name=data.name, description=data.description, base_url=validate_target_url(data.base_url))
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@app.get("/api/projects/{project_id}", response_model=ProjectOut, tags=["Projects"])
def get_project(project_id: str, db: Session = Depends(get_db)):
    return one(db, Project, project_id)


@app.patch("/api/projects/{project_id}", response_model=ProjectOut, tags=["Projects"])
def update_project(project_id: str, data: ProjectUpdate, db: Session = Depends(get_db)):
    project = one(db, Project, project_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, validate_target_url(value) if field == "base_url" else value)
    db.commit()
    db.refresh(project)
    return project


@app.delete("/api/projects/{project_id}", status_code=204, tags=["Projects"])
def delete_project(project_id: str, db: Session = Depends(get_db)):
    one(db, Project, project_id)
    endpoints = db.scalars(select(Endpoint.id).where(Endpoint.project_id == project_id)).all()
    cases = db.scalars(select(TestCase.id).where(TestCase.endpoint_id.in_(endpoints))).all()
    runs = db.scalars(select(TestRun.id).where(TestRun.project_id == project_id)).all()
    db.execute(delete(TestResult).where((TestResult.test_case_id.in_(cases)) | (TestResult.test_run_id.in_(runs))))
    db.execute(delete(TestCase).where(TestCase.endpoint_id.in_(endpoints)))
    db.execute(delete(Endpoint).where(Endpoint.project_id == project_id))
    db.execute(delete(ApiSpec).where(ApiSpec.project_id == project_id))
    db.delete(one(db, Project, project_id))
    db.commit()


@app.post("/api/projects/{project_id}/specs/import", tags=["OpenAPI"])
async def import_spec(project_id: str, data: ImportSpec, db: Session = Depends(get_db)):
    one(db, Project, project_id)
    if data.document_url:
        url = validate_target_url(data.document_url)
        try:
            async with httpx.AsyncClient(timeout=settings.request_timeout_seconds, follow_redirects=False) as client:
                response = await client.get(url)
                response.raise_for_status()
                content = response.text
        except httpx.HTTPError as exc:
            raise HTTPException(422, f"Could not retrieve OpenAPI document: {exc}")
    else:
        content = data.content
    spec, fmt = parse_document(content)
    info = spec.get("info", {})
    endpoint_data = extract_endpoints(spec)
    old = db.scalars(select(Endpoint.id).where(Endpoint.project_id == project_id)).all()
    old_cases = db.scalars(select(TestCase.id).where(TestCase.endpoint_id.in_(old))).all()
    db.execute(delete(TestResult).where(TestResult.test_case_id.in_(old_cases)))
    db.execute(delete(TestCase).where(TestCase.endpoint_id.in_(old)))
    db.execute(delete(Endpoint).where(Endpoint.project_id == project_id))
    db.execute(delete(ApiSpec).where(ApiSpec.project_id == project_id))
    db.add(
        ApiSpec(
            project_id=project_id,
            title=info.get("title", "Untitled API"),
            version=info.get("version", "unknown"),
            spec_format=fmt,
            spec_content=content,
        )
    )
    db.add_all([Endpoint(project_id=project_id, **item) for item in endpoint_data])
    db.commit()
    return {
        "title": info.get("title", "Untitled API"),
        "version": info.get("version", "unknown"),
        "endpoints_discovered": len(endpoint_data),
    }


@app.get("/api/projects/{project_id}/endpoints", response_model=list[EndpointOut], tags=["OpenAPI"])
def list_endpoints(project_id: str, db: Session = Depends(get_db)):
    one(db, Project, project_id)
    return db.scalars(
        select(Endpoint).where(Endpoint.project_id == project_id).order_by(Endpoint.path, Endpoint.method)
    ).all()


@app.post("/api/projects/{project_id}/test-cases/generate", tags=["Test cases"])
def generate_cases(project_id: str, db: Session = Depends(get_db)):
    one(db, Project, project_id)
    endpoints = db.scalars(select(Endpoint).where(Endpoint.project_id == project_id)).all()
    ids = [e.id for e in endpoints]
    db.execute(delete(TestCase).where(TestCase.endpoint_id.in_(ids)))
    cases = [c for endpoint in endpoints for c in generate(endpoint)]
    db.add_all(cases)
    db.commit()
    return {"generated": len(cases)}


@app.get("/api/projects/{project_id}/test-cases", response_model=list[TestCaseOut], tags=["Test cases"])
def list_cases(project_id: str, db: Session = Depends(get_db)):
    one(db, Project, project_id)
    return db.scalars(select(TestCase).join(Endpoint).where(Endpoint.project_id == project_id)).all()


def run_tests(run_id: str):
    db = SessionLocal()
    run = one(db, TestRun, run_id)
    project = one(db, Project, run.project_id)
    try:
        project.base_url = validate_target_url(project.base_url)
    except HTTPException:
        run.status = "completed"
        run.error_tests = 1
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
        db.close()
        return
    run.status = "running"
    run.started_at = datetime.now(timezone.utc)
    db.commit()
    cases = db.scalars(
        select(TestCase)
        .join(Endpoint)
        .where(Endpoint.project_id == project.id, TestCase.enabled)
        .limit(settings.max_test_cases_per_run)
    ).all()
    run.total_tests = len(cases)
    db.commit()
    with httpx.Client(timeout=settings.request_timeout_seconds, follow_redirects=False) as client:
        for case in cases:
            db.refresh(run)
            if run.status == "cancelled":
                break
            endpoint = one(db, Endpoint, case.endpoint_id)
            path = endpoint.path
            for p in endpoint.parameters:
                if p.get("in") == "path":
                    path = path.replace("{" + p["name"] + "}", str(p.get("schema", {}).get("example", 1)))
            started = time.perf_counter()
            status = "ERROR"
            actual = {}
            message = None
            code = None
            try:
                request_url = f"{project.base_url.rstrip('/')}/{path.lstrip('/')}"
                params = case.request_data.get("params", {}).copy()
                params.pop(case.request_data.get("omit_parameter"), None)
                with client.stream(
                    endpoint.method, request_url, json=case.request_data.get("json"), params=params
                ) as response:
                    code = response.status_code
                    body = response_body(response)
                    headers = dict(response.headers)
                actual = redact({"headers": headers, "body": body})
                if code not in case.expected_result.get("status_codes", []):
                    status = "FAIL"
                    message = f"Expected status {case.expected_result.get('status_codes')}, received {code}"
                else:
                    schema = case.expected_result.get("schema") or {}
                    try:
                        validate(body, schema) if schema else None
                        status = "PASS"
                    except (ValidationError, SchemaError) as exc:
                        status = "FAIL"
                        message = f"Response schema mismatch: {exc.message}"
            except (httpx.HTTPError, ResponseTooLargeError) as exc:
                message = f"Infrastructure error: {exc}"
                actual = {"request_url": f"{project.base_url.rstrip('/')}/{path.lstrip('/')}"}
            result = TestResult(
                test_run_id=run.id,
                test_case_id=case.id,
                status=status,
                actual_status_code=code,
                expected_result=case.expected_result,
                actual_result=actual,
                error_message=message,
                duration_ms=round((time.perf_counter() - started) * 1000),
            )
            db.add(result)
            if status == "PASS":
                run.passed_tests += 1
            elif status == "FAIL":
                run.failed_tests += 1
            else:
                run.error_tests += 1
            db.commit()
    if run.status != "cancelled":
        run.status = "completed"
    run.finished_at = datetime.now(timezone.utc)
    db.commit()
    db.close()


@app.post("/api/projects/{project_id}/test-runs", response_model=TestRunOut, status_code=202, tags=["Test runs"])
def start_run(project_id: str, tasks: BackgroundTasks, db: Session = Depends(get_db)):
    one(db, Project, project_id)
    run = TestRun(project_id=project_id)
    db.add(run)
    db.commit()
    db.refresh(run)
    tasks.add_task(run_tests, run.id)
    return run


@app.get("/api/test-runs/{run_id}", response_model=TestRunOut, tags=["Test runs"])
def get_run(run_id: str, db: Session = Depends(get_db)):
    return one(db, TestRun, run_id)


@app.get("/api/test-runs/{run_id}/results", response_model=list[TestResultOut], tags=["Test runs"])
def get_results(run_id: str, db: Session = Depends(get_db)):
    one(db, TestRun, run_id)
    return db.scalars(select(TestResult).where(TestResult.test_run_id == run_id)).all()


@app.post("/api/test-runs/{run_id}/cancel", response_model=TestRunOut, tags=["Test runs"])
def cancel_run(run_id: str, db: Session = Depends(get_db)):
    run = one(db, TestRun, run_id)
    if run.status in {"pending", "running"}:
        run.status = "cancelled"
        db.commit()
        db.refresh(run)
    return run


@app.get("/api/projects/{project_id}/reports", response_model=list[TestRunOut], tags=["Reports"])
def reports(project_id: str, db: Session = Depends(get_db)):
    one(db, Project, project_id)
    return db.scalars(select(TestRun).where(TestRun.project_id == project_id).order_by(TestRun.started_at.desc())).all()


@app.get("/api/test-runs/{run_id}/report.json", tags=["Reports"])
def export_json(run_id: str, db: Session = Depends(get_db)):
    run = one(db, TestRun, run_id)
    results = db.scalars(select(TestResult).where(TestResult.test_run_id == run_id)).all()
    return {
        "run": TestRunOut.model_validate(run).model_dump(mode="json"),
        "results": [TestResultOut.model_validate(x).model_dump(mode="json") for x in results],
    }


@app.get("/api/test-runs/{run_id}/report.csv", tags=["Reports"])
def export_csv(run_id: str, db: Session = Depends(get_db)):
    one(db, TestRun, run_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["status", "actual_status", "duration_ms", "error_message"])
    for x in db.scalars(select(TestResult).where(TestResult.test_run_id == run_id)):
        writer.writerow([x.status, x.actual_status_code, x.duration_ms, x.error_message])
    return Response(
        output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=report-{run_id}.csv"},
    )


@app.get("/api/test-runs/{run_id}/report.html", tags=["Reports"])
def export_html(run_id: str, db: Session = Depends(get_db)):
    run = one(db, TestRun, run_id)
    results = db.scalars(select(TestResult).where(TestResult.test_run_id == run_id)).all()
    rows = "".join(
        "<tr>"
        f"<td>{html.escape(item.status)}</td>"
        f"<td>{item.actual_status_code or ''}</td>"
        f"<td>{item.duration_ms or ''}</td>"
        f"<td>{html.escape(item.error_message or '')}</td>"
        "</tr>"
        for item in results
    )
    document = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>Ariescan report</title></head><body>"
        f"<h1>Ariescan test run {html.escape(run.id)}</h1>"
        f"<p>Status: {html.escape(run.status)} | Pass: {run.passed_tests} | "
        f"Fail: {run.failed_tests} | Errors: {run.error_tests}</p>"
        "<table border='1'><thead><tr><th>Result</th><th>HTTP status</th>"
        "<th>Duration (ms)</th><th>Details</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></body></html>"
    )
    return Response(
        document,
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename=report-{run_id}.html"},
    )
