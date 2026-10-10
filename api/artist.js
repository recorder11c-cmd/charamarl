// 作家ごとの「活動場所のリンク（ホーム）」
//   GET  /api/artist                  → { artists: { [artistKey]: { home, homeLabel } } }（公開・内部キーはそのまま小文字名）
//   POST {action:'set', home, homeLabel}                         本人（ログイン中のアカウント）
//   POST {action:'adminset', key|session, artistKey, home, homeLabel}  運営
//   POST {action:'ack'}                                          本人が「活動場所のリンクを確認した」と押した記録（confirmed=時刻）
//   GET  /api/artist?confirmed=1  （運営のみ）→ { artistKey: 確認した時刻 }  誰が確認済みか
// 作品側の link（作品固有リンク）とは別物。作品に link が無いとき、作家ページの上部ボタンのときに使う。
const { isAdminReq } = require('./_lib/admin.js');
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
async function currentUserKey(req) {
  const m = /(?:^|;\s*)cm_sess=([a-f0-9]{48})/.exec(req.headers.cookie || '');
  if (!m) return null;
  return await redis('GET', `sess:${m[1]}`);
}
const trim = (v, max) => String(v || '').trim().slice(0, max);
function cleanUrl(v) {
  let u = trim(v, 300);
  if (u && !/^https?:\/\//i.test(u)) u = 'https://' + u;
  try { if (u) new URL(u); } catch (e) { return null; }
  return u;
}

async function loadAll() {
  let cursor = '0'; const keys = [];
  do {
    const r = await redis('SCAN', cursor, 'MATCH', 'artist:*', 'COUNT', '200');
    cursor = String(r[0]); keys.push(...r[1]);
  } while (cursor !== '0');
  const out = {};
  if (keys.length) {
    const vals = await redis('MGET', ...keys);
    keys.forEach((k, i) => { try { const v = JSON.parse(vals[i]); if (v && v.home) out[k.slice(7)] = { home: v.home, homeLabel: v.homeLabel || '' }; } catch (e) {} });
  }
  return out;
}

module.exports = async (req, res) => {
  if (!KV_URL || !KV_TOKEN) return res.status(503).json({ error: 'KV未設定' });
  try {
    if (req.method === 'GET') {
      if (req.query && req.query.mine) { // 本人の分だけ（マイページ用）
        const k = await currentUserKey(req);
        if (!k) return res.status(401).json({ error: 'ログインしてください' });
        let rec = null; try { rec = JSON.parse(await redis('GET', `artist:${k}`)); } catch (e) {}
        return res.status(200).json({ artistKey: k, home: (rec && rec.home) || '', homeLabel: (rec && rec.homeLabel) || '', confirmed: (rec && rec.confirmed) || 0 });
      }
      if (req.query && req.query.confirmed) { // 運営のみ：誰が「確認した」を押したか
        if (!(await isAdminReq(req))) return res.status(403).json({ error: 'forbidden' });
        let cursor = '0'; const keys = [];
        do { const r = await redis('SCAN', cursor, 'MATCH', 'artist:*', 'COUNT', '200'); cursor = String(r[0]); keys.push(...r[1]); } while (cursor !== '0');
        const out = {};
        if (keys.length) { const vals = await redis('MGET', ...keys); keys.forEach((k, i) => { try { const v = JSON.parse(vals[i]); if (v && v.confirmed) out[k.slice(7)] = v.confirmed; } catch (e) {} }); }
        return res.status(200).json(out);
      }
      res.setHeader('Cache-Control', 'public, max-age=60');
      return res.status(200).json({ artists: await loadAll() });
    }
    if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' });
    const b = req.body || {};
    if (b.action === 'ack') { // 本人が「活動場所のリンクを確認した」を押した
      const k = await currentUserKey(req);
      if (!k) return res.status(401).json({ error: 'ログインしてください' });
      let rec = {}; try { rec = JSON.parse(await redis('GET', `artist:${k}`)) || {}; } catch (e) {}
      rec.confirmed = Date.now(); if (rec.home === undefined) rec.home = '';
      await redis('SET', `artist:${k}`, JSON.stringify(rec));
      return res.status(200).json({ ok: true, confirmed: rec.confirmed });
    }
    let key = null;
    if (b.action === 'set') {
      key = await currentUserKey(req);
      if (!key) return res.status(401).json({ error: 'ログインしてください' });
    } else if (b.action === 'adminset') {
      if (!(await isAdminReq(req))) return res.status(403).json({ error: 'forbidden' });
      key = trim(b.artistKey, 60).toLowerCase();
      if (!key) return res.status(400).json({ error: 'artistKey required' });
    } else {
      return res.status(400).json({ error: 'bad action' });
    }
    const home = cleanUrl(b.home);
    if (home === null) return res.status(400).json({ error: 'URLの形式が正しくありません' });
    const rec = { home, homeLabel: trim(b.homeLabel, 30), edited: Date.now() };
    if (b.action === 'set') rec.confirmed = Date.now(); // 自分で保存した＝確認した
    else { try { const old = JSON.parse(await redis('GET', `artist:${key}`)); if (old && old.confirmed) rec.confirmed = old.confirmed; } catch (e) {} } // 運営の差し替えでは確認済みを消さない
    if (!home && !rec.confirmed) await redis('DEL', `artist:${key}`);
    else await redis('SET', `artist:${key}`, JSON.stringify(rec));
    return res.status(200).json({ ok: true, artistKey: key, home, homeLabel: rec.homeLabel });
  } catch (e) {
    return res.status(500).json({ error: String((e && e.message) || e) });
  }
};
module.exports.loadArtists = loadAll;
