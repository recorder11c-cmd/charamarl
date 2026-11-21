// クーポン作成API（管理者専用・APPLY_KEY必須）
// POST {code ...} + X-Admin-Key ヘッダー（または管理者セッション）
// 旧: POST {key, code:'THANKS100', amount:100, max:50} → Stripeにクーポン+プロモーションコード作成
// 任意: min（この合計額以上で使える・円）／expires（この時刻で使えなくなる・UNIX秒）
const Stripe = require('stripe');

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' });
  const b = req.body || {};
  const { isAdminReq } = require('./_lib/admin.js');
  if (!(await isAdminReq(req))) return res.status(403).json({ error: 'forbidden' });
  try {
    const stripe = Stripe(process.env.STRIPE_SK);
    const amount = Number(b.amount) || 100;
    const code = String(b.code || 'THANKS100').toUpperCase();
    const coupon = await stripe.coupons.create({ amount_off: amount, currency: 'jpy', duration: 'once', name: `¥${amount}引き` });
    const extra = {};
    const min = Number(b.min) || 0, expires = Number(b.expires) || 0;
    if (min > 0) extra.restrictions = { minimum_amount: min, minimum_amount_currency: 'jpy' };
    if (expires > 0) extra.expires_at = expires;
    const promo = await stripe.promotionCodes.create({ promotion: { type: 'coupon', coupon: coupon.id }, code, max_redemptions: Number(b.max) || 50, ...extra });
    return res.status(200).json({ ok: true, code: promo.code, amount_off: amount, max: promo.max_redemptions, min: min || null, expires_at: promo.expires_at || null });
  } catch (e) {
    return require('./_lib/admin.js').serverError(res, e, 'coupon.js');
  }
};
