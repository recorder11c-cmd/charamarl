// 会員登録・ログインAPI (Vercel KV / Upstash Redis REST)
// POST /api/auth {action:'register', name, pass}      → { ok, name }（登録＋ログイン）
// POST /api/auth {action:'login', name, pass}          → { ok, name }
// POST /api/auth {action:'logout'}                     → { ok }
// POST /api/auth {action:'sync', likes:[], saves:[]}   → { ok }（コレクション保存・要ログイン）
// POST /api/auth {action:'delete', pass}               → { ok }（退会・要ログイン）
// POST /api/auth {action:'adminpass', name, key}       → { ok, temp }（パスワード再発行・管理）
// GET  /api/auth                                       → { user:{name}, likes, saves } or { user:null }
//
// セッション: httpOnlyクッキー cm_sess（60日）。パスワードはscryptハッシュ。
//
// 2026-10-13 IPA注意喚起を受けて追加:
//   - ログイン失敗の回数制限（ニックネームごと 15分で5回 / IPごと 15分で30回）。管理者名は外から推測できるため
//   - 新規登録の回数制限（IPごと 1時間で10件）
//   - ユーザーごとのセッション一覧 usess:{key}。パスワード変更・再発行・退会・管理削除で他のセッションを全部切る

const crypto = require('crypto');

const KV_URL = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const KV_TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;
const SESS_TTL = 60 * 60 * 24 * 60; // 60日

async function redis(...cmd) {
  const res = await fetch(KV_URL, {
    method: 'POST',
    headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(cmd),
  });
  if (!res.ok) throw new Error(`KV error ${res.status}`);
  return (await res.json()).result;
}

const { overLimit, peekLimit, clearLimit, clientIp, safeEqual, audit } = require('./_lib/admin.js');
const hashPass = (pass, salt) => crypto.scryptSync(pass, salt, 64).toString('hex');
const passOk = (pass, obj) => !!(obj && obj.hash && obj.salt) && safeEqual(hashPass(String(pass || ''), obj.salt), obj.hash);

const LOGIN_FAIL_NAME = 5, LOGIN_FAIL_IP = 30, LOGIN_WINDOW = 15 * 60;
const REGISTER_IP = 10, REGISTER_WINDOW = 60 * 60;
const nameKey = n => String(n).trim().toLowerCase();
const validName = n => /^[^\s\/\\<>"'`]{2,20}$/.test(n);

function getSession(req) {
  const m = /(?:^|;\s*)cm_sess=([a-f0-9]{48})/.exec(req.headers.cookie || '');
  return m ? m[1] : null;
}
function setCookie(res, token, maxAge) {
  res.setHeader('Set-Cookie',
    `cm_sess=${token}; Path=/; HttpOnly; SameSite=Lax; Secure; Max-Age=${maxAge}`);
}
async function currentUser(req) {
  const token = getSession(req);
  if (!token) return null;
  const key = await redis('GET', `sess:${token}`);
  if (!key) return null;
  const name = await redis('HGET', `user:${key}`, 'name');
  return name ? { key, name, token } : null;
}
async function createSession(res, key) {
  const token = crypto.randomBytes(24).toString('hex');
  await redis('SET', `sess:${token}`, key, 'EX', String(SESS_TTL));
  await redis('SADD', `usess:${key}`, token);
  await redis('EXPIRE', `usess:${key}`, String(SESS_TTL));
  setCookie(res, token, SESS_TTL);
  return token;
}
// そのユーザーのセッションを（except 以外）すべて無効にする
async function killSessions(key, except) {
  const tokens = (await redis('SMEMBERS', `usess:${key}`)) || [];
  // 2026-10-13 以前のセッションは usess に載っていないので、sess:* を走査して拾う（変更・再発行時だけなので頻度は低い）
  let cursor = '0';
  do {
    const r = await redis('SCAN', cursor, 'MATCH', 'sess:*', 'COUNT', '500');
    cursor = String(r[0]);
    const ks = r[1] || [];
    if (ks.length) {
      const vals = await redis('MGET', ...ks);
      ks.forEach((k, i) => { if (vals[i] === key) { const t = k.slice(5); if (!tokens.includes(t)) tokens.push(t); } });
    }
  } while (cursor !== '0');
  const dead = tokens.filter(t => t !== except);
  if (dead.length) {
    await redis('DEL', ...dead.map(t => `sess:${t}`));
    await redis('SREM', `usess:${key}`, ...dead);
  }
}

module.exports = async (req, res) => {
  if (!KV_URL || !KV_TOKEN) return res.status(503).json({ error: 'KV未設定' });

  try {
    // 管理者セッションで開いたときは key が空文字で来る。'||' で判定すると空文字が偽になり
    // この分岐に入らず、ユーザー一覧が黙って空で返ってしまうため「パラメータの有無」で判定する。
    // 管理用: 操作ログ（_lib/admin.js が記録する audit:log の新しい200件）
    if (req.method === 'GET' && req.query && 'audit' in req.query) {
      const { isAdminReq } = require('./_lib/admin.js');
      if (!(await isAdminReq(req))) return res.status(403).json({ error: 'forbidden' });
      const raw = (await redis('LRANGE', 'audit:log', '0', '199')) || [];
      const list = raw.map(x => { try { return JSON.parse(x); } catch { return null; } }).filter(Boolean);
      return res.status(200).json({ count: list.length, list });
    }

    if (req.method === 'GET' && req.query && ('key' in req.query || 'users' in req.query)) {
      // 管理用: 登録ユーザー一覧（APPLY_KEY または 管理者セッション）
      const { isAdminReq } = require('./_lib/admin.js');
      if (!(await isAdminReq(req))) {
        return res.status(403).json({ error: 'forbidden' });
      }
      let cursor = '0'; const keys = [];
      do {
        const r = await redis('SCAN', cursor, 'MATCH', 'user:*', 'COUNT', '200');
        cursor = String(r[0]);
        for (const k of r[1]) if (!k.endsWith(':col')) keys.push(k);
      } while (cursor !== '0');
      const users = [];
      for (const k of keys) {
        const [name, created, lastLogin] = await Promise.all([
          redis('HGET', k, 'name'), redis('HGET', k, 'created'), redis('HGET', k, 'lastLogin'),
        ]);
        users.push({ name, created: Number(created) || 0, lastLogin: Number(lastLogin) || 0 });
      }
      users.sort((a, b) => b.created - a.created);
      return res.status(200).json({ count: users.length, users });
    }

    if (req.method === 'GET') {
      const u = await currentUser(req);
      if (!u) return res.status(200).json({ user: null });
      const { ADMIN_USERS } = require('./_lib/admin.js');
      const col = await redis('GET', `user:${u.key}:col`);
      const { likes = [], saves = [] } = col ? JSON.parse(col) : {};
      return res.status(200).json({ user: { name: u.name, admin: ADMIN_USERS.includes(u.key) }, likes, saves });
    }

    if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' });
    const b = req.body || {};

    if (b.action === 'register') {
      if (await overLimit(`register:${clientIp(req)}`, REGISTER_IP, REGISTER_WINDOW)) {
        return res.status(429).json({ error: '登録が集中しています。しばらくしてからお試しください' });
      }
      const name = String(b.name || '').trim();
      if (!validName(name)) return res.status(400).json({ error: 'ニックネームは2〜20文字（空白・記号の一部は不可）' });
      if (String(b.pass || '').length < 8) return res.status(400).json({ error: 'パスワードは8文字以上にしてください' });
      const key = nameKey(name);
      const exists = await redis('EXISTS', `user:${key}`);
      if (Number(exists)) return res.status(409).json({ error: 'そのニックネームは使われています' });
      const salt = crypto.randomBytes(16).toString('hex');
      await redis('HSET', `user:${key}`, 'name', name, 'salt', salt, 'hash', hashPass(b.pass, salt), 'created', String(Date.now()));
      await createSession(res, key);
      return res.status(200).json({ ok: true, name });
    }

    if (b.action === 'login') {
      const key = nameKey(String(b.name || ''));
      const ip = clientIp(req);
      // 総当たり対策: 失敗が続いたニックネーム / IP は一定時間ログインさせない（正しいパスワードでも）
      if (await peekLimit(`login:name:${key}`, LOGIN_FAIL_NAME) || await peekLimit(`login:ip:${ip}`, LOGIN_FAIL_IP)) {
        if (require('./_lib/admin.js').ADMIN_USERS.includes(key)) await audit(req, 'blocked', 'admin login lockout');
        return res.status(429).json({ error: 'ログインの失敗が続いたため、15分ほど待ってからお試しください' });
      }
      const u = await redis('HGETALL', `user:${key}`);
      // Upstashは ["field","value",...] 配列で返す
      const obj = {}; for (let i = 0; u && i < u.length; i += 2) obj[u[i]] = u[i + 1];
      if (!passOk(b.pass, obj)) {
        await overLimit(`login:name:${key}`, LOGIN_FAIL_NAME, LOGIN_WINDOW);
        await overLimit(`login:ip:${ip}`, LOGIN_FAIL_IP, LOGIN_WINDOW);
        if (require('./_lib/admin.js').ADMIN_USERS.includes(key)) await audit(req, 'denied', 'admin login failed');
        return res.status(401).json({ error: 'ニックネームかパスワードが違います' });
      }
      await clearLimit(`login:name:${key}`);
      if (require('./_lib/admin.js').ADMIN_USERS.includes(key)) await audit(req, 'login:' + key);
      // 最終ログインを残す。作家さんがダッシュボードを見ているかを知るため
      // （2026-09-21 追加。それまで created しか無く、誰が一度も入っていないか分からなかった）
      await redis('HSET', `user:${key}`, 'lastLogin', String(Date.now()));
      await createSession(res, key);
      return res.status(200).json({ ok: true, name: obj.name });
    }

    if (b.action === 'logout') {
      const token = getSession(req);
      if (token) {
        const k = await redis('GET', `sess:${token}`);
        await redis('DEL', `sess:${token}`);
        if (k) await redis('SREM', `usess:${k}`, token);
      }
      setCookie(res, 'x', 0);
      return res.status(200).json({ ok: true });
    }

    // 管理用: パスワードの再発行（本人が忘れた場合）
    // 仮パスワードを発行して返すだけ。本人には「ログインしたら必ず変えてください」と伝える。
    // ⚠️ 作品や♥・保存はそのまま残る（アカウントを作り直さないため）。
    if (b.action === 'adminpass') {
      const { isAdminReq } = require('./_lib/admin.js');
      if (!(await isAdminReq(req))) return res.status(403).json({ error: 'forbidden' });
      const key = nameKey(String(b.name || ''));
      if (!key) return res.status(400).json({ error: 'name が必要です' });
      if (!Number(await redis('EXISTS', `user:${key}`))) return res.status(404).json({ error: 'そのアカウントはありません' });
      const temp = crypto.randomBytes(6).toString('base64url'); // 8文字
      const salt = crypto.randomBytes(16).toString('hex');
      await redis('HSET', `user:${key}`, 'salt', salt, 'hash', hashPass(temp, salt));
      await killSessions(key, null);           // 乗っ取られていた場合に備え、既存のログインを全部切る
      await clearLimit(`login:name:${key}`);
      return res.status(200).json({ ok: true, name: key, temp });
    }

    // 管理用: アカウント削除（代行用の仮アカウントの後始末など）
    // 本人のパスワードは不要。APPLY_KEY か管理者セッションが必要。
    if (b.action === 'admindel') {
      const { isAdminReq } = require('./_lib/admin.js');
      if (!(await isAdminReq(req))) return res.status(403).json({ error: 'forbidden' });
      const key = nameKey(String(b.name || ''));
      if (!key) return res.status(400).json({ error: 'name が必要です' });
      if (!Number(await redis('EXISTS', `user:${key}`))) return res.status(404).json({ error: 'そのアカウントはありません' });
      await killSessions(key, null);
      await redis('DEL', `user:${key}`, `user:${key}:col`, `usess:${key}`);
      return res.status(200).json({ ok: true, deleted: key });
    }

    // 以下は要ログイン
    const u = await currentUser(req);
    if (!u) return res.status(401).json({ error: 'ログインしてください' });

    if (b.action === 'passwd') { // パスワード変更
      const raw = await redis('HGETALL', `user:${u.key}`);
      const obj = {}; for (let i = 0; raw && i < raw.length; i += 2) obj[raw[i]] = raw[i + 1];
      if (!passOk(b.old, obj)) {
        return res.status(401).json({ error: '現在のパスワードが違います' });
      }
      if (String(b.new || '').length < 8) return res.status(400).json({ error: '新しいパスワードは8文字以上にしてください' });
      const salt = crypto.randomBytes(16).toString('hex');
      await redis('HSET', `user:${u.key}`, 'salt', salt, 'hash', hashPass(b.new, salt));
      await killSessions(u.key, u.token);      // この端末以外のログインを切る
      return res.status(200).json({ ok: true });
    }

    if (b.action === 'sync') {
      const clean = a => [...new Set((Array.isArray(a) ? a : []).map(s => String(s).slice(0, 30)))].slice(0, 200);
      await redis('SET', `user:${u.key}:col`, JSON.stringify({ likes: clean(b.likes), saves: clean(b.saves) }));
      return res.status(200).json({ ok: true });
    }

    if (b.action === 'delete') {
      const obj = {}; const raw = await redis('HGETALL', `user:${u.key}`);
      for (let i = 0; raw && i < raw.length; i += 2) obj[raw[i]] = raw[i + 1];
      if (!passOk(b.pass, obj)) return res.status(401).json({ error: 'パスワードが違います' });
      await killSessions(u.key, null);
      await redis('DEL', `user:${u.key}`, `user:${u.key}:col`, `sess:${u.token}`, `usess:${u.key}`);
      setCookie(res, 'x', 0);
      return res.status(200).json({ ok: true });
    }

    return res.status(400).json({ error: 'bad action' });
  } catch (e) {
    return require('./_lib/admin.js').serverError(res, e, 'auth.js');
  }
};
