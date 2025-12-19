#!/usr/bin/env python3
"""
Fetch OCGN stock data and generate an Atom feed (docs/feed.atom) and index page.
This version adds <icon> and <logo> elements to the Atom feed so readers can show an icon.
It will also copy an existing repository OCGN.png into docs/ so GitHub Pages serves it.
The feed includes extra metadata (subtitle, generator, alternate link) and entry-level author/summary
so it behaves more like a conventional feed.
"""
import os
import shutil
import datetime as dt
import xml.etree.ElementTree as ET
from xml.dom import minidom

import yfinance as yf
import pandas as pd

# Configuration
FEED_URL = "https://cm-fy.github.io/ocgn-stock-feed/feed.atom"
# Public URL for the icon (served from docs/ after the script copies the image)
FEED_ICON = "https://cm-fy.github.io/ocgn-stock-feed/OCGN.png"
FEED_HOMEPAGE = "https://cm-fy.github.io/ocgn-stock-feed/"
FEED_TITLE = "OCGN Stock Price Feed"
FEED_SUBTITLE = "Near-real-time OCGN (Ocugen Inc.) stock price updates (including extended hours)."
FEED_AUTHOR = "OCGN Stock Feed Bot"
SYMBOL = "OCGN"

ATOM_NS = "http://www.w3.org/2005/Atom"
ET.register_namespace('', ATOM_NS)


def fetch_ocgn_data():
    """Return info dict and recent history DataFrame for OCGN using yfinance."""
    try:
        t = yf.Ticker(SYMBOL)
        info = t.info if hasattr(t, 'info') else {}
        # Get last 2 days with 1m resolution if possible
        hist = t.history(period="2d", interval="1m", prepost=True)
        return info, hist
    except Exception as e:
        print(f"Error fetching data: {e}")
        return {}, pd.DataFrame()


def generate_atom_feed(info, hist):
    """Build an ElementTree Element for the Atom feed including icon/logo and extra metadata."""
    feed = ET.Element(ET.QName(ATOM_NS, 'feed'))

    # Basic feed metadata
    title = ET.SubElement(feed, ET.QName(ATOM_NS, 'title'))
    title.text = FEED_TITLE

    subtitle = ET.SubElement(feed, ET.QName(ATOM_NS, 'subtitle'))
    subtitle.text = FEED_SUBTITLE

    link_self = ET.SubElement(feed, ET.QName(ATOM_NS, 'link'))
    link_self.set('href', FEED_URL)
    link_self.set('rel', 'self')

    # Alternate link pointing to human-readable site
    link_alt = ET.SubElement(feed, ET.QName(ATOM_NS, 'link'))
    link_alt.set('href', FEED_HOMEPAGE)
    link_alt.set('rel', 'alternate')
    link_alt.set('type', 'text/html')

    feed_id = ET.SubElement(feed, ET.QName(ATOM_NS, 'id'))
    feed_id.text = FEED_URL

    updated = ET.SubElement(feed, ET.QName(ATOM_NS, 'updated'))
    updated.text = dt.datetime.utcnow().isoformat() + "Z"

    author = ET.SubElement(feed, ET.QName(ATOM_NS, 'author'))
    name = ET.SubElement(author, ET.QName(ATOM_NS, 'name'))
    name.text = FEED_AUTHOR

    # Generator element
    generator = ET.SubElement(feed, ET.QName(ATOM_NS, 'generator'))
    generator.text = 'fetch_stock_feed.py (custom)'

    # Add icon and logo elements so readers can show a feed image
    icon_el = ET.SubElement(feed, ET.QName(ATOM_NS, 'icon'))
    icon_el.text = FEED_ICON

    logo_el = ET.SubElement(feed, ET.QName(ATOM_NS, 'logo'))
    logo_el.text = FEED_ICON  # some clients prefer logo

    # Create an entry with latest data
    entry = ET.SubElement(feed, ET.QName(ATOM_NS, 'entry'))

    # Extract latest price info from history if available
    latest_price = None
    previous_close = None
    market_state = "UNKNOWN"
    latest_ts = dt.datetime.utcnow()

    if not hist.empty:
        try:
            latest_row = hist.iloc[-1]
            latest_price = latest_row.get('Close') if 'Close' in latest_row else latest_row.get('close', None)
            # previous close: last market close value (rough approach)
            if 'Close' in hist and len(hist) > 1:
                previous_close = hist['Close'].ffill().iloc[-2]
            latest_ts = latest_row.name.tz_convert(None) if hasattr(latest_row.name, 'tzinfo') else latest_row.name
            market_state = info.get('marketState', 'UNKNOWN') if isinstance(info, dict) else 'UNKNOWN'
        except Exception as e:
            print(f"Warning extracting latest data: {e}")

    # Entry elements
    title_entry = ET.SubElement(entry, ET.QName(ATOM_NS, 'title'))
    price_text = f"{SYMBOL}: ${latest_price:.2f}" if latest_price is not None else f"{SYMBOL}: N/A"
    title_entry.text = price_text

    link = ET.SubElement(entry, ET.QName(ATOM_NS, 'link'))
    link.set('href', f"https://finance.yahoo.com/quote/{SYMBOL}")
    link.set('rel', 'alternate')
    link.set('type', 'text/html')

    entry_id = ET.SubElement(entry, ET.QName(ATOM_NS, 'id'))
    entry_id.text = f"ocgn-{dt.datetime.utcnow().isoformat()}Z"

    entry_updated = ET.SubElement(entry, ET.QName(ATOM_NS, 'updated'))
    entry_updated.text = dt.datetime.utcnow().isoformat() + "Z"

    # Entry author
    entry_author = ET.SubElement(entry, ET.QName(ATOM_NS, 'author'))
    entry_author_name = ET.SubElement(entry_author, ET.QName(ATOM_NS, 'name'))
    entry_author_name.text = FEED_AUTHOR

    # Entry summary (short plain-text summary for compatibility)
    summary = ET.SubElement(entry, ET.QName(ATOM_NS, 'summary'))
    summary.text = f"{SYMBOL} price update: {price_text} (state: {market_state})"

    content = ET.SubElement(entry, ET.QName(ATOM_NS, 'content'))
    content.set('type', 'html')

    # Build HTML content
    content_html = "<div>\n"
    content_html += f"<h2>{SYMBOL} Stock Price Update</h2>\n"
    if latest_price is not None:
        content_html += f"<p><strong>Current Price:</strong> ${latest_price:.2f}</p>\n"
    if previous_close is not None:
        content_html += f"<p><strong>Previous Close:</strong> ${previous_close:.2f}</p>\n"
    content_html += f"<p><strong>Market State:</strong> {market_state}</p>\n"
    content_html += f"<p><strong>Last Updated:</strong> {latest_ts}</p>\n"
    content_html += "</div>"
    content.text = content_html

    return feed


def prettify_xml(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')


def ensure_icon_is_deployed():
    """If OCGN.png exists at repo root, copy it into docs/ so Pages serves it."""
    src = 'OCGN.png'
    dst_dir = 'docs'
    dst = os.path.join(dst_dir, 'OCGN.png')
    try:
        if os.path.exists(src):
            os.makedirs(dst_dir, exist_ok=True)
            shutil.copyfile(src, dst)
            print(f"Copied {src} -> {dst} so it will be deployed to Pages")
        else:
            print(f"Note: {src} not found in repo root; skipping copy. If you want an icon, add OCGN.png at repo root or put the image in docs_.")
    except Exception as e:
        print(f"Warning: could not copy icon file: {e}")


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

    # Ensure icon is deployed by copying the repo-root OCGN.png into docs/
    ensure_icon_is_deployed()

    output_path = 'docs/feed.atom'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(feed_xml)

    print(f"Feed generated successfully: {output_path}")

    # Also create an index.html for GitHub Pages
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>{FEED_TITLE}</title>
    <link rel="icon" type="image/png" href="OCGN.png" />
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; line-height: 1.6; }}
        h1 {{ color: #333; }}
        .feed-link {{ background-color: #f4f4f4; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        code {{ background-color: #e8e8e8; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
    </style>
</head>
<body>
    <h1>{FEED_TITLE}</h1>
    <p>{FEED_SUBTITLE}</p>

    <div class="feed-link">
        <h2>Atom Feed URL</h2>
        <p><code>{FEED_URL}</code></p>
        <p><a href="feed.atom">View Feed</a></p>
    </div>

    <h2>About</h2>
    <p>The feed is automatically updated on a schedule and includes extended hours trading data when available.</p>
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
