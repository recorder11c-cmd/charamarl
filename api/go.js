// NFCタグ・QRコード用リダイレクト＋スキャン計測
// GET /api/go?c=sue            → nfc:sue:scans を+1して /characters/sue.html?from=nfc へ302
// GET /api/go?stats=1&key=…    → スキャン集計（管理用）
//
// NFCタグにはこのURLを書き込む: https://charamarl.vercel.app/api/go?c=sue など

const KV_URL = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const KV_TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;

const DEST = {
  sue: '/characters/sue.html',
  putti: '/characters/putti.html',
  mossun: '/characters/mossun.html',
  gmc: '/characters/gmc.html',
  top: '/',
};

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
  const q = req.query || {};

  if (q.reset) { // 管理用: カウンタリセット
    const { isAdminReq } = require('../lib/admin.js');
    if (!(await isAdminReq(req))) {
      return res.status(403).json({ error: 'forbidden' });
    }
    await redis('DEL', ...Object.keys(DEST).map(c => `nfc:${c}:scans`));
    return res.status(200).json({ ok: true });
  }

  if (q.stats) { // スキャン集計（回数のみ・公開値）
    const ids = Object.keys(DEST);
    const vals = await redis('MGET', ...ids.map(c => `nfc:${c}:scans`));
    const out = {};
    ids.forEach((c, i) => { out[c] = Number(vals[i]) || 0; });
    return res.status(200).json(out);
  }

  const c = DEST[q.c] ? q.c : 'top';
  try {
    if (KV_URL && KV_TOKEN) await redis('INCR', `nfc:${c}:scans`);
  } catch (_) {} // 計測失敗でも誘導は止めない
  res.statusCode = 302;
  res.setHeader('Location', DEST[c] + (DEST[c].includes('?') ? '&' : '?') + 'from=nfc');
  return res.end();
};
