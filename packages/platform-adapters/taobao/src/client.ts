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

/** Minimal TOP client for the official Taobao API. */
export class TaobaoClient {
  private readonly gateway: string;

  constructor(private readonly config: TaobaoConfig) {
    this.gateway = config.gateway ?? "https://eco.taobao.com/router/rest";
  }

  async call<T>(method: string, params: Record<string, string | number | boolean> = {}): Promise<TaobaoResponse<T>> {
    const payload: Record<string, string> = {
      method,
      app_key: this.config.appKey,
      sign_method: "hmac-sha256",
      v: "2.0",
      format: "json",
      timestamp: this.formatTimestamp(new Date()),
      session: this.config.session,
    };
    for (const [key, value] of Object.entries(params)) payload[key] = String(value);

    payload.sign = await this.sign(payload, this.config.appSecret);
    const response = await fetch(this.gateway, {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded;charset=UTF-8" },
      body: new URLSearchParams(payload),
    });
    const raw = await response.json();
    if (!response.ok) throw new Error(`Taobao HTTP ${response.status}`);
    return { raw, data: raw as T };
  }

  private async sign(params: Record<string, string>, secret: string): Promise<string> {
    const canonical = Object.keys(params).sort().map((key) => `${key}${params[key]}`).join("");
    const key = await crypto.subtle.importKey(
      "raw",
      new TextEncoder().encode(secret),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"],
    );
    const signature = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(canonical));
    return Array.from(new Uint8Array(signature)).map((b) => b.toString(16).padStart(2, "0")).join("").toUpperCase();
  }

  private formatTimestamp(date: Date): string {
    const pad = (n: number) => String(n).padStart(2, "0");
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
  }
}
