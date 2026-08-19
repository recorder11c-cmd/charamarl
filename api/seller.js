// 販売者情報（お支払い先）API (Upstash Redis REST)
// POST /api/seller {action:'save', sellerName, email, bank, branch, acctType, acctNum, acctName, note, agree:true} → { ok }（要ログイン）
// GET  /api/seller                → 自分の登録情報 { data } or { data:null }（要ログイン）
// GET  /api/seller?key=APPLY_KEY  → 管理用: 全登録一覧 { count, list }
//
// 保存先: seller:{userKey}（ハッシュではなくJSON文字列）。一覧用に集合 seller:index に userKey を追加。

const KV_URL = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const KV_TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;

async function redis(...cmd) {
  const res = await fetch(KV_URL, {
    method: 'POST',
    headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(cmd),
  });
  if (!res.ok) throw new Error(`KV error ${res.status}`);
  return (await res.json()).result;
}

async function currentUser(req) {
  const m = /(?:^|;\s*)cm_sess=([a-f0-9]{48})/.exec(req.headers.cookie || '');
  if (!m) return null;
  const key = await redis('GET', `sess:${m[1]}`);
  if (!key) return null;
  const name = await redis('HGET', `user:${key}`, 'name');
  return name ? { key, name } : null;
}

const trim = (v, n) => String(v || '').trim().slice(0, n);

module.exports = async (req, res) => {
  if (!KV_URL || !KV_TOKEN) return res.status(503).json({ error: 'KV未設定' });

  try {
    if (req.method === 'GET') {
      // 管理用: 全登録一覧
      if (req.query && req.query.key) {
        const { isAdminReq } = require('../lib/admin.js');
        if (!(await isAdminReq(req))) return res.status(403).json({ error: 'forbidden' });
        const keys = (await redis('SMEMBERS', 'seller:index')) || [];
        const list = [];
        for (const k of keys) {
          const raw = await redis('GET', `seller:${k}`);
          if (raw) { const d = JSON.parse(raw); d.userKey = k; list.push(d); }
        }
        list.sort((a, b) => (b.ts || 0) - (a.ts || 0));
        return res.status(200).json({ count: list.length, list });
      }
      // 本人: 自分の登録情報
      const u = await currentUser(req);
      if (!u) return res.status(401).json({ error: 'ログインしてください' });
      const raw = await redis('GET', `seller:${u.key}`);
      return res.status(200).json({ data: raw ? JSON.parse(raw) : null });
    }

    if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' });
    const b = req.body || {};
    const u = await currentUser(req);
    if (!u) return res.status(401).json({ error: 'ログインしてください' });

    if (b.action === 'save') {
      const d = {
        sellerName: trim(b.sellerName, 60),
        email: trim(b.email, 100),
        bank: trim(b.bank, 40),
        branch: trim(b.branch, 40),
        acctType: b.acctType === '当座' ? '当座' : '普通',
        acctNum: trim(b.acctNum, 10).replace(/[^0-9]/g, ''),
        acctName: trim(b.acctName, 60),
        note: trim(b.note, 300),
        userName: u.name,
        agree: b.agree === true,
        ts: Date.now(),
      };
      if (!d.sellerName) return res.status(400).json({ error: 'お支払い先の名義を入力してください' });
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(d.email)) return res.status(400).json({ error: 'メールアドレスの形式をご確認ください' });
      if (!d.bank || !d.branch || !d.acctNum || !d.acctName) return res.status(400).json({ error: '振込先（銀行名・支店名・口座番号・口座名義）をすべて入力してください' });
      if (!d.agree) return res.status(400).json({ error: '販売条件への同意にチェックしてください' });
      await redis('SET', `seller:${u.key}`, JSON.stringify(d));
      await redis('SADD', 'seller:index', u.key);
      return res.status(200).json({ ok: true });
    }

    return res.status(400).json({ error: 'bad action' });
  } catch (e) {
    return res.status(500).json({ error: String((e && e.message) || e) });
  }
};
