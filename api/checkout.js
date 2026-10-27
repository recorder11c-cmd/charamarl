const Stripe = require('stripe');

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const stripe = Stripe(process.env.STRIPE_SK);

  const { items, successUrl, cancelUrl, coupon } = req.body;
  // スマートボールのゾロ目クーポン(ZORO****/QUAD****)が来たら、決済画面で自動適用する(コードを手で貼らなくてよい)
  //   Stripe では discounts と allow_promotion_codes は同時に使えない。見つからない/失効/最低額未満のときは手入力欄つきで作り直す
  const cpCode = /^(ZORO|QUAD)[A-Z0-9]{4}$/.test(String(coupon || '')) ? String(coupon) : null;

  // Origin が無いリクエストでも壊れないよう固定ベースURLをフォールバック
  const base = req.headers.origin || "https://charamarl.com";

  try {
    let promoId = null;
    if (cpCode) { try { const pl = await stripe.promotionCodes.list({ code: cpCode, active: true, limit: 1 }); if (pl.data[0] && (!pl.data[0].expires_at || pl.data[0].expires_at * 1000 > Date.now())) promoId = pl.data[0].id; } catch (_) {} }
    const params = (withPromo) => ({
      ...(withPromo ? { discounts: [{ promotion_code: promoId }] } : { allow_promotion_codes: true }),
      payment_method_types: ['card'],
      line_items: items.map(item => ({
        price_data: {
          currency: 'jpy',
          product_data: {
            name: item.name,
            images: item.images || [],
          },
          unit_amount: item.price,
        },
        quantity: item.quantity,
      })),
      mode: 'payment',
      success_url: successUrl || `${base}/success.html?sid={CHECKOUT_SESSION_ID}`,
      cancel_url: cancelUrl || `${base}/cancel.html`,
      shipping_address_collection: {
        allowed_countries: ['JP'],
      },
      locale: 'ja',
    });
    let session = null, applied = false;
    if (promoId) { try { session = await stripe.checkout.sessions.create(params(true)); applied = true; } catch (_) { session = null; } }
    if (!session) session = await stripe.checkout.sessions.create(params(false));

    res.status(200).json({ url: session.url, coupon_applied: applied });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
