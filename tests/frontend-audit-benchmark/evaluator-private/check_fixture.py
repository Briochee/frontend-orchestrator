#!/usr/bin/env python3
"""Stdlib-only static fixture health check. Does not claim a browser or visual audit."""
from pathlib import Path
from html.parser import HTMLParser
import subprocess

ROOT = Path(__file__).resolve().parents[1] / 'demo-app'
PAGES = [ROOT / 'index.html'] + [ROOT / x / 'index.html' for x in ('orders','analytics','customers','settings')]
class Elements(HTMLParser):
    def __init__(self): super().__init__(); self.titles=0;self.mains=0;self.navs=0;self.scripts=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='h1':self.titles+=1
        if tag=='main':self.mains+=1
        if tag=='nav':self.navs+=1
        if tag=='script' and attrs.get('src'):self.scripts.append(attrs['src'])

for page in PAGES:
    assert page.is_file(),f'Missing route: {page}'
    parser=Elements();parser.feed(page.read_text())
    assert parser.titles==1 and parser.mains==1 and parser.navs>=1,(page,parser.__dict__)
    for script in parser.scripts:
        assert (page.parent/script).resolve().is_file(),(page,script)
    print('OK page:',page.relative_to(ROOT),'scripts:',len(parser.scripts))
for js in (ROOT/'src').glob('*.js'):
    subprocess.run(['node','--check',str(js)],check=True)
print('OK JavaScript syntax')
subprocess.run(['node','--test',str(ROOT/'tests/smoke.test.mjs')],check=True)
print('STATIC FIXTURE CHECK PASSED (not a browser audit)')
