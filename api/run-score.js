// DINORENNY RUN ランキングAPI (Upstash Redis REST)
// GET    /api/run-score?char=SUE&pid=xxx         → { top:[{rank,name,score,me}], me:{rank,best}|null, total }
// POST   /api/run-score {char, pid, name, score}  → { rank, best, total, top }  (ベスト更新時のみ上書き)
// DELETE /api/run-score?char=SUE&pid=xxx&key=APPLY_KEY → 削除(管理用)
//
// Redis: run:rank:{char} = ZSET(pid→best) / run:player:{char}:{pid} = HASH(name,score,at)
// 特典なしの共有用ランキングなので不正対策は軽め(レート制限・値の妥当性チェック・管理削除のみ)

const KV_URL = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const KV_TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;
const ADMIN_KEY = process.env.APPLY_KEY;

async function redis(...cmd) {
  const res = await fetch(KV_URL, { method: 'POST', headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' }, body: JSON.stringify(cmd) });
  if (!res.ok) throw new Error(`KV error ${res.status}`);
  return (await res.json()).result;
}
async function pipeline(cmds) {
  const res = await fetch(KV_URL.replace(/\/$/, '') + '/pipeline', { method: 'POST', headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' }, body: JSON.stringify(cmds) });
  if (!res.ok) throw new Error(`KV pipeline error ${res.status}`);
  return (await res.json()).map(r => r.result);
}

const CHAR_RE = /^[a-z0-9_-]{1,20}$/i;
const PID_RE = /^[a-f0-9]{16,32}$/;
const MAX_SCORE = 999999;
const TOP_N = 20;

function cleanName(n) {
  return String(n || '').replace(/[\x00-\x1f\x7f]/g, '').replace(/\s+/g, ' ').trim().slice(0, 12);
}

async function board(char, pid) {
  const key = `run:rank:${char}`;
  const [raw, total] = await Promise.all([redis('ZREVRANGE', key, 0, TOP_N - 1, 'WITHSCORES'), redis('ZCARD', key)]);
  const rows = [];
  for (let i = 0; i < (raw || []).length; i += 2) rows.push({ pid: raw[i], score: Number(raw[i + 1]) });
  const names = rows.length ? await pipeline(rows.map(r => ['HGET', `run:player:${char}:${r.pid}`, 'name'])) : [];
  const top = rows.map((r, i) => ({ rank: i + 1, name: names[i] || '???', score: r.score, me: r.pid === pid }));
  let me = null;
  if (pid) {
    const [rank, best] = await Promise.all([redis('ZREVRANK', key, pid), redis('ZSCORE', key, pid)]);
    if (rank !== null && rank !== undefined) me = { rank: Number(rank) + 1, best: Number(best) };
  }
  return { top, me, total: Number(total) || 0 };
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Cache-Control', 'no-store');
  if (req.method === 'OPTIONS') return res.status(204).end();
  if (!KV_URL || !KV_TOKEN) return res.status(503).json({ error: 'KV未設定' });

  try {
    const q = req.query || {};
    if (req.method === 'GET') {
      const char = String(q.char || 'SUE');
      if (!CHAR_RE.test(char)) return res.status(400).json({ error: 'bad char' });
      const pid = PID_RE.test(String(q.pid || '')) ? String(q.pid) : null;
      const out = await board(char, pid);
      if (ADMIN_KEY && q.key === ADMIN_KEY) {           // 管理用: 削除に使うpidを付けて返す
        const raw = await redis('ZREVRANGE', `run:rank:${char}`, 0, TOP_N - 1);
        out.top.forEach((t, i) => { t.pid = raw[i]; });
      }
      return res.status(200).json(out);
    }

    if (req.method === 'POST') {
      const b = req.body || {};
      const char = String(b.char || '');
      const pid = String(b.pid || '');
      const name = cleanName(b.name);
      const score = Math.floor(Number(b.score));
      if (!CHAR_RE.test(char) || !PID_RE.test(pid)) return res.status(400).json({ error: 'bad id' });
      if (!name) return res.status(400).json({ error: 'name required' });
      if (!Number.isFinite(score) || score < 1 || score > MAX_SCORE) return res.status(400).json({ error: 'bad score' });

      // レート制限: 同一IPから1分に12回まで
      const ip = (req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'unknown';
      const rl = `run:rl:${ip}`;
      const n = await redis('INCR', rl);
      if (n === 1) await redis('EXPIRE', rl, 60);
      if (n > 12) return res.status(429).json({ error: 'too many' });

      const key = `run:rank:${char}`, pkey = `run:player:${char}:${pid}`;
      const prev = Number(await redis('ZSCORE', key, pid)) || 0;
      if (score > prev) {
        await pipeline([
          ['ZADD', key, score, pid],
          ['HSET', pkey, 'name', name, 'score', score, 'at', Date.now()],
        ]);
      } else {
        await redis('HSET', pkey, 'name', name); // 名前だけ更新
      }
      const out = await board(char, pid);
      return res.status(200).json({ rank: out.me ? out.me.rank : null, best: Math.max(prev, score), total: out.total, top: out.top });
    }

    if (req.method === 'DELETE') {
      if (!ADMIN_KEY || q.key !== ADMIN_KEY) return res.status(403).json({ error: 'forbidden' });
      const char = String(q.char || ''), pid = String(q.pid || '');
      if (!CHAR_RE.test(char) || !PID_RE.test(pid)) return res.status(400).json({ error: 'bad id' });
      await pipeline([['ZREM', `run:rank:${char}`, pid], ['DEL', `run:player:${char}:${pid}`]]);
      return res.status(200).json({ ok: true });
    }

    return res.status(405).json({ error: 'method' });
  } catch (e) {
    return res.status(500).json({ error: String(e.message || e) });
  }
};
