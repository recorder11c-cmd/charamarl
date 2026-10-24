// チラシなど印刷物のQR短縮URL /q/<k> → 数えてから転送（2026-10-24〜。それ以前は vercel.json の redirect で数えていなかった）
//   GET /q/j  … 図鑑 / /q/a … AR / /q/g … ギャラリー / /q/k … アクキー / /q/b … 作家募集
//   GET /api/q?summary=1 → 日別の回数と端末の目安（IP＋UAのハッシュ。個人情報は保存しない）
//   ?nc=1 を付けると数えない（動作確認用）
const crypto = require('crypto');
const { redis, clientIp, serverError } = require('./_lib/admin.js');
const DEST = {
  j: 'https://charamarl.com/tap/junkeeees.html?utm_source=flyer&utm_medium=print&utm_campaign=junk_fes_bag',
  a: 'https://charamarl.com/ar/fes/?utm_source=flyer&utm_medium=print&utm_campaign=junk_fes_bag&utm_content=ar',
  g: 'https://charamarl.com/?utm_source=flyer&utm_medium=print&utm_campaign=junk_fes_bag&utm_content=gallery#discover',
  k: 'https://charamarl.com/characters/keyrings.html?utm_source=flyer&utm_medium=print&utm_campaign=junk_fes_bag&utm_content=keyrings',
  b: 'https://charamarl.com/join.html?utm_source=flyer&utm_medium=print&utm_campaign=junk_fes_bag&utm_content=join',
};
const LABEL = { j: '図鑑', a: 'AR', g: 'ギャラリー', k: 'アクキー', b: '作家募集' };
const jstDay = () => new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 10);

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  const q = req.query || {};
  try {
    if (q.summary !== undefined) {
      const days = []; const start = Date.parse('2026-10-24T00:00:00+09:00');
      for (let t = start; t <= Date.now() + 9 * 3600e3; t += 864e5) days.push(new Date(t).toISOString().slice(0, 10));
      const out = { label: LABEL, days: {}, total: {} };
      for (const k of Object.keys(DEST)) out.total[k] = { hits: Number(await redis('GET', `q:cnt:${k}`)) || 0, devices: Number(await redis('SCARD', `q:dev:${k}`)) || 0 };
      for (const day of days.slice(-14)) {
        const o = {};
        for (const k of Object.keys(DEST)) { const h = Number(await redis('GET', `q:cnt:${day}:${k}`)) || 0; const d = Number(await redis('SCARD', `q:dev:${day}:${k}`)) || 0; if (h) o[k] = { hits: h, devices: d }; }
        if (Object.keys(o).length) out.days[day] = o;
      }
      return res.status(200).json(out);
    }
    const k = String(q.k || '').toLowerCase();
    const dest = DEST[k];
    if (!dest) return res.status(404).send('not found');
    if (q.nc === undefined) {
      const day = jstDay();
      const dev = crypto.createHash('sha256').update(clientIp(req) + '|' + String(req.headers['user-agent'] || '')).digest('hex').slice(0, 16);
      const cmds = [['INCR', `q:cnt:${k}`], ['INCR', `q:cnt:${day}:${k}`], ['SADD', `q:dev:${k}`, dev], ['SADD', `q:dev:${day}:${k}`, dev], ['EXPIRE', `q:dev:${day}:${k}`, String(400 * 86400)]];
      for (const c of cmds) { try { await redis(...c); } catch (_) {} }   // 数えられなくても転送はする
    }
    res.statusCode = 302; res.setHeader('Location', dest); return res.end();
  } catch (e) { return serverError(res, e, 'q.js'); }
};
