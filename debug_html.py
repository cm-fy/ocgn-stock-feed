import requests
import re
import time

url = f"https://finance.yahoo.com/quote/OCGN?t={int(time.time())}"
headers = {"User-Agent": "Mozilla/5.0"}
resp = requests.get(url, headers=headers, timeout=10)

# Search for qsp-overnight-price
match = re.search(r'data-testid="qsp-overnight-price">(.*?)</span>', resp.text)
if match:
    print(f"Found qsp-overnight-price: {match.group(1)}")
else:
    print("qsp-overnight-price not found in HTML")

# Also check for the close percentage
close_match = re.search(r'\(-4\.12%\)', resp.text)
if close_match:
    print("Found (-4.12%) in HTML")
    # Get some context
    start = max(0, close_match.start() - 100)
    end = min(len(resp.text), close_match.end() + 100)
    print("Context around (-4.12%):")
    print(resp.text[start:end])
else:
    print("(-4.12%) not found in HTML")

# Check for any overnight price mentions
overnight_matches = re.findall(r'overnight.*?([0-9]+\.[0-9]{4})', resp.text, re.IGNORECASE)
if overnight_matches:
    print(f"Overnight price matches: {overnight_matches}")
else:
    print("No overnight price matches found")