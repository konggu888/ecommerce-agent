const API_URL = process.env.TAOBAO_SANDBOX_API_URL || 'https://gw.api.tbsandbox.com/router/rest';
const APP_KEY = process.env.TAOBAO_SANDBOX_APP_KEY || 'test';
const APP_SECRET = process.env.TAOBAO_SANDBOX_APP_SECRET || 'test';

/**
 * Official Taobao sandbox connectivity client.
 *
 * Defaults intentionally use Alibaba's documented sandbox test credentials:
 * appkey=test, secret=test.
 * For authenticated APIs, TAOBAO_SANDBOX_SESSION must be a real sandbox
 * SessionKey/AccessToken obtained from sandbox OAuth; it must not be guessed.
 */

function signTopRequest(params, secret) {
  const keys = Object.keys(params).sort();
  const base = keys.map((key) => key + String(params[key])).join('');
  return require('node:crypto')
    .createHmac('sha256', secret)
    .update(base, 'utf8')
    .digest('hex')
    .toUpperCase();
}

export async function callTaobaoSandbox({
  method = 'taobao.user.get',
  fields = 'nick',
  nick = 'sandbox_c_1',
  session = process.env.TAOBAO_SANDBOX_SESSION,
} = {}) {
  const timestamp = new Date().toISOString().replace(/[-:TZ.]/g, '').slice(0, 14);

  const params = {
    app_key: APP_KEY,
    format: 'json',
    method,
    sign_method: 'hmac-sha256',
    timestamp,
    v: '2.0',
    fields,
    nick,
  };

  if (session) params.session = session;

  params.sign = signTopRequest(params, APP_SECRET);

  const url = new URL(API_URL);
  Object.entries(params).forEach(([key, value]) => url.searchParams.set(key, value));

  const response = await fetch(url, {
    method: 'GET',
    headers: { accept: 'application/json' },
  });

  const text = await response.text();
  let body;
  try {
    body = JSON.parse(text);
  } catch {
    body = { raw: text };
  }

  return {
    ok: response.ok,
    httpStatus: response.status,
    endpoint: API_URL,
    appKey: APP_KEY,
    authenticated: Boolean(session),
    body,
  };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  callTaobaoSandbox()
    .then((result) => {
      console.log(JSON.stringify(result, null, 2));
      process.exitCode = result.ok ? 0 : 1;
    })
    .catch((error) => {
      console.error(JSON.stringify({
        ok: false,
        endpoint: API_URL,
        error: error instanceof Error ? error.message : String(error),
      }, null, 2));
      process.exitCode = 1;
    });
}
