const Stripe = require('stripe');

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const stripe = Stripe(process.env.STRIPE_SK);

  const { items, successUrl, cancelUrl } = req.body;

  try {
    const session = await stripe.checkout.sessions.create({
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
      success_url: successUrl || `${req.headers.origin}/success.html`,
      cancel_url: cancelUrl || `${req.headers.origin}/cancel.html`,
      shipping_address_collection: {
        allowed_countries: ['JP'],
      },
      locale: 'ja',
    });

    res.status(200).json({ url: session.url });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
