#!/usr/bin/env python3
"""Check the real production output, without a third-party test dependency."""
import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
HOST = 'aquariniquemu.github.io'
KNOWN_MISSING = {'考研政治早期笔记.pdf', '写作模板.docx', '杨鸿文老师通信原理讲义.zip', '通信原理知识点_withMarginNotes.pdf', '复试英语问题简略.docx'}
class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.links=[]; self.images=[]; self.scripts=[]; self.math=0; self.lang=''; self.feed(text)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='html': self.lang=a.get('lang','')
        if tag=='math': self.math+=1
        if tag=='img': self.images.append(a)
        if tag=='script' and a.get('src'): self.scripts.append(a['src'])
        if tag in ('a','link') and a.get('href'): self.links.append(a['href'])
        if tag in ('img','script') and a.get('src'): self.links.append(a['src'])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--public-dir',default='public');args=ap.parse_args()
    public=Path(args.public_dir).resolve(); errors=[]; known=set(); count=0; maths=0; galleries=0
    def fail(message):errors.append(message)
    for required in ('index.html','index.json','index.xml','sitemap.xml','robots.txt','posts/index.html','notes/index.html','travel/index.html','archives/index.html','about/index.html','fonts/inter-latin.woff2'):
        if not (public/required).is_file():fail('Missing '+required)
    for file in public.rglob('*.html'):
        text=file.read_text();doc=Document(text);count+=1;rel=file.relative_to(public).as_posix();maths+=doc.math
        if 'livereload.js' in text:fail(f'{rel}: development script in production')
        if not doc.lang and 'http-equiv' not in text.lower():fail(f'{rel}: missing document language')
        for src in doc.scripts:
            if any(x in src.lower() for x in ('katex','mathjax','jquery','packery','medium-zoom')):fail(f'{rel}: unwanted client script {src}')
        has_gallery='class="photo-gallery"' in text or 'class=photo-gallery' in text
        glight=any('glightbox' in s for s in doc.scripts)
        if has_gallery!=glight:fail(f'{rel}: gallery/resource condition mismatch')
        galleries+=int(has_gallery)
        for img in doc.images:
            # Blowfish card thumbnails are absolutely positioned inside fixed-size wrappers.
            reserved='absolute' in img.get('class','') and 'h-full' in img.get('class','')
            if not reserved and not (img.get('width') and img.get('height')):fail(f'{rel}: image has no intrinsic size {img.get("src")}')
            if not img.get('alt') and img.get('role')!='presentation':fail(f'{rel}: image missing alternative text')
        current='https://'+HOST+'/'+rel.removesuffix('index.html')
        for value in doc.links:
            u=urlsplit(urljoin(current,value))
            if u.scheme not in ('http','https') or u.hostname!=HOST:continue
            path=unquote(u.path).lstrip('/');target=public/path
            if not target.is_file() and not (target/'index.html').is_file():
                if Path(path).name in KNOWN_MISSING and rel.startswith('notes/2022/04/postgraduate-exam-reflections/'):
                    known.add(Path(path).name)
                else:fail(f'{rel}: broken local target {value}')
    # Drafts must be absent from both HTML and the search index.
    index=(public/'index.json').read_text() if (public/'index.json').exists() else '[]'
    try:json.loads(index)
    except ValueError:fail('Invalid search index JSON')
    for file in (ROOT/'content').rglob('index.md'):
        text=file.read_text();front=text.split('---',2)[1] if text.startswith('---') else ''
        if re.search(r'^draft:\s*true\s*$',front,re.M):
            slug=re.search(r'^slug:\s*["\']?([^"\'\n]+)',front,re.M)
            if slug:
                value=slug.group(1).strip()
                if any(p.parent.name==value for p in public.rglob('index.html')) or value in index:fail(f'Draft leaked: {file.relative_to(ROOT)}')
        if re.search(r'^math:\s*true',front,re.M) or re.search(r'\{\{[<%]\s*katex',text):fail(f'Client math forbidden: {file.relative_to(ROOT)}')
    if maths<2:fail('Expected both inline and block MathML in the notebook entry')
    if galleries<1:fail('Expected the migrated travel gallery')
    try:
        rss=ET.parse(public/'index.xml');items=rss.findall('./channel/item')
        if not items:fail('RSS is empty')
        for item in items:
            if len(item.findtext('description',''))<100:fail('RSS contains empty/truncated entry: '+item.findtext('title',''))
        ET.parse(public/'sitemap.xml')
    except (ET.ParseError,FileNotFoundError) as e:fail(f'Invalid XML: {e}')
    if errors:
        print('\n'.join('FAIL: '+x for x in errors));return 1
    print(f'PASS: {count} HTML pages; {maths} MathML expressions; {galleries} gallery pages; local assets, draft exclusion, search JSON, RSS and sitemap verified.')
    if known:print(f'Known legacy limitation: {len(known)} pre-existing unavailable attachments (docs/MIGRATION.md).')
    return 0
if __name__=='__main__':sys.exit(main())
