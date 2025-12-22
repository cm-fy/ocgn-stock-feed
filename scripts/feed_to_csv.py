#!/usr/bin/env python3
import urllib.request
import xml.etree.ElementTree as ET
import re
import os

url = 'https://cm-fy.github.io/ocgn-stock-feed/feed.atom'
print('Fetching', url)
resp = urllib.request.urlopen(url)
data = resp.read()
root = ET.fromstring(data)
ns = {'atom': 'http://www.w3.org/2005/Atom'}
rows = []
for entry in root.findall('atom:entry', ns):
    pub = entry.find('atom:published', ns)
    title = entry.find('atom:title', ns)
    if pub is None or title is None:
        continue
    pubtext = pub.text.strip()
    titletext = ' '.join(title.text.split()) if title.text else ''
    m = re.search(r"\$([0-9]+(?:\.[0-9]+)?)", titletext)
    price = m.group(1) if m else ''
    rows.append((pubtext, price))

# sort chronologically
rows.sort(key=lambda x: x[0])

out_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'feed_prices.csv')
with open(out_path, 'w', newline='', encoding='utf-8') as f:
    f.write('published,price\n')
    for pub, price in rows:
        f.write(f'{pub},{price}\n')

print('Wrote', out_path, 'with', len(rows), 'rows')
