// JUNKeeeeS FES 2026 会場NFCの計測（サーバー側の数え方。GA4は広告ブロック等で4割ほど落ちるので、ROKUさんへの報告はこちらを主にする）
//   POST {t:'scan', spot:'a'|'b'|'c', d:<端末ID>, found:1..3}   図鑑を会場スポットで開いた
//   POST {t:'legendary_view'|'legendary_save'|'legendary_share'|'to_run'|'platinum_unlock'|'run_open', d}
//   GET  ?summary=1  → 日別の集計（個人情報なし。端末IDは出さない）
// 端末IDは図鑑がブラウザに作るランダムな文字列。名前・連絡先は持たない。会期後1か月で削除（11/25）。
const { redis, clientIp, overLimit, serverError } = require('./_lib/admin.js');
const DAYS = ['2026-10-24', '2026-10-25'];
const TYPES = ['open', 'scan', 'legendary_view', 'legendary_save', 'legendary_share', 'to_run', 'platinum_unlock', 'run_open'];
const jstDay = () => new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 10);

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  try {
    if (req.method === 'GET') {
      const ip = clientIp(req); if (await overLimit(`fes:sum:${ip}`, 60, 600)) return res.status(429).json({ error: 'too many' });
      const out = { days: {}, devices_all: 0, spots_per_device: { 1: 0, 2: 0, 3: 0 } };
      for (const day of DAYS) {
        const o = { scans: {}, devices: {}, complete: 0 };
        o.opens = {}; for (const s of ['a', 'b', 'c']) { o.opens[s] = Number(await redis('GET', `fes:cnt:${day}:open:${s}`)) || 0; o.scans[s] = Number(await redis('GET', `fes:cnt:${day}:scan:${s}`)) || 0; o.devices[s] = Number(await redis('SCARD', `fes:dev:${day}:${s}`)) || 0; }
        o.devices.opened = Number(await redis('SCARD', `fes:devo:${day}`)) || 0;
        o.devices.all = Number(await redis('SCARD', `fes:dev:${day}:all`)) || 0;
        o.complete = Number(await redis('SCARD', `fes:complete:${day}`)) || 0;
        for (const t of TYPES.slice(2)) o[t] = Number(await redis('GET', `fes:cnt:${day}:${t}`)) || 0;
        out.days[day] = o;
      }
      const devs = (await redis('SMEMBERS', 'fes:devices')) || [];
      out.devices_all = devs.length;
      for (const d of devs) { const n = Number(await redis('SCARD', `fes:ds:${d}`)) || 0; if (n >= 1 && n <= 3) out.spots_per_device[n]++; }
      if (q.log !== undefined) { const raw = (await redis('LRANGE', 'fes:log', '0', '499')) || []; out.log = raw.map(x => { try { const o = JSON.parse(x); o.jst = new Date(o.ts + 9 * 3600e3).toISOString().replace('T', ' ').slice(5, 16); return o; } catch (_) { return null; } }).filter(Boolean); }
      try { const r = await fetch('https://charamarl.com/api/run-score?char=JUNK_AGERU&fes=1'); const j = await r.json(); out.run_fes_players = j.total || 0; } catch (_) { out.run_fes_players = null; }
      return res.status(200).json(out);
    }
    if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' });
    let b = req.body || {}; if (typeof b === 'string') { try { b = JSON.parse(b); } catch (_) { b = {}; } }
    const t = String(b.t || ''); if (!TYPES.includes(t)) return res.status(400).json({ error: 'bad type' });
    const d = String(b.d || '').replace(/[^a-z0-9]/gi, '').slice(0, 32); if (d.length < 8) return res.status(400).json({ error: 'bad device' });
    if (d.startsWith('test')) return res.status(200).json({ ok: true, test: true });   // 動作確認用。数えない
    const ip = clientIp(req); if (await overLimit(`fes:post:${ip}`, 120, 600)) return res.status(429).json({ error: 'too many' });
    const day = jstDay();
    const cmds = [];
    if (t === 'open') {
      const spot = String(b.spot || ''); if (!['a', 'b', 'c'].includes(spot)) return res.status(400).json({ error: 'bad spot' });
      cmds.push(['INCR', `fes:cnt:${day}:open:${spot}`], ['SADD', `fes:devo:${day}`, d]);
    } else if (t === 'scan') {
      const spot = String(b.spot || ''); if (!['a', 'b', 'c'].includes(spot)) return res.status(400).json({ error: 'bad spot' });
      cmds.push(['INCR', `fes:cnt:${day}:scan:${spot}`], ['SADD', `fes:dev:${day}:${spot}`, d], ['SADD', `fes:dev:${day}:all`, d], ['SADD', 'fes:devices', d], ['SADD', `fes:ds:${d}`, spot]);
      if (Number(b.found) >= 3) cmds.push(['SADD', `fes:complete:${day}`, d]);
    } else {
      cmds.push(['INCR', `fes:cnt:${day}:${t}`]);
    }
    cmds.push(['LPUSH', 'fes:log', JSON.stringify({ ts: Date.now(), t, spot: b.spot || null, found: Number(b.found) || null })], ['LTRIM', 'fes:log', '0', '4999']);   // 時刻つきの記録(10/26〜。端末IDは入れない)
    for (const c of cmds) await redis(...c);
    return res.status(200).json({ ok: true });
  } catch (e) { return serverError(res, e, 'fes.js'); }
};
