// 管理者判定の共通ヘルパー
// ・APPLY_KEY（クエリ or ボディ）での認証（従来どおり）
// ・またはログインセッションが管理者アカウントなら許可
const KV_URL = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const KV_TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;

const ADMIN_USERS = ['ahoyoung']; // 管理者アカウント（ニックネーム小文字）

async function redis(...cmd) {
  const res = await fetch(KV_URL, {
    method: 'POST',
    headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(cmd),
  });
  if (!res.ok) throw new Error(`KV error ${res.status}`);
  return (await res.json()).result;
}

async function sessionUserKey(req) {
  const m = /(?:^|;\s*)cm_sess=([a-f0-9]{48})/.exec(req.headers.cookie || '');
  if (!m) return null;
  return await redis('GET', `sess:${m[1]}`);
}

async function isAdminReq(req) {
  const q = req.query || {};
  const bodyKey = req.body && req.body.key;
  if (process.env.APPLY_KEY && (q.key === process.env.APPLY_KEY || bodyKey === process.env.APPLY_KEY)) return true;
  const userKey = await sessionUserKey(req);
  return ADMIN_USERS.includes(String(userKey || ''));
}

module.exports = { isAdminReq, ADMIN_USERS, sessionUserKey };
