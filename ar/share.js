// CHARAMARL AR 共通: 画面の写真(カメラ映像+3D)を作ってシェアする
// 使い方: CM_AR_SHARE.snapshot({video, gl}) → canvas / CM_AR_SHARE.share({canvas, text, url}) → Promise
(function(){
  function coverDraw(ctx, src, W, H){
    var vw = src.videoWidth || src.width, vh = src.videoHeight || src.height;
    if(!vw || !vh) return;
    var s = Math.max(W / vw, H / vh), sw = W / s, sh = H / s;
    ctx.drawImage(src, (vw - sw) / 2, (vh - sh) / 2, sw, sh, 0, 0, W, H);
  }
  function watermark(ctx, W, H, label){
    label = label || 'charamarl.com';
    var u = Math.max(W, H) / 1000;                 // 1000px基準で拡縮
    var pad = 28 * u, r = 22 * u, h = 76 * u;
    ctx.save();
    ctx.font = '900 ' + Math.round(34 * u) + 'px "Helvetica Neue", Arial, sans-serif';
    var tw = ctx.measureText('CHARAMARL').width;
    ctx.font = '700 ' + Math.round(20 * u) + 'px "Helvetica Neue", Arial, sans-serif';
    var tw2 = ctx.measureText(label).width;
    var w = Math.max(tw, tw2) + pad * 2, x = pad, y = H - pad - h;
    ctx.fillStyle = 'rgba(255,255,255,0.92)';
    ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); ctx.fill();
    ctx.textBaseline = 'alphabetic';
    ctx.font = '900 ' + Math.round(34 * u) + 'px "Helvetica Neue", Arial, sans-serif';
    ctx.fillStyle = '#FF8A00'; ctx.fillText('CHARA', x + pad, y + 40 * u);
    var cw = ctx.measureText('CHARA').width;
    ctx.fillStyle = '#A855F7'; ctx.fillText('MARL', x + pad + cw, y + 40 * u);
    ctx.font = '700 ' + Math.round(20 * u) + 'px "Helvetica Neue", Arial, sans-serif';
    ctx.fillStyle = '#111'; ctx.fillText(label, x + pad, y + 64 * u);
    ctx.restore();
  }
  // カメラ映像の上に3Dの描画を重ねる。gl(WebGLキャンバス)は描画直後に渡すこと
  function snapshot(o){
    var gl = o.gl, W = gl.width, H = gl.height;
    var c = document.createElement('canvas'); c.width = W; c.height = H;
    var ctx = c.getContext('2d');
    ctx.fillStyle = '#111'; ctx.fillRect(0, 0, W, H);
    if(o.video) coverDraw(ctx, o.video, W, H);
    ctx.drawImage(gl, 0, 0, W, H);
    watermark(ctx, W, H, o.label);
    return c;
  }
  function toBlob(canvas){ return new Promise(function(res){ canvas.toBlob(function(b){ res(b); }, 'image/jpeg', 0.92); }); }
  function css(){
    if(document.getElementById('cmShareCss')) return;
    var s = document.createElement('style'); s.id = 'cmShareCss';
    s.textContent = '.cmsh{position:fixed;inset:0;z-index:900;background:rgba(0,0,0,.82);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;padding:20px;font-family:"M PLUS Rounded 1c","Hiragino Maru Gothic ProN",sans-serif;}'
      + '.cmsh img{max-width:80vw;max-height:56vh;border-radius:14px;box-shadow:0 10px 30px rgba(0,0,0,.5);}'
      + '.cmsh .t{color:#fff;font-weight:900;font-size:15px;text-align:center;line-height:1.5;}'
      + '.cmsh .row{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;}'
      + '.cmsh button,.cmsh a{font-family:inherit;font-weight:900;font-size:14px;padding:12px 18px;border-radius:30px;border:3px solid #fff;background:#fff;color:#111;text-decoration:none;cursor:pointer;}'
      + '.cmsh .x{background:#111;color:#fff;}'
      + '.cmtoast{position:fixed;left:50%;bottom:calc(env(safe-area-inset-bottom) + 96px);transform:translateX(-50%);z-index:950;background:#111;color:#fff;font-weight:900;font-size:14px;padding:12px 18px;border-radius:30px;box-shadow:0 6px 0 rgba(0,0,0,.25);max-width:88vw;text-align:center;line-height:1.4;font-family:"M PLUS Rounded 1c","Hiragino Maru Gothic ProN",sans-serif;transition:opacity .4s;}';
    document.head.appendChild(s);
  }
  function toast(msg){
    css(); var t = document.createElement('div'); t.className = 'cmtoast'; t.textContent = msg; document.body.appendChild(t);
    setTimeout(function(){ t.style.opacity = '0'; setTimeout(function(){ t.remove(); }, 450); }, 3200);
  }
  // 端末の共有シート(画像付き)→無理なら画面に画像を出して保存してもらう
  // ※iPhoneは画像を渡すと文章が落ちるアプリが多いので、文章とリンクはクリップボードにも入れておく(呼び出し側でコピー済み)
  function share(o){
    return toBlob(o.canvas).then(function(blob){
      var file = new File([blob], 'charamarl_ar.jpg', { type: 'image/jpeg' });
      var text = o.text + '\n' + o.url;
      if(navigator.canShare && navigator.canShare({ files: [file] })){
        return navigator.share({ files: [file], text: text, title: 'CHARAMARL' }).then(function(){ if(o.copied) toast('文章とリンクはコピー済み。投稿に貼りつけてね'); return 'native'; }).catch(function(e){ if(e && e.name === 'AbortError') return 'cancel'; return fallback(blob, o); });
      }
      return fallback(blob, o);
    });
  }
  function fallback(blob, o){
    css();
    var url = URL.createObjectURL(blob);
    var box = document.createElement('div'); box.className = 'cmsh';
    box.innerHTML = '<img alt="AR写真"><div class="t">画像を長押しで保存できます<br>Xに投稿するときは、保存した画像を添えてください</div><div class="row"><a class="x" target="_blank" rel="noopener">Xで投稿</a><button type="button" data-c>リンクをコピー</button><button type="button" data-x>閉じる</button></div>';
    box.querySelector('img').src = url;
    box.querySelector('a.x').href = 'https://twitter.com/intent/tweet?text=' + encodeURIComponent(o.text) + '&url=' + encodeURIComponent(o.url);
    box.querySelector('[data-c]').addEventListener('click', function(){ if(navigator.clipboard) navigator.clipboard.writeText(o.url).catch(function(){}); this.textContent = 'コピーしました'; });
    box.querySelector('[data-x]').addEventListener('click', function(){ box.remove(); URL.revokeObjectURL(url); });
    document.body.appendChild(box);
    return 'fallback';
  }
  // 文章+リンクをクリップボードへ(タップ直後に呼ぶこと。あとで呼ぶとiPhoneが拒否する)
  function copyText(text){
    try{ if(navigator.clipboard && navigator.clipboard.writeText){ navigator.clipboard.writeText(text).catch(function(){}); return true; } }catch(e){}
    return false;
  }
  window.CM_AR_SHARE = { snapshot: snapshot, share: share, copyText: copyText, toast: toast };
})();
