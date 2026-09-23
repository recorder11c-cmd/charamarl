// 台紙AR の認識データ ar/targets.mind を作り直す(マーカー画像を変えたら必ず実行)
// 使い方:
//   mkdir -p /tmp/mindar && cd /tmp/mindar && npm init -y && npm i mind-ar@1.2.5 @tensorflow/tfjs
//   node /Users/KCL/charamarl/tools/ar_compile.mjs   ← /tmp/mindar の中で実行(node_modules を相対で読むため)
// 注意: ブラウザ内のコンパイルは非表示タブで止まるので使わない。mind-ar 同梱の canvas を使う。
import { OfflineCompiler } from './node_modules/mind-ar/src/image-target/offline-compiler.js';
import { loadImage } from './node_modules/mind-ar/node_modules/canvas/index.js';
import { writeFile } from 'fs/promises';
const REPO = '/Users/KCL/charamarl';
// 並び順 = targetIndex。0=70x100mm版(marker.png) 1=名刺55x91mm版(marker_meishi.png)。順番を変えたら ar/index.html と ar/avatar.html の targetIndex も合わせる
const MARKERS = [`${REPO}/ar/marker.png`, `${REPO}/ar/marker_meishi.png`];
const t0 = Date.now();
const imgs = await Promise.all(MARKERS.map((p) => loadImage(p)));
imgs.forEach((im, i) => console.log('marker', i, im.width + 'x' + im.height));
const compiler = new OfflineCompiler();
let last = -1;
await compiler.compileImageTargets(imgs, (p) => { const q = Math.floor(p / 10) * 10; if (q !== last) { last = q; console.log(q + '%', Math.round((Date.now() - t0) / 1000) + 's'); } });
const buf = await compiler.exportData();
await writeFile(`${REPO}/ar/targets.mind`, Buffer.from(buf));
console.log('wrote ar/targets.mind', buf.byteLength, 'bytes', Math.round((Date.now() - t0) / 1000) + 's');
