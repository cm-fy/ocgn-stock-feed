import requests
import re
import json

url = 'https://finance.yahoo.com/quote/OCGN'
headers = {'User-Agent': 'Mozilla/5.0'}
resp = requests.get(url, headers=headers, timeout=10)
print('Status:', resp.status_code)

# Check for overnight in text
print('Has 1.99:', '1.99' in resp.text)
positions = [m.start() for m in re.finditer(r'1\.99', resp.text)]
print('Positions of 1.99:', positions)
for pos in positions[:3]:  # first 3
    start = max(0, pos - 50)
    end = min(len(resp.text), pos + 50)
    print(f'Context at {pos}: {repr(resp.text[start:end])}')

overnight_match = re.search(r'Overnight:.*', resp.text)
if overnight_match:
    print('Overnight line:', repr(overnight_match.group(0)[:300]))
else:
    print('No Overnight found')

# Find the script with quoteResponse
matches = re.findall(r'<script type="application/json" data-sveltekit-fetched[^>]*>(.*?)</script>', resp.text, re.DOTALL)
for i, match in enumerate(matches):
    try:
        data = json.loads(match)
        body = data.get('body')
        if body and isinstance(body, str):
            q = json.loads(body)
            if 'quoteResponse' in q:
                result = q.get('quoteResponse', {}).get('result', [{}])[0]
                print(f'Script {i}: Found quoteResponse')
                for key in ['overnightMarketPrice', 'preMarketPrice', 'postMarketPrice', 'regularMarketPrice', 'currentPrice']:
                    if key in result:
                        val = result[key]
                        if isinstance(val, dict):
                            print(f'{key}: {val.get("raw")}')
                        else:
                            print(f'{key}: {val}')
                    else:
                        print(f'{key}: NOT PRESENT')
                break
    except:
        continue
else:
    print('No quoteResponse found')

# Check for prices in HTML
prices = re.findall(r'([0-9]+\.[0-9]{2})', resp.text)
print('All prices in HTML:', prices[:10])