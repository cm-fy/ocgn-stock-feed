import requests
import re
url = 'https://finance.yahoo.com/quote/OCGN'
resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
tooltip_match = re.search(r'<td class="hu-tooltip-value">(.*?)</td>', resp.text)
if tooltip_match:
    print('Tooltip value:', repr(tooltip_match.group(1)))
else:
    print('No tooltip match')