export type TaobaoOAuthConfig = {
  appKey: string;
  redirectUri: string;
  authorizeUrl?: string;
};

/** Builds the official Taobao OAuth authorization URL. */
export function buildTaobaoAuthorizeUrl(config: TaobaoOAuthConfig, state: string): string {
  const url = new URL(config.authorizeUrl ?? "https://oauth.taobao.com/authorize");
  url.searchParams.set("response_type", "code");
  url.searchParams.set("client_id", config.appKey);
  url.searchParams.set("redirect_uri", config.redirectUri);
  url.searchParams.set("state", state);
  return url.toString();
}
