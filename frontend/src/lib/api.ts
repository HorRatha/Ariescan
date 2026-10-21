import { env } from "./env";

export type Project = {
  id: string;
  name: string;
  base_url: string;
  description: string | null;
  created_at: string;
  updated_at: string;
};

export type Endpoint = {
  id: string;
  method: string;
  path: string;
  summary: string | null;
  parameters: Array<Record<string, unknown>>;
  request_schema: Record<string, unknown> | null;
  response_schemas: Record<string, Record<string, unknown>>;
};

export type TestCase = {
  id: string;
  endpoint_id: string;
  name: string;
  test_type: string;
  enabled: boolean;
};

export type TestRun = {
  id: string;
  project_id: string;
  status: "pending" | "running" | "completed" | "cancelled";
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  error_tests: number;
  started_at: string | null;
  finished_at: string | null;
};

export type TestResult = {
  id: string;
  test_case_id: string;
  status: "PASS" | "FAIL" | "ERROR" | "SKIPPED";
  actual_status_code: number | null;
  expected_result: Record<string, unknown>;
  actual_result: Record<string, unknown>;
  error_message: string | null;
  duration_ms: number | null;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${env.apiUrl}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail || `Request failed (${response.status})`);
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

export const api = {
  listProjects: () => request<Project[]>("/api/projects"),
  createProject: (data: Pick<Project, "name" | "base_url" | "description">) =>
    request<Project>("/api/projects", { method: "POST", body: JSON.stringify(data) }),
  deleteProject: (id: string) => request<void>(`/api/projects/${id}`, { method: "DELETE" }),
  importSpec: (id: string, data: { document_url?: string; content?: string }) =>
    request<{ title: string; version: string; endpoints_discovered: number }>(
      `/api/projects/${id}/specs/import`,
      { method: "POST", body: JSON.stringify(data) },
    ),
  discoverSpec: (id: string) => request<{ title: string; version: string; endpoints_discovered: number; document_url: string }>(
    `/api/projects/${id}/specs/discover`,
    { method: "POST" },
  ),
  endpoints: (id: string) => request<Endpoint[]>(`/api/projects/${id}/endpoints`),
  testCases: (id: string) => request<TestCase[]>(`/api/projects/${id}/test-cases`),
  generateCases: (id: string) => request<{ generated: number }>(`/api/projects/${id}/test-cases/generate`, { method: "POST" }),
  startRun: (id: string) => request<TestRun>(`/api/projects/${id}/test-runs`, { method: "POST" }),
  getRun: (id: string) => request<TestRun>(`/api/test-runs/${id}`),
  results: (id: string) => request<TestResult[]>(`/api/test-runs/${id}/results`),
  cancelRun: (id: string) => request<TestRun>(`/api/test-runs/${id}/cancel`, { method: "POST" }),
  reports: (id: string) => request<TestRun[]>(`/api/projects/${id}/reports`),
  reportUrl: (id: string, format: "json" | "csv" | "html") => `${env.apiUrl}/api/test-runs/${id}/report.${format}`,
};
