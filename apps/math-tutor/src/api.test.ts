import { describe, expect, it, vi } from "vitest";
import { fetchApiHealth } from "./api";

describe("fetchApiHealth", () => {
  it("returns validated health data from the backend", async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(
        JSON.stringify({
          ok: true,
          service: "math-tutor-api",
          storage: "sqlite",
          schema_version: "1",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );

    await expect(fetchApiHealth(fetcher)).resolves.toEqual({
      ok: true,
      service: "math-tutor-api",
      storage: "sqlite",
      schema_version: "1",
    });
    expect(fetcher).toHaveBeenCalledWith("/api/health", {
      headers: { Accept: "application/json" },
    });
  });

  it("surfaces HTTP errors instead of treating them as connected", async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(
      new Response("unavailable", { status: 503 }),
    );

    await expect(fetchApiHealth(fetcher)).rejects.toThrow("HTTP 503");
  });

  it("rejects malformed payloads", async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), { status: 200 }),
    );

    await expect(fetchApiHealth(fetcher)).rejects.toThrow("数据格式不正确");
  });
});
