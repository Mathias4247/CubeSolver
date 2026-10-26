"""Bygger index.html (til publicering) og index.test.html (med test-hook) ud fra template.html.

Løsningsbiblioteket (cubejs, MIT) bliver lagt direkte ind i siden, så den er én selvstændig fil.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
lib = ROOT / 'vendor' / 'cubejs' / 'lib'
t = (ROOT / 'template.html').read_text(encoding='utf-8')
cube = (lib / 'cube.js').read_text(encoding='utf-8')
solve = (lib / 'solve.js').read_text(encoding='utf-8')
for s in (cube, solve):
    assert '</script' not in s.lower()
out = t.replace('/*__CUBE__*/', cube).replace('/*__SOLVE__*/', solve)

def write(name, strip_test):
    o = out
    if strip_test:
        o = re.sub(r'/\*TEST\*/.*?/\*ENDTEST\*/', '', o, flags=re.S)
    (ROOT / name).write_text(o, encoding='utf-8')
    print(name, len(o.encode('utf-8')) // 1024, 'KB')

write('index.test.html', False)
write('index.html', True)
