"use client";

import { ChangeEvent, FormEvent, useCallback, useEffect, useState } from "react";
import { api, Endpoint, Project, TestCase, TestResult, TestRun } from "@/lib/api";

const running = (run: TestRun | null) => run && ["pending", "running"].includes(run.status);
const errorText = (error: unknown) => error instanceof Error ? error.message : "Unexpected request failure.";

export default function Home() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [project, setProject] = useState<Project | null>(null);
  const [endpoints, setEndpoints] = useState<Endpoint[]>([]);
  const [cases, setCases] = useState<TestCase[]>([]);
  const [reports, setReports] = useState<TestRun[]>([]);
  const [run, setRun] = useState<TestRun | null>(null);
  const [results, setResults] = useState<TestResult[]>([]);
  const [name, setName] = useState("");
  const [baseUrl, setBaseUrl] = useState("http://localhost:8000");
  const [specUrl, setSpecUrl] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async (value: Project) => {
    const [foundEndpoints, foundCases, foundReports] = await Promise.all([api.endpoints(value.id), api.testCases(value.id), api.reports(value.id)]);
    setEndpoints(foundEndpoints); setCases(foundCases); setReports(foundReports);
  }, []);
  useEffect(() => { void api.listProjects().then((items) => { setProjects(items); setProject(items[0] ?? null); }).catch((e) => setNotice(errorText(e))); }, []);
  useEffect(() => { if (project) void refresh(project).catch((e) => setNotice(errorText(e))); else { setEndpoints([]); setCases([]); } }, [project, refresh]);
  useEffect(() => {
    if (!run || !["pending", "running"].includes(run.status)) return;
    const runId = run.id;
    const id = window.setInterval(() => void api.getRun(runId).then(async (next) => { setRun(next); if (!running(next)) { setResults(await api.results(next.id)); if (project) await refresh(project); } }).catch((e) => setNotice(errorText(e))), 1000);
    return () => window.clearInterval(id);
  }, [run, project, refresh]);

  async function create(event: FormEvent) {
    event.preventDefault(); setBusy(true); setNotice("");
    try { const created = await api.createProject({ name, base_url: baseUrl, description: null }); setProjects((old) => [created, ...old]); setProject(created); setName(""); const response = await api.discoverSpec(created.id); await refresh(created); setNotice(`${response.endpoints_discovered} endpoints discovered from ${response.document_url}.`); }
    catch (e) { setNotice(errorText(e)); } finally { setBusy(false); }
  }
  async function importSpec(content?: string) {
    if (!project || (!content && !specUrl)) return; setBusy(true);
    try { const response = await api.importSpec(project.id, content ? { content } : { document_url: specUrl }); await refresh(project); setNotice(`${response.endpoints_discovered} endpoints imported.`); }
    catch (e) { setNotice(errorText(e)); } finally { setBusy(false); }
  }
  async function upload(event: ChangeEvent<HTMLInputElement>) { const file = event.target.files?.[0]; if (file) await importSpec(await file.text()); event.target.value = ""; }
  async function generate() { if (!project) return; setBusy(true); try { const output = await api.generateCases(project.id); await refresh(project); setNotice(`${output.generated} tests generated.`); } catch (e) { setNotice(errorText(e)); } finally { setBusy(false); } }
  async function start() { if (!project) return; setBusy(true); try { setRun(await api.startRun(project.id)); setResults([]); } catch (e) { setNotice(errorText(e)); } finally { setBusy(false); } }

  return <main className="min-h-screen bg-slate-50"><header className="border-b bg-white"><div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4"><div><h1 className="text-2xl">Ariescan</h1><p className="text-sm text-slate-500">OpenAPI API testing workspace</p></div><a href="http://localhost:8081/docs" target="_blank" rel="noreferrer" className="btn-secondary text-sm">Swagger UI</a></div></header><div className="mx-auto grid max-w-7xl gap-6 px-5 py-6 lg:grid-cols-[280px_1fr]"><aside className="space-y-5"><section className="card"><h2 className="mb-3 text-lg">Projects</h2>{projects.map((item) => <button key={item.id} onClick={() => setProject(item)} className={`mb-2 w-full rounded-md px-3 py-2 text-left text-sm ${project?.id === item.id ? "bg-blue-600 text-white" : "hover:bg-slate-100"}`}><b className="block">{item.name}</b><span className="block truncate text-xs opacity-70">{item.base_url}</span></button>)}{!projects.length && <p className="text-sm text-slate-500">No projects yet.</p>}</section><form className="card space-y-3" onSubmit={create}><h2 className="text-lg">New project</h2><Input label="Project name" value={name} setValue={setName} required /><Input label="Target API URL" value={baseUrl} setValue={setBaseUrl} required /><button disabled={busy} className="btn-primary w-full disabled:opacity-50">Create project</button></form></aside><section className="space-y-5">{notice && <div className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">{notice}</div>}{!project ? <div className="card text-center"><h2>Create a project to begin</h2><p className="mt-2 text-slate-500">Connect a running target API and its OpenAPI document.</p></div> : <><section className="card"><div className="flex flex-wrap items-center justify-between gap-3"><div><h2>{project.name}</h2><p className="text-sm text-slate-500">Target: {project.base_url}</p></div><div className="flex gap-3"><b>{endpoints.length} endpoints</b><b>{cases.length} tests</b></div></div><div className="mt-4 grid gap-2 md:grid-cols-[1fr_auto_auto]"><input value={specUrl} onChange={(e) => setSpecUrl(e.target.value)} placeholder="OpenAPI URL, e.g. https://api.example.com/openapi.json" className="rounded-md border px-3 py-2 text-sm"/><button disabled={busy || !specUrl} onClick={() => void importSpec()} className="btn-primary disabled:opacity-50">Import URL</button><label className="btn-secondary cursor-pointer text-center">Upload OpenAPI / Postman JSON<input type="file" className="hidden" accept=".json,.yaml,.yml" onChange={upload}/></label></div><p className="mt-2 text-xs text-slate-500">Postman Documenter links are webpages. Export the Postman collection as JSON, then upload it here.</p></section><section className="card"><div className="flex flex-wrap justify-between gap-3"><div><h2>Generated test cases</h2><p className="text-sm text-slate-500">Safe, documentation-driven validation checks.</p></div><div className="flex gap-2"><button disabled={busy || !endpoints.length} onClick={() => void generate()} className="btn-secondary disabled:opacity-50">Generate</button><button disabled={busy || !cases.length || Boolean(running(run))} onClick={() => void start()} className="btn-primary disabled:opacity-50">Run tests</button></div></div><Table cases={cases} endpoints={endpoints}/></section><section className="card"><div className="flex justify-between"><div><h2>Execution results</h2><p className="text-sm text-slate-500">{run ? `${run.status} · ${run.passed_tests} passed · ${run.failed_tests} failed · ${run.error_tests} errors` : "Start a test run when ready."}</p></div>{running(run) && <button className="text-sm text-red-600" onClick={() => void api.cancelRun(run!.id).then(setRun)}>Cancel</button>}</div><Results results={results}/></section><section className="card"><h2>Reports</h2>{reports.map((item) => <div key={item.id} className="mt-2 flex justify-between rounded bg-slate-50 p-2 text-sm"><span>{item.id.slice(0, 8)} · {item.status}</span><span className="space-x-3">{(["json", "csv", "html"] as const).map((format) => <a key={format} className="text-blue-600" target="_blank" rel="noreferrer" href={api.reportUrl(item.id, format)}>{format.toUpperCase()}</a>)}</span></div>)}{!reports.length && <p className="mt-2 text-sm text-slate-500">No completed reports.</p>}</section><section className="card"><h2>Endpoint explorer</h2>{endpoints.map((endpoint) => <details key={endpoint.id} className="mt-2 rounded border p-3"><summary className="cursor-pointer"><b className="mr-2 text-blue-700">{endpoint.method}</b><code>{endpoint.path}</code> <span className="text-sm text-slate-500">{endpoint.summary}</span></summary><pre className="mt-3 overflow-auto rounded bg-slate-950 p-3 text-xs text-white">{JSON.stringify(endpoint, null, 2)}</pre></details>)}</section></>}</section></div></main>;
}

function Input({ label, value, setValue, required = false }: { label: string; value: string; setValue: (value: string) => void; required?: boolean }) { return <label className="block text-sm font-medium">{label}<input required={required} value={value} onChange={(e) => setValue(e.target.value)} className="mt-1 w-full rounded-md border px-3 py-2 font-normal"/></label>; }
function Table({ cases, endpoints }: { cases: TestCase[]; endpoints: Endpoint[] }) { return <div className="mt-4 overflow-x-auto"><table className="w-full text-left text-sm"><thead className="border-b text-slate-500"><tr><th>Endpoint</th><th>Test</th><th>Type</th></tr></thead><tbody>{cases.map((item) => <tr className="border-b" key={item.id}><td className="py-2 font-mono text-xs">{endpoints.find((endpoint) => endpoint.id === item.endpoint_id)?.path ?? "—"}</td><td>{item.name}</td><td>{item.test_type.split("_").join(" ")}</td></tr>)}{!cases.length && <tr><td colSpan={3} className="py-5 text-center text-slate-500">Import a spec and generate tests.</td></tr>}</tbody></table></div>; }
function Results({ results }: { results: TestResult[] }) { return <div className="mt-4 overflow-x-auto"><table className="w-full text-left text-sm"><thead className="border-b text-slate-500"><tr><th>Result</th><th>HTTP</th><th>Duration</th><th>Details</th></tr></thead><tbody>{results.map((item) => <tr className="border-b" key={item.id}><td className={item.status === "PASS" ? "py-2 font-bold text-emerald-600" : "py-2 font-bold text-red-600"}>{item.status}</td><td>{item.actual_status_code ?? "—"}</td><td>{item.duration_ms ?? "—"} ms</td><td>{item.error_message ?? "Matches expectation"}</td></tr>)}{!results.length && <tr><td colSpan={4} className="py-5 text-center text-slate-500">Results appear after a run finishes.</td></tr>}</tbody></table></div>; }
