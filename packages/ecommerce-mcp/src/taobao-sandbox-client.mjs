import { createHmac } from 'node:crypto';

const API_URL = process.env.TAOBAO_SANDBOX_API_URL || 'https://gw.api.tbsandbox.com/router/rest';
const APP_KEY = process.env.TAOBAO_SANDBOX_APP_KEY || 'test';
const APP_SECRET = process.env.TAOBAO_SANDBOX_APP_SECRET || 'test';

// Alibaba's official sandbox document publishes this example access token.
// It is only a fallback for sandbox testing; override it with a fresh token
// when the sandbox token has expired.
const DOCUMENTED_SANDBOX_ACCESS_TOKEN =
  '620101925972b8f5b3c3bfb9bcdfhb722b64a660ce34e732074082786';

const ACCESS_TOKEN =
  process.env.TAOBAO_SANDBOX_ACCESS_TOKEN || DOCUMENTED_SANDBOX_ACCESS_TOKEN;

function hmacSign(params, secret) {
  const base = Object.keys(params)
    .filter((key) => key !== 'sign')
    .sort()
    .map((key) => key + String(params[key]))
    .join('');
  return createHmac('sha256', secret).update(base, 'utf8').digest('hex').toUpperCase();
}

async function callApi(method, params = {}) {
  const body = new URLSearchParams({
    app_key: APP_KEY,
    format: 'json',
    method,
    v: '2.0',
    ...params,
  });

  // The sandbox OAuth example uses access_token directly.
  if (ACCESS_TOKEN) body.set('access_token', ACCESS_TOKEN);

  const response = await fetch(API_URL, {
    method: 'POST',
    headers: {
      accept: 'application/json',
      'content-type': 'application/x-www-form-urlencoded;charset=utf-8',
    },
    body,
  });

  const text = await response.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    data = { raw: text };
  }

  const error =
    data?.error_response ||
    data?.error ||
    data?.sub_code ||
    null;

  return {
    method,
    httpStatus: response.status,
    transportOk: response.ok,
    apiOk: !error,
    error,
    data,
  };
}

function countPayload(data) {
  const response = Object.values(data || {}).find(
    (value) => value && typeof value === 'object' && !Array.isArray(value)
  );
  if (!response) return 0;
  const candidates = ['items', 'trades', 'orders', 'users', 'shops'];
  for (const key of candidates) {
    const value = response[key];
    if (Array.isArray(value)) return value.length;
    if (value && Array.isArray(value[key])) return value[key].length;
  }
  return response.item || response.trade || response.user || response.shop ? 1 : 0;
}

async function runSuite() {
  const results = [];

  // 1. Identity
  results.push(await callApi('taobao.user.get', {
    fields: 'user_id,uid,nick,sex',
    nick: 'sandbox_c_1',
  }));

  // 2. Shop
  results.push(await callApi('taobao.shop.get', {
    fields: 'sid,cid,title,desc,bulletin,pic_path,created,modified',
  }));

  // 3. On-sale inventory
  const onsale = await callApi('taobao.items.onsale.get', {
    fields: 'num_iid,title,price,num,approve_status',
    page_no: '1',
    page_size: '40',
  });
  results.push(onsale);

  // 4. Inventory
  results.push(await callApi('taobao.items.inventory.get', {
    fields: 'num_iid,title,price,num,approve_status',
    page_no: '1',
    page_size: '40',
  }));

  // 5. Sold trades
  const trades = await callApi('taobao.trades.sold.get', {
    fields: 'tid,type,status,created,modified,payment,orders',
    page_no: '1',
    page_size: '40',
  });
  results.push(trades);

  // 6. Incremental trades: one-day real sandbox window.
  const end = new Date();
  const start = new Date(end.getTime() - 24 * 60 * 60 * 1000);
  const fmt = (d) => d.toISOString().slice(0, 19).replace('T', ' ');
  results.push(await callApi('taobao.trades.sold.increment.get', {
    fields: 'tid,type,status,created,modified,payment',
    start_modified: fmt(start),
    end_modified: fmt(end),
    page_no: '1',
    page_size: '40',
  }));

  // 7. Enrich the first real item returned by sandbox.
  const item =
    onsale.data?.items_onsale_get_response?.items?.item?.[0] ||
    onsale.data?.items_onsale_get_response?.items?.item?.[0];
  const numIid = item?.num_iid || item?.numIid;
  if (numIid) {
    results.push(await callApi('taobao.item.get', {
      fields: 'num_iid,title,price,num,sku,props,desc_modules,sell_point',
      num_iid: String(numIid),
    }));
  }

  // 8. Enrich the first real trade returned by sandbox.
  const trade =
    trades.data?.trades_sold_get_response?.trades?.trade?.[0];
  const tid = trade?.tid;
  if (tid) {
    results.push(await callApi('taobao.trade.fullinfo.get', {
      fields: 'tid,type,status,payment,orders,promotion_details',
      tid: String(tid),
    }));
  }

  const failed = results.filter((r) => !r.apiOk);
  const passed = results.length - failed.length;

  return {
    endpoint: API_URL,
    sandbox: true,
    appKey: APP_KEY,
    accessTokenSource: process.env.TAOBAO_SANDBOX_ACCESS_TOKEN
      ? 'environment'
      : 'official-document-example',
    calls: results.map((r) => ({
      method: r.method,
      httpStatus: r.httpStatus,
      transportOk: r.transportOk,
      apiOk: r.apiOk,
      recordCount: countPayload(r.data),
      error: r.error,
    })),
    passed,
    failed: failed.length,
    total: results.length,
    raw: results,
  };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  runSuite()
    .then((report) => {
      // Never print access tokens.
      console.log(JSON.stringify(report, null, 2));
      process.exitCode = report.failed === 0 ? 0 : 1;
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

export { callApi, runSuite };
