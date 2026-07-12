// 会員登録・ログインAPI (Vercel KV / Upstash Redis REST)
// POST /api/auth {action:'register', name, pass}      → { ok, name }（登録＋ログイン）
// POST /api/auth {action:'login', name, pass}          → { ok, name }
// POST /api/auth {action:'logout'}                     → { ok }
// POST /api/auth {action:'sync', likes:[], saves:[]}   → { ok }（コレクション保存・要ログイン）
// POST /api/auth {action:'delete', pass}               → { ok }（退会・要ログイン）
// GET  /api/auth                                       → { user:{name}, likes, saves } or { user:null }
//
// セッション: httpOnlyクッキー cm_sess（60日）。パスワードはscryptハッシュ。

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

const hashPass = (pass, salt) => crypto.scryptSync(pass, salt, 64).toString('hex');
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
  setCookie(res, token, SESS_TTL);
}

module.exports = async (req, res) => {
  if (!KV_URL || !KV_TOKEN) return res.status(503).json({ error: 'KV未設定' });

  try {
    if (req.method === 'GET') {
      const u = await currentUser(req);
      if (!u) return res.status(200).json({ user: null });
      const col = await redis('GET', `user:${u.key}:col`);
      const { likes = [], saves = [] } = col ? JSON.parse(col) : {};
      return res.status(200).json({ user: { name: u.name }, likes, saves });
    }

    if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' });
    const b = req.body || {};

    if (b.action === 'register') {
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
      const u = await redis('HGETALL', `user:${key}`);
      // Upstashは ["field","value",...] 配列で返す
      const obj = {}; for (let i = 0; u && i < u.length; i += 2) obj[u[i]] = u[i + 1];
      if (!obj.hash || hashPass(String(b.pass || ''), obj.salt) !== obj.hash) {
        return res.status(401).json({ error: 'ニックネームかパスワードが違います' });
      }
      await createSession(res, key);
      return res.status(200).json({ ok: true, name: obj.name });
    }

    if (b.action === 'logout') {
      const token = getSession(req);
      if (token) await redis('DEL', `sess:${token}`);
      setCookie(res, 'x', 0);
      return res.status(200).json({ ok: true });
    }

    // 以下は要ログイン
    const u = await currentUser(req);
    if (!u) return res.status(401).json({ error: 'ログインしてください' });

    if (b.action === 'sync') {
      const clean = a => [...new Set((Array.isArray(a) ? a : []).map(s => String(s).slice(0, 30)))].slice(0, 200);
      await redis('SET', `user:${u.key}:col`, JSON.stringify({ likes: clean(b.likes), saves: clean(b.saves) }));
      return res.status(200).json({ ok: true });
    }

    if (b.action === 'delete') {
      const obj = {}; const raw = await redis('HGETALL', `user:${u.key}`);
      for (let i = 0; raw && i < raw.length; i += 2) obj[raw[i]] = raw[i + 1];
      if (hashPass(String(b.pass || ''), obj.salt) !== obj.hash) return res.status(401).json({ error: 'パスワードが違います' });
      await redis('DEL', `user:${u.key}`, `user:${u.key}:col`, `sess:${u.token}`);
      setCookie(res, 'x', 0);
      return res.status(200).json({ ok: true });
    }

    return res.status(400).json({ error: 'bad action' });
  } catch (e) {
    return res.status(500).json({ error: String((e && e.message) || e) });
  }
};
