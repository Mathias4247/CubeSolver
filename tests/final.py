import os, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
TMP = tempfile.mkdtemp(prefix='kubeloeser-')
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch()
    # (a) production file, Worker unavailable -> main-thread fallback
    ctx = b.new_context(); ctx.add_init_script("window.Worker = undefined;")
    pg = ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + str(ROOT / 'index.html')); pg.wait_for_timeout(300)
    pg.click('#btn-demo'); pg.wait_for_selector('#s-review:not([hidden])'); pg.click('#btn-solve')
    pg.wait_for_selector('#s-solve:not([hidden])', timeout=30000)
    n = pg.locator('#chips .mv').count()
    for _ in range(n): pg.click('#btn-next')
    print('(a) fallback solve:', pg.inner_text('#sol-title'), '->', pg.inner_text('#now').replace('\n',' | '), '| errors:', errs)
    ctx.close()
    # (b) correct a sticker by tapping, on the test build
    pg = b.new_page(); pg.goto('file://' + str(ROOT / 'index.test.html')); pg.wait_for_timeout(300)
    pg.click('#btn-demo'); pg.wait_for_selector('#s-review:not([hidden])')
    truth = pg.evaluate("window.__kubeloeser.S().grid.join('')")
    # find a non-center sticker, recolour it to a different class
    i = 0
    while i % 9 == 4 or truth[i] == 'U': i += 1
    pg.click(f'.stk[data-i="{i}"]'); pg.wait_for_selector('#palette:not([hidden])')
    pg.click('#pal button[data-c="white"]')
    print('(b) after wrong colour:', pg.inner_text('#rev-msg'), '| solve enabled:', pg.is_enabled('#btn-solve'))
    pg.click(f'.stk[data-i="{i}"]'); orig = {'U':'white','R':'red','F':'green','D':'yellow','L':'orange','B':'blue'}[truth[i]]
    pg.click(f'#pal button[data-c="{orig}"]')
    print('(b) after fixing it:', pg.inner_text('#rev-msg'), '| solve enabled:', pg.is_enabled('#btn-solve'))
    b.close()
