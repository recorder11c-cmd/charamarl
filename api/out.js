// 送客計測リダイレクト: GET /api/out?g={galleryId}
// 承認済みギャラリー作品の外部リンクへ302リダイレクトしつつ、作品別・作家別の送客数をカウントする。
// URLはRedis上の登録リンクのみ(オープンリダイレクト防止のため to= は受け付けない)。
// カウント: out:{galleryId} / out:artist:{artistKey} / out:total

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

module.exports = async (req, res) => {
  if (!KV_URL || !KV_TOKEN) return res.status(503).json({ error: 'KV未設定' });
  try {
    // 管理用: 集計一覧 GET /api/out?stats=1&key=...
    if (req.query && req.query.stats) {
      const { isAdminReq } = require('../lib/admin.js');
      if (!(await isAdminReq(req))) return res.status(403).json({ error: 'forbidden' });
      let cursor = '0'; const keys = [];
      do {
        const r = await redis('SCAN', cursor, 'MATCH', 'out:*', 'COUNT', '200');
        cursor = String(r[0]);
        keys.push(...r[1]);
      } while (cursor !== '0');
      const out = {};
      if (keys.length) {
        const vals = await redis('MGET', ...keys);
        keys.forEach((k, i) => { out[k] = Number(vals[i]) || 0; });
      }
      return res.status(200).json(out);
    }

    const g = String((req.query && req.query.g) || '');
    if (!/^g[a-f0-9]{12}$/.test(g)) return res.status(400).json({ error: 'bad id' });
    const raw = await redis('GET', `gal:${g}`);
    if (!raw) return res.redirect(302, 'https://charamarl.com/');
    const item = JSON.parse(raw);
    let link = String(item.link || '');
    if (item.status !== 'approved' || !/^https?:\/\//.test(link)) {
      return res.redirect(302, 'https://charamarl.com/');
    }
    // 計測(失敗してもリダイレクトは通す)
    try {
      await redis('INCR', `out:${g}`);
      if (item.artistKey) await redis('INCR', `out:artist:${item.artistKey}`);
      await redis('INCR', 'out:total');
    } catch (e) {}
    // utm付与(既にクエリがあるURLにも対応)
    try {
      const u = new URL(link);
      if (!u.searchParams.has('utm_source')) {
        u.searchParams.set('utm_source', 'charamarl');
        u.searchParams.set('utm_medium', 'referral');
      }
      link = u.toString();
    } catch (e) {}
    return res.redirect(302, link);
  } catch (e) {
    return res.status(500).json({ error: String((e && e.message) || e) });
  }
};
