export type TaobaoConfig = {
  appKey: string;
  appSecret: string;
  session: string;
  gateway?: string;
};

export type TaobaoResponse<T> = {
  data?: T;
  error?: { code?: string | number; message?: string };
  raw: unknown;
};

/**
 * Minimal TOP/淘宝官方 API client.
 *
 * Important: signing is intentionally isolated so the rest of the adapter does
 * not depend on credential handling details. Never log appSecret/session.
 */
export class TaobaoClient {
  private readonly gateway: string;

  constructor(private readonly config: TaobaoConfig) {
    this.gateway = config.gateway ?? "https://eco.taobao.com/router/rest";
  }

  async call<T>(method: string, params: Record<string, string | number | boolean> = {}): Promise<TaobaoResponse<T>> {
    const timestamp = this.formatTimestamp(new Date());
    const payload: Record<string, string> = {
      method,
      app_key: this.config.appKey,
      sign_method: "hmac",
      v: "2.0",
      format: "json",
      timestamp,
      session: this.config.session,
    };

    for (const [key, value] of Object.entries(params)) payload[key] = String(value);

    const sign = await this.sign(payload, this.config.appSecret);
    payload.sign = sign;

    const body = new URLSearchParams(payload);
    const response = await fetch(this.gateway, {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded;charset=UTF-8" },
      body,
    });

    const raw = await response.json();
    if (!response.ok) throw new Error(`Taobao HTTP ${response.status}`);

    return { raw, data: raw as T };
  }

  private async sign(params: Record<string, string>, secret: string): Promise<string> {
    const canonical = Object.keys(params).sort().map((key) => `${key}${params[key]}`).join("");
    const data = new TextEncoder().encode(canonical);
    const key = await crypto.subtle.importKey(
      "raw",
      new TextEncoder().encode(secret),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"],
    );
    const signature = await crypto.subtle.sign("HMAC", key, data);
    return Array.from(new Uint8Array(signature)).map((b) => b.toString(16).padStart(2, "0")).join("").toUpperCase();
  }

  private formatTimestamp(date: Date): string {
    const pad = (n: number) => String(n).padStart(2, "0");
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
  }
}
