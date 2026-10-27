// ピンズスマートボールのクーポン発行API
//   POST {action:'zorome', d:<端末ID>, level:3|4} → ゾロ目のご褒美: 4個セットの Stripe プロモーションコードを1枚発行
//     level 3(同じピンズに3回・既定) = ¥500引き / level 4(4回) = ¥1,000引き
//   返り値 {code, amount_off, expires:<ISO>, level}。同じ端末/IPは1日1枚(2回目は同じコードを返す)。
//   すでに¥500を持つ端末が level 4 で来たら、¥500のコードを無効化して¥1,000に差し替える(upgraded:true。月の発行枚数は増やさない)。月の発行上限 MONTH_MAX。
// 🔴 ゲームの結果はブラウザ側の判定なので、ここでは「本当にゾロ目だったか」は確かめられない。
//    代わりに 1端末1日1枚・1回限り・24時間で失効・月上限 で抑える。割引分はCHARAMARL持ち(作家の取り分は定価ベース・2026-10-19 ユーザー決定)
const Stripe = require('stripe');
const { redis, clientIp, overLimit, serverError } = require('./_lib/admin.js');

const AMOUNTS = { 3: 500, 4: 1000 }, MONTH_MAX = 100, TTL_H = 24;
const ALNUM = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
function randCode(n){ let s = ''; for (let i = 0; i < n; i++) s += ALNUM[Math.floor(Math.random() * ALNUM.length)]; return s; }

async function issue(stripe, level, expires){
  const amount = AMOUNTS[level];
  const coupon = await stripe.coupons.create({ amount_off: amount, currency: 'jpy', duration: 'once', name: `ピンズスマートボール ゾロ目×${level} ¥${amount}引き` });
  let promo = null;
  for (let i = 0; i < 3 && !promo; i++) {
    try { promo = await stripe.promotionCodes.create({ promotion: { type: 'coupon', coupon: coupon.id }, code: (level === 4 ? 'QUAD' : 'ZORO') + randCode(4), max_redemptions: 1, expires_at: expires, restrictions: { minimum_amount: 4400, minimum_amount_currency: 'jpy' } }); }
    catch (e) { if (i === 2) throw e; }
  }
  return { code: promo.code, amount_off: amount, expires: new Date(expires * 1000).toISOString(), level, promo_id: promo.id };
}
function pub(rec){ const { promo_id, ...o } = rec; return o; }   // promo_id はブラウザへ返さない

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' });
  let b = req.body || {}; if (typeof b === 'string') { try { b = JSON.parse(b); } catch (_) { b = {}; } }
  if (b.action !== 'zorome') return res.status(400).json({ error: 'bad action' });
  const d = String(b.d || '').replace(/[^a-z0-9]/gi, '').slice(0, 32);
  if (d.length < 8) return res.status(400).json({ error: 'bad device' });
  const level = Number(b.level) === 4 ? 4 : 3;
  try {
    const ip = clientIp(req);
    if (await overLimit(`smb:zorome:${ip}`, 20, 600)) return res.status(429).json({ error: 'too many' });
    const day = new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 10);   // JST
    const keyD = `smb:cp:${day}:${d}`, keyI = `smb:cp:${day}:ip:${ip}`;
    const prevRaw = (await redis('GET', keyD)) || (await redis('GET', keyI));
    let prev = null; if (prevRaw) { try { prev = JSON.parse(prevRaw); } catch (_) {} }
    const stripe = Stripe(process.env.STRIPE_SK);
    const expires = Math.floor(Date.now() / 1000) + TTL_H * 3600;
    let out;
    if (prev && (prev.amount_off || 0) >= AMOUNTS[level]) return res.status(200).json(Object.assign({ again: true }, pub(prev)));
    if (prev) {
      // ¥500 → ¥1,000 への差し替え。古いコードは使えなくする(失敗しても続ける。両方とも1回限りなので害は小さい)
      if (prev.promo_id) { try { await stripe.promotionCodes.update(prev.promo_id, { active: false }); } catch (_) {} }
      out = await issue(stripe, level, expires); out.upgraded = true;
    } else {
      const month = day.slice(0, 7);
      const n = Number(await redis('INCR', `smb:cp:month:${month}`));
      if (n > MONTH_MAX) return res.status(200).json({ error: 'limit', message: '今月のクーポンは上限に達しました' });
      out = await issue(stripe, level, expires);
    }
    const rec = JSON.stringify(out);
    await redis('SET', keyD, rec, 'EX', String(TTL_H * 3600 + 3600));
    await redis('SET', keyI, rec, 'EX', String(TTL_H * 3600 + 3600));
    await redis('LPUSH', 'smb:cp:log', JSON.stringify(Object.assign({ ts: Date.now(), d, ip }, out)));
    await redis('LTRIM', 'smb:cp:log', '0', '999');
    return res.status(200).json(pub(out));
  } catch (e) {
    return serverError(res, e, 'smartball.js');
  }
};
