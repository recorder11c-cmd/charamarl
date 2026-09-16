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
const crypto = require('crypto');
// NFCアクキー所有者トークン: HMAC(APPLY_KEY, 'run-owner:'+char) の先頭20桁。go.js が発行し、ここで検証する
function ownerToken(char) { return ADMIN_KEY ? crypto.createHmac('sha256', ADMIN_KEY).update('run-owner:' + char).digest('hex').slice(0, 20) : null; }

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
const ALLOWED_CHARS = ['SUE', 'PUTTI', 'MOSSUN', 'GMC', 'UFOO', 'KAGECHIYO', 'YURUCRAZY', 'DOGOOOOO', 'INKUMO', 'DANNA', 'BLOCKMA', 'MONY'];   // 公開キャラのみ受け付ける(プロンプト公開後のコピー流入対策)
// 週間ランキング: 日本時間の月曜始まり。キー = run:rank:{char}:w:{その週の月曜 YYYY-MM-DD}
function weekKey(now = new Date()) {
  const jst = new Date(now.getTime() + 9 * 3600e3);
  const dow = (jst.getUTCDay() + 6) % 7;            // 月=0 … 日=6
  const mon = new Date(jst.getTime() - dow * 864e5);
  return mon.toISOString().slice(0, 10);
}
const charOk = c => CHAR_RE.test(c) && ALLOWED_CHARS.includes(c);
const PID_RE = /^[a-f0-9]{16,32}$/;
const MAX_SCORE = 999999;
const TOP_N = 20;

function cleanName(n) {
  return String(n || '').replace(/[\x00-\x1f\x7f]/g, '').replace(/\s+/g, ' ').trim().slice(0, 12);
}

async function boardOf(char, key, pid) {
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
// 累計(top/me/total)＋今週(week:{key,top,me,total})を返す
async function board(char, pid) {
  const wk = weekKey();
  const [all, week] = await Promise.all([boardOf(char, `run:rank:${char}`, pid), boardOf(char, `run:rank:${char}:w:${wk}`, pid)]);
  return Object.assign(all, { week: Object.assign({ key: wk }, week) });
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
      if (!charOk(char)) return res.status(400).json({ error: 'bad char' });
      if (q.owner !== undefined) {           // 所有者トークン検証
        const ok = !!ownerToken(char) && String(q.owner) === ownerToken(char);
        return res.status(200).json({ owner: ok });
      }
      if (q.stats !== undefined) {           // 管理用: 日別のプレイ数・ゲームオーバー数(直近14日)
        if (!ADMIN_KEY || q.key !== ADMIN_KEY) return res.status(403).json({ error: 'forbidden' });
        const days = []; const d = new Date();
        for (let i = 0; i < 14; i++) { days.push(new Date(d.getTime() - i * 864e5).toISOString().slice(0, 10)); }
        const vals = await redis('MGET', ...days.flatMap(day => [`run:stat:${char}:play:${day}`, `run:stat:${char}:over:${day}`, `run:stat:${char}:share:${day}`, `run:stat:${char}:shop:${day}`]));
        const total = await redis('ZCARD', `run:rank:${char}`);
        const daily = days.map((day, i) => ({ day, play: +vals[i*4] || 0, over: +vals[i*4+1] || 0, share: +vals[i*4+2] || 0, shop: +vals[i*4+3] || 0 }));
        return res.status(200).json({ char, registered: Number(total) || 0, daily });
      }
      if (q.week !== undefined) {            // 指定週の順位表(管理用)。week=YYYY-MM-DD(その週の月曜) / week=last で先週
        if (!ADMIN_KEY || q.key !== ADMIN_KEY) return res.status(403).json({ error: 'forbidden' });
        let wk = String(q.week);
        if (wk === 'last') wk = weekKey(new Date(Date.now() - 7 * 864e5));
        if (!/^\d{4}-\d{2}-\d{2}$/.test(wk)) return res.status(400).json({ error: 'bad week' });
        const b = await boardOf(char, `run:rank:${char}:w:${wk}`, null);
        const raw = await redis('ZREVRANGE', `run:rank:${char}:w:${wk}`, 0, TOP_N - 1);
        b.top.forEach((t, i) => { t.pid = raw[i]; });
        return res.status(200).json({ char, week: wk, top: b.top, total: b.total });
      }
      const pid = PID_RE.test(String(q.pid || '')) ? String(q.pid) : null;
      const out = await board(char, pid);
      if (ADMIN_KEY && q.key === ADMIN_KEY) {           // 管理用: 削除に使うpidを付けて返す
        const raw = await redis('ZREVRANGE', `run:rank:${char}`, 0, TOP_N - 1);
        out.top.forEach((t, i) => { t.pid = raw[i]; });
      }
      return res.status(200).json(out);
    }

    if (req.method === 'POST' && typeof req.body === 'string') {   // sendBeacon(text/plain) 対策
      try { req.body = JSON.parse(req.body); } catch (_) { req.body = {}; }
    }
    if (req.method === 'POST' && req.body && req.body.event) {   // 計測ビーコン: play / over / share / shop
      const b = req.body; const char = String(b.char || '');
      const ev = String(b.event);
      if (!charOk(char) || !['play', 'over', 'share', 'shop'].includes(ev)) return res.status(400).json({ error: 'bad event' });
      const ip = (req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'unknown';
      const rl = `run:rl:ev:${ip}`; const n = await redis('INCR', rl); if (n === 1) await redis('EXPIRE', rl, 60);
      if (n > 60) return res.status(429).json({ error: 'too many' });
      const day = new Date().toISOString().slice(0, 10);
      await redis('INCR', `run:stat:${char}:${ev}:${day}`);
      return res.status(200).json({ ok: true });
    }

    if (req.method === 'POST') {
      const b = req.body || {};
      const char = String(b.char || '');
      const pid = String(b.pid || '');
      const name = cleanName(b.name);
      const score = Math.floor(Number(b.score));
      if (!charOk(char) || !PID_RE.test(pid)) return res.status(400).json({ error: 'bad id' });
      if (!name) return res.status(400).json({ error: 'name required' });
      if (!Number.isFinite(score) || score < 1 || score > MAX_SCORE) return res.status(400).json({ error: 'bad score' });

      // レート制限: 同一IPから1分に12回まで
      const ip = (req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'unknown';
      const rl = `run:rl:${ip}`;
      const n = await redis('INCR', rl);
      if (n === 1) await redis('EXPIRE', rl, 60);
      if (n > 12) return res.status(429).json({ error: 'too many' });

      const key = `run:rank:${char}`, wkey = `run:rank:${char}:w:${weekKey()}`, pkey = `run:player:${char}:${pid}`;
      const [prevRaw, prevWRaw] = await Promise.all([redis('ZSCORE', key, pid), redis('ZSCORE', wkey, pid)]);
      const prev = Number(prevRaw) || 0, prevW = Number(prevWRaw) || 0;
      const cmds = [['HSET', pkey, 'name', name]];
      if (score > prev) cmds.push(['ZADD', key, score, pid], ['HSET', pkey, 'score', score, 'at', Date.now()]);
      if (score > prevW) cmds.push(['ZADD', wkey, score, pid], ['EXPIRE', wkey, 60 * 86400]);   // 週間キーは60日で自然消滅
      await pipeline(cmds);
      const out = await board(char, pid);
      return res.status(200).json({ rank: out.me ? out.me.rank : null, best: Math.max(prev, score), total: out.total, top: out.top, week: out.week, weekBest: Math.max(prevW, score) });
    }

    if (req.method === 'DELETE') {
      if (!ADMIN_KEY || q.key !== ADMIN_KEY) return res.status(403).json({ error: 'forbidden' });
      const char = String(q.char || ''), pid = String(q.pid || '');
      if (!charOk(char) || !PID_RE.test(pid)) return res.status(400).json({ error: 'bad id' });
      await pipeline([['ZREM', `run:rank:${char}`, pid], ['ZREM', `run:rank:${char}:w:${weekKey()}`, pid], ['DEL', `run:player:${char}:${pid}`]]);
      return res.status(200).json({ ok: true });
    }

    return res.status(405).json({ error: 'method' });
  } catch (e) {
    return res.status(500).json({ error: String(e.message || e) });
  }
};
