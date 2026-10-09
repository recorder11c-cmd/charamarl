// JUNKeeeeS FES チラシAR の認識データ ar/fes/targets.mind を作る(チラシの表面が変わったら必ず実行)。実行は /tmp/mindar の中で(tools/ar_compile.mjs と同じ手順)

import { OfflineCompiler } from './node_modules/mind-ar/src/image-target/offline-compiler.js';
import { loadImage } from './node_modules/canvas/index.js';
import { writeFile } from 'fs/promises';
const REPO='/Users/KCL/charamarl'; const t0=Date.now();
const imgs=await Promise.all([`${REPO}/ar/fes/marker_flyer.png`].map(p=>loadImage(p)));
const c=new OfflineCompiler(); let last=-1;
await c.compileImageTargets(imgs,(p)=>{const q=Math.floor(p/10)*10; if(q!==last){last=q; console.log(q+'%',Math.round((Date.now()-t0)/1000)+'s');}});
const buf=await c.exportData(); await writeFile(`${REPO}/ar/fes/targets.mind`,Buffer.from(buf)); console.log('wrote',buf.byteLength,'bytes');
