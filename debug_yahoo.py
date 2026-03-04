import requests
import re
import json

url = 'https://finance.yahoo.com/quote/OCGN'
headers = {'User-Agent': 'Mozilla/5.0'}
resp = requests.get(url, headers=headers, timeout=10)
print('Status:', resp.status_code)
matches = re.findall(r'<script type="application/json" data-sveltekit-fetched[^>]*>(.*?)</script>', resp.text, re.DOTALL)
print(f'Found {len(matches)} script tags')
for i, match in enumerate(matches):
    print(f'--- Script {i} ---')
    try:
        data = json.loads(match)
        print('Data keys:', list(data.keys()))
        body = data.get('body')
        if body:
            print('Body type:', type(body))
            if isinstance(body, str):
                q = json.loads(body)
                print('Quote keys:', list(q.keys()))
                result = q.get('quoteResponse', {}).get('result', [])
                if result:
                    print('Result:', result[0])
                else:
                    print('No result')
            else:
                print('Body not str')
        else:
            print('No body')
    except Exception as e:
        print('Error:', e)
    print()

# Also check for price in HTML
price_matches = re.findall(r'([0-9]+\.[0-9]{2})', resp.text)
print('All prices found in HTML:', price_matches[:10])  # first 10