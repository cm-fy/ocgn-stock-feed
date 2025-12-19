#!/usr/bin/env python3
"""
Fetch OCGN stock price data including extended hours and generate an Atom feed.
"""

import yfinance as yf
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os

# Configuration
GITHUB_PAGES_BASE_URL = os.environ.get('GITHUB_PAGES_URL', 'https://cm-fy.github.io/ocgn-stock-feed')
FEED_URL = f"{GITHUB_PAGES_BASE_URL}/feed.atom"


def fetch_ocgn_data():
    """Fetch OCGN stock data including extended hours trading."""
    try:
        ticker = yf.Ticker("OCGN")
        
        # Get current stock info
        info = ticker.info
        
        # Get historical data for the last day with extended hours
        hist = ticker.history(period="1d", interval="1m", prepost=True)
        
        return info, hist
    except Exception as e:
        # Log the error for debugging
        print(f"Error fetching data from yfinance: {type(e).__name__}: {e}")
        # Return empty data structures on error
        return {}, None


def generate_atom_feed(info, hist):
    """Generate an Atom feed from stock data."""
    # Create the root element
    feed = ET.Element('feed', xmlns='http://www.w3.org/2005/Atom')
    
    # Add feed metadata
    title = ET.SubElement(feed, 'title')
    title.text = 'OCGN Stock Price Feed'
    
    link = ET.SubElement(feed, 'link', href=FEED_URL, rel='self')
    
    feed_id = ET.SubElement(feed, 'id')
    feed_id.text = FEED_URL
    
    updated = ET.SubElement(feed, 'updated')
    updated.text = datetime.now(timezone.utc).isoformat()
    
    author = ET.SubElement(feed, 'author')
    author_name = ET.SubElement(author, 'name')
    author_name.text = 'OCGN Stock Feed Bot'
    
    # Handle empty info dict (no data available)
    if not info:
        # Add a placeholder entry when data is unavailable
        entry = ET.SubElement(feed, 'entry')
        
        entry_title = ET.SubElement(entry, 'title')
        entry_title.text = "OCGN: Data unavailable"
        
        entry_link = ET.SubElement(entry, 'link', href='https://finance.yahoo.com/quote/OCGN')
        
        entry_id = ET.SubElement(entry, 'id')
        entry_id.text = f"ocgn-{datetime.now(timezone.utc).isoformat()}"
        
        entry_updated = ET.SubElement(entry, 'updated')
        entry_updated.text = datetime.now(timezone.utc).isoformat()
        
        content = ET.SubElement(entry, 'content', type='html')
        content.text = f"""<div>
    <h2>OCGN Stock Price Update</h2>
    <p>Stock data is temporarily unavailable. Please check back later.</p>
    <p><strong>Last Updated:</strong> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
</div>"""
        return feed
    
    # Get current price information
    current_price = info.get('currentPrice') or info.get('regularMarketPrice', 'N/A')
    previous_close = info.get('previousClose', 'N/A')
    
    # Calculate change
    if isinstance(current_price, (int, float)) and isinstance(previous_close, (int, float)):
        change = current_price - previous_close
        change_percent = (change / previous_close) * 100
    else:
        change = 'N/A'
        change_percent = 'N/A'
    
    # Get market state
    market_state = info.get('marketState', 'UNKNOWN')
    
    # Add entry for current price
    entry = ET.SubElement(feed, 'entry')
    
    entry_title = ET.SubElement(entry, 'title')
    if isinstance(current_price, (int, float)):
        entry_title.text = f"OCGN: ${current_price:.2f}"
    else:
        entry_title.text = f"OCGN: {current_price}"
    
    entry_link = ET.SubElement(entry, 'link', href='https://finance.yahoo.com/quote/OCGN')
    
    entry_id = ET.SubElement(entry, 'id')
    entry_id.text = f"ocgn-{datetime.now(timezone.utc).isoformat()}"
    
    entry_updated = ET.SubElement(entry, 'updated')
    entry_updated.text = datetime.now(timezone.utc).isoformat()
    
    # Create content with price details
    content = ET.SubElement(entry, 'content', type='html')
    content_html = f"""<div>
    <h2>OCGN Stock Price Update</h2>
    <p><strong>Current Price:</strong> ${current_price if isinstance(current_price, (int, float)) else current_price}</p>
    <p><strong>Previous Close:</strong> ${previous_close if isinstance(previous_close, (int, float)) else previous_close}</p>"""
    
    if isinstance(change, (int, float)) and isinstance(change_percent, (int, float)):
        content_html += f"""
    <p><strong>Change:</strong> ${change:.2f} ({change_percent:+.2f}%)</p>"""
    
    content_html += f"""
    <p><strong>Market State:</strong> {market_state}</p>
    <p><strong>Last Updated:</strong> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
"""
    
    # Add extended hours info if available
    if hist is not None and not hist.empty and len(hist) > 0:
        try:
            latest_row = hist.iloc[-1]
            content_html += f"""
    <h3>Latest Trading Data (Including Extended Hours)</h3>
    <p><strong>Open:</strong> ${latest_row['Open']:.2f}</p>
    <p><strong>High:</strong> ${latest_row['High']:.2f}</p>
    <p><strong>Low:</strong> ${latest_row['Low']:.2f}</p>
    <p><strong>Close:</strong> ${latest_row['Close']:.2f}</p>
    <p><strong>Volume:</strong> {int(latest_row['Volume']):,}</p>
    <p><strong>Timestamp:</strong> {latest_row.name.strftime('%Y-%m-%d %H:%M:%S %Z')}</p>
"""
        except (KeyError, IndexError, ValueError) as e:
            print(f"Warning: Could not extract historical data: {type(e).__name__}: {e}")
    
    content_html += """
</div>"""
    content.text = content_html
    
    return feed


def prettify_xml(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')


def main():
    """Main function to fetch data and generate feed."""
    print("Fetching OCGN stock data...")
    info, hist = fetch_ocgn_data()
    
    print("Generating Atom feed...")
    feed = generate_atom_feed(info, hist)
    
    print("Writing feed to file...")
    feed_xml = prettify_xml(feed)
    
    # Ensure output directory exists
    os.makedirs('docs', exist_ok=True)
    
    output_path = 'docs/feed.atom'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(feed_xml)
    
    print(f"Feed generated successfully: {output_path}")
    
    # Also create an index.html for GitHub Pages
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OCGN Stock Feed</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{ color: #333; }}
        .feed-link {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        code {{
            background-color: #e8e8e8;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }}
    </style>
</head>
<body>
    <h1>OCGN Stock Price Feed</h1>
    <p>This feed provides real-time OCGN stock price updates, including extended hours trading data.</p>
    
    <div class="feed-link">
        <h2>Atom Feed URL</h2>
        <p><code>{FEED_URL}</code></p>
        <p><a href="feed.atom">View Feed</a></p>
    </div>
    
    <h2>About</h2>
    <p>The feed is automatically updated every 15 minutes during market hours and extended trading hours.</p>
    <p>Stock data is fetched from Yahoo Finance using the yfinance Python library.</p>
    
    <h2>How to Use</h2>
    <p>Subscribe to the feed in your favorite RSS/Atom reader using the feed URL above.</p>
</body>
</html>
"""
    
    index_path = 'docs/index.html'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print(f"Index page generated: {index_path}")


if __name__ == '__main__':
    main()
