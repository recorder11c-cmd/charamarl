// 管理者判定・回数制限・監査ログの共通ヘルパー（サーバー側だけで使う）
// 🔴 api/_lib/ に置いている。_ で始まるフォルダは Vercel がルートにも静的配信にもしないため。
//    2026-09-21 まで lib/admin.js にあり、https://charamarl.com/lib/admin.js で誰でも読めていた。
//    秘密の値は入っていなかったが、認証の経路と管理者名が外から見える状態だった。
//
// 2026-10-13 IPA注意喚起（不正アクセスによる漏えい事案）を受けて強化:
//   - キーは X-Admin-Key ヘッダーを優先。URL(?key=)はアクセスログ・履歴に残るので非推奨（互換のため当面は受ける）
//   - 比較は timingSafeEqual（定数時間）
//   - キーの間違いが IP ごとに 15分で10回を超えたら、その IP からのキー認証を止める（総当たり対策）
//   - 管理操作は audit:log に記録（誰が・いつ・どこから・何を）。apply-admin の「操作ログ」で見られる
//   - 全 API のキー判定をここに集約（以前は gallery / n / run-score / coupon が個別に q.key === APPLY_KEY を見ていた）
const crypto = require('crypto');

const KV_URL = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const KV_TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;

const ADMIN_USERS = ['ahoyoung']; // 管理者アカウント（ニックネーム小文字）

const KEY_FAIL_LIMIT = 10;        // キー間違いの許容回数
const KEY_FAIL_WINDOW = 15 * 60;  // 秒
const AUDIT_MAX = 2000;           // 監査ログの保持件数

async function redis(...cmd) {
  const res = await fetch(KV_URL, {
    method: 'POST',
    headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(cmd),
  });
  if (!res.ok) throw new Error(`KV error ${res.status}`);
  return (await res.json()).result;
}

function clientIp(req) {
  const h = req.headers || {};
  const v = h['x-real-ip'] || h['x-vercel-forwarded-for'] || h['x-forwarded-for'] || '';
  return String(v).split(',')[0].trim().slice(0, 64) || 'unknown';
}

// 定数時間比較（長さが違っても時間差が出ないようにハッシュしてから比べる）
function safeEqual(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string' || !a || !b) return false;
  const ha = crypto.createHash('sha256').update(a).digest();
  const hb = crypto.createHash('sha256').update(b).digest();
  return crypto.timingSafeEqual(ha, hb);
}

// リクエストに付いてきた管理キー（ヘッダー > body > URL）。無ければ ''
function suppliedKey(req) {
  const h = (req.headers || {})['x-admin-key'];
  if (h) return String(h);
  let b = req.body;
  if (typeof b === 'string') { try { b = JSON.parse(b || '{}'); } catch { b = {}; } }
  if (b && b.key) return String(b.key);
  const q = req.query || {};
  if (q.key) return String(q.key);
  return '';
}

// 汎用の回数制限。窓の中で limit を超えたら true（=止める）
async function overLimit(bucket, limit, windowSec) {
  const k = `rl:${bucket}`;
  const n = Number(await redis('INCR', k));
  if (n === 1) await redis('EXPIRE', k, String(windowSec));
  return n > limit;
}
async function peekLimit(bucket, limit) {
  const n = Number(await redis('GET', `rl:${bucket}`)) || 0;
  return n >= limit;
}
async function clearLimit(bucket) { await redis('DEL', `rl:${bucket}`); }

async function sessionUserKey(req) {
  const m = /(?:^|;\s*)cm_sess=([a-f0-9]{48})/.exec((req.headers && req.headers.cookie) || '');
  if (!m) return null;
  return await redis('GET', `sess:${m[1]}`);
}

async function audit(req, via, note) {
  try {
    const entry = {
      ts: Date.now(), via, ip: clientIp(req), method: req.method,
      path: String(req.url || '').split('?')[0].slice(0, 100),
      action: (req.body && typeof req.body === 'object' && req.body.action) ? String(req.body.action).slice(0, 30) : undefined,
      note: note ? String(note).slice(0, 200) : undefined,
      ua: String((req.headers || {})['user-agent'] || '').slice(0, 120),
    };
    await redis('LPUSH', 'audit:log', JSON.stringify(entry));
    await redis('LTRIM', 'audit:log', '0', String(AUDIT_MAX - 1));
  } catch (_) { /* ログ失敗で本処理は止めない */ }
}

async function isAdminReq(req) {
  const ip = clientIp(req);
  const key = suppliedKey(req);
  const master = process.env.APPLY_KEY;
  if (key && master) {
    // 総当たり中の IP は、正しいキーでも通さない
    if (await peekLimit(`adminkey:${ip}`, KEY_FAIL_LIMIT)) { await audit(req, 'blocked', 'key lockout'); return false; }
    if (safeEqual(key, master)) { await audit(req, 'key'); return true; }
    await overLimit(`adminkey:${ip}`, KEY_FAIL_LIMIT, KEY_FAIL_WINDOW);
    await audit(req, 'denied', 'wrong key');
    // キーが違っても、管理者セッションがあればそちらで判定を続ける
  }
  const userKey = await sessionUserKey(req);
  if (ADMIN_USERS.includes(String(userKey || ''))) { await audit(req, 'session:' + userKey); return true; }
  return false;
}

// 500 を返すときに内部のエラー文を外へ出さない
function serverError(res, e, where) {
  console.error(`[${where || 'api'}]`, e);
  return res.status(500).json({ error: 'サーバーでエラーが起きました。時間をおいてもう一度お試しください' });
}

module.exports = {
  isAdminReq, ADMIN_USERS, sessionUserKey, clientIp, overLimit, peekLimit, clearLimit,
  safeEqual, audit, serverError, redis,
};
