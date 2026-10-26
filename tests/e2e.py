import os, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
TMP = tempfile.mkdtemp(prefix='kubeloeser-')
import json, random, subprocess, math, sys
from PIL import Image, ImageDraw, ImageFilter
from playwright.sync_api import sync_playwright

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
HARD = '--hard' in sys.argv  # dårligere lys, større forskydning, mere genskær
random.seed(seed)
# true scrambled cube (letters = faces, standard colours: U white, R red, F green, D yellow, L orange, B blue)
truth = subprocess.check_output(['node','-e',"const C=require(process.argv[1]);console.log(C.random().asString())", str(ROOT / 'vendor' / 'cubejs' / 'index.js')]).decode().strip()
RGB = {'U':(240,240,235),'R':(205,30,40),'F':(25,160,70),'D':(246,210,0),'L':(245,125,20),'B':(20,85,190)}
ORDER = ['F','R','B','L','U','D']
OFF = {f:i*9 for i,f in enumerate('URFDLB')}

def photo(face, path):
    W,H = 1000,800
    bg = tuple(random.randint(90,140) for _ in range(3))
    im = Image.new('RGB',(W,H),bg); d = ImageDraw.Draw(im)
    cell, gap = 165, 10
    # lighting for this photo: brightness, colour cast
    bright = (random.uniform(0.50,1.20) if HARD else random.uniform(0.72,1.12)); cast = [(random.uniform(0.80,1.20) if HARD else random.uniform(0.90,1.10)) for _ in range(3)]
    cx, cy = W/2 + (random.uniform(-70,70) if HARD else random.uniform(-35,35)), H/2 + (random.uniform(-50,50) if HARD else random.uniform(-30,30))
    tile = Image.new('RGB',(3*cell+4*gap,3*cell+4*gap),(15,15,18)); td = ImageDraw.Draw(tile)
    for i in range(9):
        r,c = divmod(i,3); col = RGB[truth[OFF[face]+i]]
        col = tuple(max(0,min(255,int(v*bright*cast[k]))) for k,v in enumerate(col))
        x0 = gap + c*(cell+gap); y0 = gap + r*(cell+gap)
        td.rounded_rectangle([x0,y0,x0+cell,y0+cell],radius=14,fill=col)
        if random.random()<(0.5 if HARD else 0.25):  # glare spot on one sticker
            gx,gy = x0+random.randint(30,cell-30), y0+random.randint(30,cell-30)
            td.ellipse([gx-18,gy-18,gx+18,gy+18],fill=tuple(min(255,v+70) for v in col))
    tile = tile.rotate(random.uniform(-4,4), expand=True, resample=Image.BICUBIC, fillcolor=bg)
    im.paste(tile,(int(cx-tile.width/2),int(cy-tile.height/2)))
    # noise
    px = im.load()
    for _ in range(40000):
        x,y = random.randrange(W), random.randrange(H); r,g,b = px[x,y]; n = random.randint(-14,14); px[x,y] = (max(0,min(255,r+n)),max(0,min(255,g+n)),max(0,min(255,b+n)))
    im = im.filter(ImageFilter.GaussianBlur(1.2))
    im.save(path)

paths = []
for f in ORDER:
    p = f'{TMP}/{f}.png'; photo(f,p); paths.append(p)

with sync_playwright() as pw:
    b = pw.chromium.launch(); ctx = b.new_context(viewport={'width':430,'height':900}); pg = ctx.new_page()
    errs=[]; pg.on('pageerror', lambda e: errs.append('PAGEERR '+str(e)))
    pg.goto('file://' + str(ROOT / 'index.test.html')); pg.wait_for_timeout(300)
    pg.click('#btn-start')
    for i,p in enumerate(paths):
        pg.set_input_files('#in-gal', p); pg.wait_for_selector('#cap-right:not([hidden])'); pg.wait_for_timeout(150)
        pg.click('#btn-use'); pg.wait_for_timeout(100)
    pg.wait_for_selector('#s-review:not([hidden])')
    grid = pg.evaluate("window.__kubeloeser.S().grid.join('')")
    warn = pg.evaluate("Object.keys(window.__kubeloeser.S().warn).length")
    print('truth:', truth); print('read :', grid)
    wrong = [i for i in range(54) if grid[i]!=truth[i]]
    print('seed',seed,'wrong stickers:', len(wrong), wrong, '| flagged uncertain:', warn)
    msg = pg.inner_text('#rev-msg'); print('review msg:', msg, '| solve enabled:', pg.is_enabled('#btn-solve'))
    pg.screenshot(path=f'{TMP}/review_{seed}.png', full_page=True)
    if pg.is_enabled('#btn-solve'):
        pg.click('#btn-solve'); pg.wait_for_selector('#s-solve:not([hidden])', timeout=30000)
        title = pg.inner_text('#sol-title'); n = pg.evaluate('window.__kubeloeser.S().moves.length')
        print('solve screen:', title)
        # step through every move, then check last state solved
        for _ in range(n): pg.click('#btn-next')
        done = pg.inner_text('#now'); print('after last move:', done.replace('\n',' | '))
        last = pg.evaluate("window.__kubeloeser.S().states.slice(-1)[0]")
        print('final solved:', last == 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB')
        pg.screenshot(path=f'{TMP}/solve_{seed}.png', full_page=True)
    print('errors:', errs)
    b.close()
