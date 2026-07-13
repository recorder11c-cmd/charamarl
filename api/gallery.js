// ギャラリー投稿API (Vercel Blob + Upstash Redis)
// POST {action:'submit', title, desc, link, image} … 作品投稿（要ログイン、imageはdataURL）→ 審査待ちへ
// GET  ?status=approved                            … 公開中の作品一覧（誰でも）
// GET  ?mine=1                                     … 自分の投稿一覧（要ログイン）
// GET  ?status=pending&key=APPLY_KEY               … 審査待ち一覧（管理）
// POST {action:'approve'|'reject'|'remove', id, key:APPLY_KEY} … 審査/削除（管理）
//
// Redis: gal:{id}=JSON / gal:ids=IDリスト(新しい順) / react:extra=♥許可ID集合
// 画像: Vercel Blob (public) gallery/{id}.jpg

const crypto = require('crypto');
const { put, del } = require('@vercel/blob');

const KV_URL = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const KV_TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;
const MAX_IMG_BYTES = 3.5 * 1024 * 1024;
const MAX_PER_USER = 20;

async function redis(...cmd) {
  const res = await fetch(KV_URL, {
    method: 'POST',
    headers: { Authorization: `Bearer ${KV_TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(cmd),
  });
  if (!res.ok) throw new Error(`KV error ${res.status}`);
  return (await res.json()).result;
}

// auth.jsと同じセッション方式
async function currentUser(req) {
  const m = /(?:^|;\s*)cm_sess=([a-f0-9]{48})/.exec(req.headers.cookie || '');
  if (!m) return null;
  const key = await redis('GET', `sess:${m[1]}`);
  if (!key) return null;
  const name = await redis('HGET', `user:${key}`, 'name');
  return name ? { key, name } : null;
}

const trim = (v, max) => String(v || '').trim().slice(0, max);
const isAdmin = (q) => process.env.APPLY_KEY && q && q.key === process.env.APPLY_KEY;

async function loadAll() {
  const ids = (await redis('LRANGE', 'gal:ids', '0', '199')) || [];
  if (!ids.length) return [];
  const raw = await redis('MGET', ...ids.map(id => `gal:${id}`));
  return raw.map(s => { try { return JSON.parse(s); } catch { return null; } }).filter(Boolean);
}

// dataURL → {buf, contentType} 検証つき
function decodeImage(dataUrl) {
  const m = /^data:(image\/(?:jpeg|png|webp));base64,([A-Za-z0-9+/=]+)$/.exec(String(dataUrl || ''));
  if (!m) return null;
  const buf = Buffer.from(m[2], 'base64');
  if (buf.length < 100 || buf.length > MAX_IMG_BYTES) return null;
  const isJpeg = buf[0] === 0xFF && buf[1] === 0xD8;
  const isPng = buf[0] === 0x89 && buf[1] === 0x50;
  const isWebp = buf.slice(8, 12).toString() === 'WEBP';
  if (!isJpeg && !isPng && !isWebp) return null;
  return { buf, contentType: m[1] };
}

module.exports = async (req, res) => {
  if (!KV_URL || !KV_TOKEN) return res.status(503).json({ error: 'KV未設定' });

  try {
    if (req.method === 'GET') {
      const q = req.query || {};
      if (q.mine) {
        const u = await currentUser(req);
        if (!u) return res.status(401).json({ error: 'ログインしてください' });
        const list = (await loadAll()).filter(a => a.artistKey === u.key)
          .map(({ artistKey, ...pub }) => pub);
        return res.status(200).json({ list });
      }
      if (q.status === 'pending' || q.status === 'all') {
        if (!isAdmin(q)) return res.status(403).json({ error: 'forbidden' });
        const list = (await loadAll()).filter(a => q.status === 'all' || a.status === 'pending');
        return res.status(200).json({ list });
      }
      // 公開一覧（承認済みのみ・内部キーは出さない）
      const list = (await loadAll()).filter(a => a.status === 'approved')
        .map(({ artistKey, ...pub }) => pub);
      return res.status(200).json({ list });
    }

    if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' });
    const b = req.body || {};

    if (b.action === 'submit') {
      const u = await currentUser(req);
      if (!u) return res.status(401).json({ error: 'ログインしてください' });
      const title = trim(b.title, 60);
      const desc = trim(b.desc, 500);
      let link = trim(b.link, 300);
      if (!title) return res.status(400).json({ error: '作品タイトルを入力してください' });
      if (link && !/^https?:\/\//.test(link)) link = 'https://' + link;
      const mine = (await loadAll()).filter(a => a.artistKey === u.key);
      if (mine.length >= MAX_PER_USER) return res.status(400).json({ error: `投稿は${MAX_PER_USER}件までです` });
      const img = decodeImage(b.image);
      if (!img) return res.status(400).json({ error: '画像を読み込めませんでした（jpeg/png/webp・3.5MBまで）' });

      const id = 'g' + crypto.randomBytes(6).toString('hex');
      const ext = img.contentType === 'image/png' ? 'png' : img.contentType === 'image/webp' ? 'webp' : 'jpg';
      const blob = await put(`gallery/${id}.${ext}`, img.buf, {
        access: 'public', contentType: img.contentType, addRandomSuffix: false,
      });
      const item = {
        id, title, desc, link,
        img: blob.url,
        artist: u.name, artistKey: u.key,
        status: 'pending', ts: Date.now(),
      };
      await redis('SET', `gal:${id}`, JSON.stringify(item));
      await redis('LPUSH', 'gal:ids', id);
      return res.status(200).json({ ok: true, id });
    }

    if (b.action === 'edit') {
      const u = await currentUser(req);
      if (!u) return res.status(401).json({ error: 'ログインしてください' });
      const id = trim(b.id, 20);
      const raw = await redis('GET', `gal:${id}`);
      if (!raw) return res.status(404).json({ error: 'not found' });
      const item = JSON.parse(raw);
      if (item.artistKey !== u.key) return res.status(403).json({ error: '自分の投稿のみ編集できます' });
      const title = trim(b.title, 60);
      if (!title) return res.status(400).json({ error: '作品タイトルを入力してください' });
      item.title = title;
      item.desc = trim(b.desc, 500);
      let link = trim(b.link, 300);
      if (link && !/^https?:\/\//.test(link)) link = 'https://' + link;
      item.link = link;
      if (b.image) { // 画像差し替えは再審査へ
        const img = decodeImage(b.image);
        if (!img) return res.status(400).json({ error: '画像を読み込めませんでした（jpeg/png/webp・3.5MBまで）' });
        const ext = img.contentType === 'image/png' ? 'png' : img.contentType === 'image/webp' ? 'webp' : 'jpg';
        const oldImg = item.img;
        const blob = await put(`gallery/${id}_${Date.now()}.${ext}`, img.buf, {
          access: 'public', contentType: img.contentType, addRandomSuffix: false,
        });
        item.img = blob.url;
        if (item.status === 'approved') {
          item.status = 'pending';
          await redis('SREM', 'react:extra', id);
        }
        try { await del(oldImg); } catch (_) {}
      }
      item.edited = Date.now();
      await redis('SET', `gal:${id}`, JSON.stringify(item));
      return res.status(200).json({ ok: true, status: item.status });
    }

    // 以下は管理操作
    if (!isAdmin(req.query) && !(process.env.APPLY_KEY && b.key === process.env.APPLY_KEY)) {
      return res.status(403).json({ error: 'forbidden' });
    }
    const id = trim(b.id, 20);
    const raw = await redis('GET', `gal:${id}`);
    if (!raw) return res.status(404).json({ error: 'not found' });
    const item = JSON.parse(raw);

    if (b.action === 'approve' || b.action === 'reject') {
      item.status = b.action === 'approve' ? 'approved' : 'rejected';
      await redis('SET', `gal:${id}`, JSON.stringify(item));
      await redis(b.action === 'approve' ? 'SADD' : 'SREM', 'react:extra', id);
      return res.status(200).json({ ok: true, status: item.status });
    }

    if (b.action === 'remove') {
      await redis('DEL', `gal:${id}`, `art:${id}:likes`, `art:${id}:saves`);
      await redis('LREM', 'gal:ids', '0', id);
      await redis('SREM', 'react:extra', id);
      try { await del(item.img); } catch (_) {}
      return res.status(200).json({ ok: true });
    }

    return res.status(400).json({ error: 'bad action' });
  } catch (e) {
    return res.status(500).json({ error: String((e && e.message) || e) });
  }
};
