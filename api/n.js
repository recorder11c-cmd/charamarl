// NFCタグ / QRコードの行き先: GET /n/{key}  →  /api/n?c={key}
//
// なぜ1枚挟むのか:
//   タグは出荷したら二度と書き換えられない。行き先を直接焼き込むと、そこで固定される。
//   ここを通しておけば、行き先はあとからいつでも変えられるし、何回かざされたかも数えられる。
//
// 行き先の決まり方:
//   ① Redis の nfc:dest:{key}（管理画面/APIで上書きしたもの）
//   ② DEST の既定値
//   ③ どちらも無ければトップ
//
// カウント: nfc:count:{key} / nfc:count:total
//
// 管理:
//   GET  /api/n?stats=1&key=APPLY_KEY            … かざされた回数と現在の行き先
//   POST /api/n  {key:APPLY_KEY, c:'sue', to:'/tap/sue.html?nfc=1'}  … 行き先を変える
//                 to を空文字にすると既定値に戻る

const KV_URL = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const KV_TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;

// 既定の行き先。?nfc=1 を付けてあるのは、GA4で「NFC経由の来訪」を分けて読むため。
// ⚠️ だんな（赤猫かるま）だけ COLOR TAP が無いのでキャラクターページに送っている。
//    TAPができたら nfc:dest:danna を上書きするか、ここを直す。
const DEST = {
  sue:       '/tap/sue.html?nfc=1',
  putti:     '/tap/putti.html?nfc=1',
  mossun:    '/tap/mossun.html?nfc=1',
  gmc:       '/tap/gmc.html?nfc=1',
  ufoo:      '/tap/ufoo.html?nfc=1',
  dogooooo:  '/tap/dogooooo.html?nfc=1',
  inkumo:    '/tap/inkumo.html?nfc=1',
  blockma:   '/tap/blockma.html?nfc=1',
  mony:      '/tap/mony.html?nfc=1',
  yurucrazy: '/tap/yurucrazy.html?nfc=1',
  danna:     '/characters/danna.html?nfc=1',
  // アクキーはまだ無いが、TAPがあるので札を作ればすぐ使えるもの
  kagechiyo: '/tap/kagechiyo.html?nfc=1',
  csh:       '/tap/csh.html?nfc=1',
  ghost:     '/tap/ghost.html?nfc=1',
  rafu:      '/tap/rafu.html?nfc=1',
  gotochi:   '/tap/gotochi.html?nfc=1',
  junkeeees: '/tap/junkeeees.html?nfc=1',
};

const SITE = 'https://charamarl.com';

async function redis(...cmd) {
  const res = await fetch(KV_URL, {
    method: 'POST',
    headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(cmd),
  });
  if (!res.ok) throw new Error(`KV error ${res.status}`);
  return (await res.json()).result;
}

// 行き先はこちらの持ち物だけ。外部URLは受け付けない（オープンリダイレクト防止）
const safe = (to) => (typeof to === 'string' && /^\/[^/\\]/.test(to) ? to : null);
const norm = (c) => String(c || '').trim().toLowerCase().replace(/[^a-z0-9_-]/g, '').slice(0, 40);

module.exports = async (req, res) => {
  if (!KV_URL || !KV_TOKEN) return res.status(503).json({ error: 'KV未設定' });
  const q = req.query || {};
  const admin = () => process.env.APPLY_KEY && q.key === process.env.APPLY_KEY;

  try {
    if (req.method === 'POST') {
      const b = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
      if (!(process.env.APPLY_KEY && b.key === process.env.APPLY_KEY)) {
        return res.status(403).json({ error: 'forbidden' });
      }
      const c = norm(b.c);
      if (!c) return res.status(400).json({ error: 'c が必要です' });
      if (b.to === '') {
        await redis('DEL', `nfc:dest:${c}`);
        return res.status(200).json({ ok: true, c, to: DEST[c] || '/', source: '既定値' });
      }
      const to = safe(b.to);
      if (!to) return res.status(400).json({ error: '行き先はサイト内のパスにしてください（/tap/... の形）' });
      await redis('SET', `nfc:dest:${c}`, to);
      return res.status(200).json({ ok: true, c, to, source: '上書き' });
    }

    if (q.stats) {
      if (!admin()) return res.status(403).json({ error: 'forbidden' });
      const keys = Object.keys(DEST);
      const [counts, dests, total] = await Promise.all([
        redis('MGET', ...keys.map(k => `nfc:count:${k}`)),
        redis('MGET', ...keys.map(k => `nfc:dest:${k}`)),
        redis('GET', 'nfc:count:total'),
      ]);
      const list = keys.map((k, i) => ({
        c: k,
        scans: Number(counts[i]) || 0,
        to: dests[i] || DEST[k],
        overridden: !!dests[i],
        url: `${SITE}/n/${k}`,
      })).sort((a, b) => b.scans - a.scans);
      return res.status(200).json({ total: Number(total) || 0, list });
    }

    const c = norm(q.c);
    const dest = (c && (safe(await redis('GET', `nfc:dest:${c}`)) || DEST[c])) || '/';
    // 数えるのに失敗しても、行き先には必ず飛ばす
    if (c) {
      try {
        await redis('INCR', `nfc:count:${c}`);
        await redis('INCR', 'nfc:count:total');
      } catch (_) {}
    }
    res.setHeader('Cache-Control', 'no-store');
    res.writeHead(302, { Location: SITE + dest });
    return res.end();
  } catch (e) {
    res.writeHead(302, { Location: SITE + '/' });
    return res.end();
  }
};
