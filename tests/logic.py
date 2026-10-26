import os, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
TMP = tempfile.mkdtemp(prefix='kubeloeser-')
from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
    pg.goto('file://' + str(ROOT / 'index.test.html')); pg.wait_for_timeout(500)
    res = pg.evaluate("""() => {
      const K = window.__kubeloeser, out = {valid:0, invalidAccepted:0, n:600, mutFail:0, mutTotal:0, swapAccepted:0, twistAccepted:0};
      const rnd = n => Math.floor(Math.random()*n);
      for (let i=0;i<out.n;i++){
        const s = Cube.random().asString();
        if (K.verify(s).ok) out.valid++;
        // swap two non-center stickers of different color -> usually invalid
        let a=rnd(54), c=rnd(54); 
        if (a%9==4||c%9==4||s[a]==s[c]) continue;
        const arr=s.split(''); [arr[a],arr[c]]=[arr[c],arr[a]];
        out.mutTotal++;
        const v=K.verify(arr.join(''));
        if(!v.ok) out.mutFail++;
        else { // if accepted, make sure cubejs can really solve it (it is a legal cube)
          try{ const sol=Cube.fromString(arr.join('')).solve(); const c2=Cube.fromString(arr.join('')); c2.move(sol); if(!c2.isSolved()) out.swapAccepted++; }catch(e){ out.swapAccepted++; }
        }
      }
      // twist a single corner (rotate its three stickers) -> must be rejected
      let s = Cube.random().asString().split('');
      const t = [8, 9, 20]; // URF corner facelets U9,R1,F3
      const tmp=s[t[0]]; s[t[0]]=s[t[1]]; s[t[1]]=s[t[2]]; s[t[2]]=tmp;
      out.twistAccepted = K.verify(s.join('')).ok ? 1 : 0;
      out.twistMsg = K.verify(s.join('')).msg;
      return out;
    }""")
    print(json.dumps(res, ensure_ascii=False, indent=1)); print('errors:', errs)
    b.close()
