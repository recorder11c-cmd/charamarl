// クーポン作成API（管理者専用・APPLY_KEY必須）
// POST {key, code:'THANKS100', amount:100, max:50} → Stripeにクーポン+プロモーションコード作成
const Stripe = require('stripe');

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' });
  const b = req.body || {};
  if (!process.env.APPLY_KEY || b.key !== process.env.APPLY_KEY) return res.status(403).json({ error: 'forbidden' });
  try {
    const stripe = Stripe(process.env.STRIPE_SK);
    const amount = Number(b.amount) || 100;
    const code = String(b.code || 'THANKS100').toUpperCase();
    const coupon = await stripe.coupons.create({ amount_off: amount, currency: 'jpy', duration: 'once', name: `¥${amount}引き` });
    const promo = await stripe.promotionCodes.create({ promotion: { type: 'coupon', coupon: coupon.id }, code, max_redemptions: Number(b.max) || 50 });
    return res.status(200).json({ ok: true, code: promo.code, amount_off: amount, max: promo.max_redemptions });
  } catch (e) {
    return res.status(500).json({ error: String((e && e.message) || e) });
  }
};
