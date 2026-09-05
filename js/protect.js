// 作品画像の「気軽な保存」を抑止する。
//
// ⚠️ これは完全な保護ではありません。スクリーンショットや開発者ツールは防げません。
//    作家さんにもそのとおり説明しています（「守れます」と言って破られるほうが信頼を失うため）。
//    本当の防波堤は robots.txt のAI学習クローラー遮断と利用規約のほうです。
//
// 対象: ギャラリーの作品画像・作品モーダル・アーティストページの作品一覧
(function () {
  var SEL = '#masonry img, #artOverlay img, .works img, .char-visual img, .newrow img';
  var IN = '#masonry, #artOverlay, .works, .char-visual, .newrow';

  // 長押しメニュー・ドラッグ保存を止める
  var st = document.createElement('style');
  st.textContent = SEL.split(',').map(function (s) { return s.trim(); }).join(',') +
    '{-webkit-touch-callout:none;-webkit-user-drag:none;user-drag:none;}';
  (document.head || document.documentElement).appendChild(st);

  function guard() {
    document.querySelectorAll(SEL).forEach(function (im) {
      if (im.dataset.cmGuard) return;
      im.dataset.cmGuard = '1';
      im.setAttribute('draggable', 'false');
      im.addEventListener('dragstart', function (e) { e.preventDefault(); });
    });
  }

  // 右クリック（作品画像の上だけ。ページ全体は普通に使える）
  document.addEventListener('contextmenu', function (e) {
    var t = e.target;
    if (t && t.tagName === 'IMG' && t.closest && t.closest(IN)) e.preventDefault();
  });

  guard();
  document.addEventListener('DOMContentLoaded', guard);
  // 作品は後から差し込まれるので、増えるたびに掛け直す
  try { new MutationObserver(guard).observe(document.documentElement, { childList: true, subtree: true }); } catch (e) {}
})();
