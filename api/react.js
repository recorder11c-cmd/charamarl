// いいね/保存の集計API (Vercel KV / Upstash Redis REST)
// GET  /api/react            → 全作品のカウント { roar:{likes,saves}, ... }
// GET  /api/react?id=roar    → 単品 { likes, saves }
// POST /api/react {id, type:'like'|'save', op:'add'|'remove'} → { count }
//
// 必要な環境変数(VercelのStorage連携で自動追加):
//   KV_REST_API_URL / KV_REST_API_TOKEN  (または UPSTASH_REDIS_REST_URL / _TOKEN)

const ART_IDS = [
  'roar','worldcup','90s','nodino','costume','ahoyoung', // ギャラリーアート
  'sue','putti','mossun','gmc',                          // キャラクター(TRENDINGランキング用)
];
// カラーリクエスト投票用ID（定番色以外の商品化リクエスト）
const COLOR_REQ = /^(sue|putti|mossun)_(red|yellow|green|cyan|blue|pink)$/;
const COLOR_IDS = ['sue','putti','mossun'].flatMap(c =>
  ['red','yellow','green','cyan','blue','pink'].map(k => `${c}_${k}`));
// 投稿ギャラリー(api/gallery.js)で承認された作品IDは react:extra 集合で許可
async function isAllowedId(id) {
  if (ART_IDS.includes(id)) return true;
  if (COLOR_REQ.test(String(id))) return true;
  if (!/^g[a-f0-9]{12}$/.test(String(id))) return false;
  return Number(await redis('SISMEMBER', 'react:extra', id)) === 1;
}

const KV_URL = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const KV_TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;

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

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(204).end();

  if (!KV_URL || !KV_TOKEN) {
    return res.status(503).json({ error: 'KV未設定' });
  }

  try {
    if (req.method === 'GET') {
      const { id } = req.query || {};
      if (id) {
        if (!(await isAllowedId(id))) return res.status(400).json({ error: 'unknown id' });
        const [likes, saves] = await Promise.all([
          redis('GET', `art:${id}:likes`),
          redis('GET', `art:${id}:saves`),
        ]);
        return res.status(200).json({ likes: Number(likes) || 0, saves: Number(saves) || 0 });
      }
      // 全件: 固定ID + 承認済み投稿IDをMGETでまとめて取得
      const extra = (await redis('SMEMBERS', 'react:extra')) || [];
      const allIds = [...ART_IDS, ...COLOR_IDS, ...extra];
      const keys = allIds.flatMap(a => [`art:${a}:likes`, `art:${a}:saves`]);
      const vals = await redis('MGET', ...keys);
      const out = {};
      allIds.forEach((a, i) => {
        out[a] = { likes: Number(vals[i * 2]) || 0, saves: Number(vals[i * 2 + 1]) || 0 };
      });
      return res.status(200).json(out);
    }

    if (req.method === 'POST') {
      const { id, type, op } = req.body || {};
      if (!(await isAllowedId(id))) return res.status(400).json({ error: 'unknown id' });
      if (!['like', 'save'].includes(type)) return res.status(400).json({ error: 'bad type' });
      const key = `art:${id}:${type}s`;
      let count = await redis(op === 'remove' ? 'DECR' : 'INCR', key);
      count = Number(count) || 0;
      if (count < 0) { await redis('SET', key, '0'); count = 0; } // 負数ガード
      return res.status(200).json({ count });
    }

    return res.status(405).json({ error: 'method not allowed' });
  } catch (e) {
    return res.status(500).json({ error: String((e && e.message) || e) });
  }
};
