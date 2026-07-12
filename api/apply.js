// クリエイター応募API (Vercel KV / Upstash Redis REST)
// POST   /api/apply {name, sns, email, genre, message} → { ok:true }
// GET    /api/apply?key=APPLY_KEY           → 応募一覧（管理用・キー必須）
// DELETE /api/apply?key=APPLY_KEY&ts=…      → 該当応募を削除（管理用）
//
// 必要な環境変数: KV_REST_API_URL / KV_REST_API_TOKEN（react.jsと共通）
//                APPLY_KEY（管理一覧の閲覧キー）

const KV_URL = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const KV_TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;
const LIST_KEY = 'apply:list';

async function redis(...cmd) {
  const res = await fetch(KV_URL, {
    method: 'POST',
    headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(cmd),
  });
  if (!res.ok) throw new Error(`KV error ${res.status}`);
  const data = await res.json();
  return data.result;
}

const trim = (v, max) => String(v || '').trim().slice(0, max);

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(204).end();

  if (!KV_URL || !KV_TOKEN) return res.status(503).json({ error: 'KV未設定' });

  try {
    if (req.method === 'POST') {
      const b = req.body || {};
      if (trim(b.hp, 10)) return res.status(200).json({ ok: true }); // honeypot: botには成功を装う
      const entry = {
        name: trim(b.name, 100),
        sns: trim(b.sns, 300),
        email: trim(b.email, 200),
        genre: trim(b.genre, 50),
        message: trim(b.message, 2000),
        ts: Date.now(),
      };
      if (!entry.name) return res.status(400).json({ error: 'アーティスト名は必須です' });
      if (!entry.sns && !entry.email) return res.status(400).json({ error: 'SNSリンクかメールのどちらかは必須です' });
      await redis('LPUSH', LIST_KEY, JSON.stringify(entry));
      await redis('LTRIM', LIST_KEY, '0', '499');
      return res.status(200).json({ ok: true });
    }

    if (req.method === 'GET' || req.method === 'DELETE') {
      const { key, ts } = req.query || {};
      if (!process.env.APPLY_KEY || key !== process.env.APPLY_KEY) {
        return res.status(403).json({ error: 'forbidden' });
      }
      const raw = (await redis('LRANGE', LIST_KEY, '0', '-1')) || [];
      if (req.method === 'DELETE') {
        const target = raw.find(s => { try { return String(JSON.parse(s).ts) === String(ts); } catch { return false; } });
        if (!target) return res.status(404).json({ error: 'not found' });
        await redis('LREM', LIST_KEY, '1', target);
        return res.status(200).json({ ok: true });
      }
      const list = raw.map(s => { try { return JSON.parse(s); } catch { return null; } }).filter(Boolean);
      return res.status(200).json({ count: list.length, list });
    }

    return res.status(405).json({ error: 'method not allowed' });
  } catch (e) {
    return res.status(500).json({ error: String((e && e.message) || e) });
  }
};
