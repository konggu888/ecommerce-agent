export interface ApiHealth {
  ok: boolean;
  service: string;
  storage: string;
  schema_version: string;
}

export type ApiConnectionState =
  | { status: "checking" }
  | { status: "connected"; health: ApiHealth }
  | { status: "unavailable"; message: string };

export async function fetchApiHealth(
  fetcher: typeof fetch = fetch,
  endpoint = "/api/health",
): Promise<ApiHealth> {
  const response = await fetcher(endpoint, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error(`API 请求失败（HTTP ${response.status}）`);
  }

  const payload: unknown = await response.json();
  if (
    typeof payload !== "object" ||
    payload === null ||
    !("ok" in payload) ||
    payload.ok !== true ||
    !("service" in payload) ||
    typeof payload.service !== "string" ||
    !("storage" in payload) ||
    typeof payload.storage !== "string" ||
    !("schema_version" in payload) ||
    typeof payload.schema_version !== "string"
  ) {
    throw new Error("API 返回的数据格式不正确");
  }

  return payload as ApiHealth;
}
