/* ===== CHARAMARL 共有カート (localStorageベース) =====
   使い方:
     <link rel="stylesheet" href="cart.css">  (パス階層に応じて ../ を付ける)
     <script src="cart.js"></script>
     ヘッダーに <span data-cart-mount></span> を置く（カゴボタンが自動で入る）
     商品側: CHARAMARL_CART.add(char, color, name, colorName, price)
*/
(function(){
  const KEY = 'charamarl_cart';
  const PROD_BASE = 'https://charamarl.vercel.app';
  const img = (char,color) => `/img/colors_nobg/${char}_${color}.png`;          // サムネ(ルート相対)
  const imgAbs = (char,color) => `${PROD_BASE}/img/colors_nobg/${char}_${color}.png`; // 決済用(公開HTTPS)

  function get(){ try { return JSON.parse(localStorage.getItem(KEY)||'[]'); } catch(e){ return []; } }
  function save(c){ localStorage.setItem(KEY, JSON.stringify(c)); render(); }

  // --- カゴボタンを mount に設置 ---
  const mount = document.querySelector('[data-cart-mount]');
  if (mount) {
    mount.innerHTML = '<button class="cart-btn" id="cartBtn" aria-label="カート">🛍<span class="cart-count empty" id="cartCount">0</span></button>';
  }

  // --- ドロワーを body に注入 ---
  const wrap = document.createElement('div');
  wrap.innerHTML = `
    <div class="cart-overlay" id="cartOverlay"></div>
    <aside class="cart-drawer" id="cartDrawer" aria-label="カート">
      <div class="cart-head"><h3>🛍 カート</h3><button class="cart-close" id="cartClose" aria-label="閉じる">×</button></div>
      <div class="cart-items" id="cartItems"></div>
      <div class="cart-foot" id="cartFoot" style="display:none;">
        <div class="cart-total"><span class="lbl">合計</span><span class="amt" id="cartTotal">¥0</span></div>
        <button class="cart-checkout" id="cartCheckout">まとめて購入する →</button>
      </div>
    </aside>`;
  document.body.appendChild(wrap);

  const itemsEl = document.getElementById('cartItems');
  const countEl = () => document.getElementById('cartCount');
  const drawer = document.getElementById('cartDrawer');
  const overlay = document.getElementById('cartOverlay');

  function render(){
    const cart = get();
    const count = cart.reduce((s,i)=>s+i.qty,0);
    const cc = countEl();
    if (cc) { cc.textContent = count; cc.classList.toggle('empty', count===0); }
    const foot = document.getElementById('cartFoot');
    if (cart.length===0){
      itemsEl.innerHTML = '<div class="cart-empty">カートは空です。<br>キャラクターを選んで追加してください。</div>';
      foot.style.display='none'; return;
    }
    foot.style.display='block';
    document.getElementById('cartTotal').textContent = '¥'+cart.reduce((s,i)=>s+i.price*i.qty,0).toLocaleString();
    itemsEl.innerHTML = cart.map(i=>`
      <div class="cart-item">
        <img src="${i.img || img(i.char,i.color)}" alt="${i.name}">
        <div class="cart-item-info">
          <div class="cart-item-name">${i.name} アクキー</div>
          <div class="cart-item-color">${i.colorName}</div>
          <div class="cart-item-price">¥${i.price.toLocaleString()}</div>
        </div>
        <div class="cart-qty">
          <button data-dec="${i.id}">−</button><span>${i.qty}</span><button data-inc="${i.id}">＋</button>
        </div>
        <button class="cart-remove" data-rm="${i.id}">削除</button>
      </div>`).join('');
  }

  itemsEl.addEventListener('click', e=>{
    const t=e.target, cart=get();
    if(t.dataset.inc){ const it=cart.find(i=>i.id===t.dataset.inc); if(it){it.qty++; save(cart);} }
    else if(t.dataset.dec){ let it=cart.find(i=>i.id===t.dataset.dec); if(it){it.qty--; save(it.qty<=0?cart.filter(i=>i.id!==it.id):cart);} }
    else if(t.dataset.rm){ save(cart.filter(i=>i.id!==t.dataset.rm)); }
  });

  function openCart(){ render(); drawer.classList.add('open'); overlay.classList.add('open'); document.body.style.overflow='hidden'; }
  function closeCart(){ drawer.classList.remove('open'); overlay.classList.remove('open'); document.body.style.overflow=''; }
  const cb=document.getElementById('cartBtn'); if(cb) cb.addEventListener('click', openCart);
  document.getElementById('cartClose').addEventListener('click', closeCart);
  overlay.addEventListener('click', closeCart);

  document.getElementById('cartCheckout').addEventListener('click', async ()=>{
    const cart=get(); if(cart.length===0) return;
    const btn=document.getElementById('cartCheckout'); btn.textContent='処理中...'; btn.disabled=true;
    try{
      const res=await fetch('/api/checkout',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({ items: cart.map(i=>({ name:`${i.name} アクリルキーホルダー ${i.colorName}`, price:i.price, quantity:i.qty, images:[i.img ? PROD_BASE+i.img : imgAbs(i.char,i.color)] })) })});
      const data=await res.json();
      if(data.url){ window.location.href=data.url; }
      else { alert('エラー: '+(data.error||'不明')); btn.textContent='まとめて購入する →'; btn.disabled=false; }
    }catch(e){ alert('通信エラー'); btn.textContent='まとめて購入する →'; btn.disabled=false; }
  });

  // 公開API
  window.CHARAMARL_CART = {
    add(char, color, name, colorName, price, imgPath){
      const cart=get(); const id=char+'_'+color;
      const ex=cart.find(i=>i.id===id);
      if(ex) ex.qty++; else cart.push({ id, char, color, name, colorName, price:price||1200, qty:1, img:imgPath||null });
      save(cart);
    },
    open: openCart
  };

  render(); // 初期バッジ
})();
