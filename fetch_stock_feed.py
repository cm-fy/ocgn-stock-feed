#!/usr/bin/env python3
"""
Fetch OCGN stock data and generate an Atom feed (docs/feed.atom) and index page.
This version fetches 1m history, resamples to 5m, builds a full ET trading-window (04:00-20:00 ET) with 192 entries
and copies OCGN.png into docs/ so GitHub Pages serves it.
"""
import os
import shutil
import datetime as dt
from zoneinfo import ZoneInfo
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

# How many entries to include across the full 04:00-20:00 ET window at 5-minute cadence
ENTRIES_IN_FULL_WINDOW = 192  # 16 hours * 12 samples/hour

ATOM_NS = "http://www.w3.org/2005/Atom"
ET.register_namespace('', ATOM_NS)

ET_TZ = ZoneInfo('UTC')
LOCAL_TZ = ZoneInfo('America/New_York')


def fetch_ocgn_data():
    """Return info dict and recent history DataFrame for OCGN using yfinance (1m resolution)."""
    try:
        t = yf.Ticker(SYMBOL)
        info = t.info if hasattr(t, 'info') else {}
        # Get last 2 days with 1m resolution including pre/post market
        hist = t.history(period="2d", interval="1m", prepost=True)
        return info, hist
    except Exception as e:
        print(f"Error fetching data: {e}")
        return {}, pd.DataFrame()


def build_full_window_index(date_et: dt.date):
    """Return a DatetimeIndex in ET for the full 04:00-20:00 window at 5-minute cadence for the given date."""
    start = dt.datetime.combine(date_et, dt.time(4, 0), tzinfo=LOCAL_TZ)
    end = dt.datetime.combine(date_et, dt.time(20, 0), tzinfo=LOCAL_TZ)
    return pd.date_range(start=start, end=end, freq='5T')


def generate_atom_feed(info, hist):
    """Build an ElementTree Element for the Atom feed including icon/logo and full-window entries."""
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
    updated.text = dt.datetime.utcnow().replace(tzinfo=ET_TZ).isoformat()

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
    logo_el.text = FEED_ICON

    # Prepare history: ensure tz-aware index and resample to 5-minute buckets
    df = hist.copy()
    if not df.empty:
        # Make sure index has tzinfo; yfinance often returns tz-aware index
        if df.index.tz is None:
            # assume UTC if no tz provided
            df = df.tz_localize('UTC')
        # Convert to ET local time for windowing
        df = df.tz_convert(LOCAL_TZ)

        # Use the Close column if present
        if 'Close' in df.columns:
            price_series = df['Close']
        elif 'close' in df.columns:
            price_series = df['close']
        else:
            # try to find a close-like column
            price_series = df.iloc[:, 0]

        # Resample to 5-minute using last available observation in each bucket
        price_5m = price_series.resample('5T').last()
        # Forward-fill small gaps so the full window has values where possible
        price_5m = price_5m.ffill()
    else:
        price_5m = pd.Series(dtype=float)

    # Determine target date in ET to build the full window
    now_et = dt.datetime.now(LOCAL_TZ)
    target_date = now_et.date()

    full_index = build_full_window_index(target_date)

    # Reindex price_5m to the full window (index in ET), keeping UTC-aware index for outputs
    if not price_5m.empty:
        # price_5m index is ET tz-aware; reindex
        price_5m = price_5m.reindex(full_index, method='ffill')
    else:
        # create empty series indexed by full_index
        price_5m = pd.Series([None] * len(full_index), index=full_index)

    # For previous close, attempt to find last close prior to start of window
    previous_close = None
    try:
        if not hist.empty and 'Close' in hist.columns:
            # Use hist in UTC, convert to ET for comparison
            hist_utc = hist.copy()
            if hist_utc.index.tz is None:
                hist_utc = hist_utc.tz_localize('UTC')
            hist_et = hist_utc.tz_convert(LOCAL_TZ)
            # find last close before 04:00 ET of target_date
            start_et = dt.datetime.combine(target_date, dt.time(4, 0), tzinfo=LOCAL_TZ)
            prev_vals = hist_et[hist_et.index < start_et]
            if not prev_vals.empty and 'Close' in prev_vals.columns:
                previous_close = prev_vals['Close'].iloc[-1]
    except Exception:
        previous_close = None

    # Build entries for each timestamp in full_index (most recent first per Atom convention)
    for ts in reversed(full_index):
        price = price_5m.get(ts, None)
        # Compose entry
        entry = ET.SubElement(feed, ET.QName(ATOM_NS, 'entry'))

        title_entry = ET.SubElement(entry, ET.QName(ATOM_NS, 'title'))
        price_text = f"{SYMBOL}: ${price:.2f}" if price is not None and not pd.isna(price) else f"{SYMBOL}: N/A"
        title_entry.text = price_text

        link = ET.SubElement(entry, ET.QName(ATOM_NS, 'link'))
        link.set('href', f"https://finance.yahoo.com/quote/{SYMBOL}")
        link.set('rel', 'alternate')
        link.set('type', 'text/html')

        entry_id = ET.SubElement(entry, ET.QName(ATOM_NS, 'id'))
        entry_id.text = f"ocgn-{ts.strftime('%Y%m%d-%H%M')}-{SYMBOL.lower()}"

        # published and updated timestamps in UTC
        ts_utc = ts.astimezone(ET_TZ)
        published = ET.SubElement(entry, ET.QName(ATOM_NS, 'published'))
        published.text = ts_utc.isoformat()

        entry_updated = ET.SubElement(entry, ET.QName(ATOM_NS, 'updated'))
        entry_updated.text = ts_utc.isoformat()

        # Entry author
        entry_author = ET.SubElement(entry, ET.QName(ATOM_NS, 'author'))
        entry_author_name = ET.SubElement(entry_author, ET.QName(ATOM_NS, 'name'))
        entry_author_name.text = FEED_AUTHOR

        # Entry summary
        summary = ET.SubElement(entry, ET.QName(ATOM_NS, 'summary'))
        if price is not None and not pd.isna(price):
            if previous_close is not None:
                change = price - previous_close
                pct = (change / previous_close * 100) if previous_close else 0
                summary.text = f"{SYMBOL} {price:.2f} ({change:+.2f}, {pct:+.2f}%) at {ts.strftime('%H:%M %Z')}."
            else:
                summary.text = f"{SYMBOL} {price:.2f} at {ts.strftime('%H:%M %Z')}"
        else:
            summary.text = f"{SYMBOL} price unavailable at {ts.strftime('%H:%M %Z')}"

        content = ET.SubElement(entry, ET.QName(ATOM_NS, 'content'))
        content.set('type', 'html')
        content_html = "<div>\n"
        content_html += f"<h2>{SYMBOL} Stock Price Update</h2>\n"
        if price is not None and not pd.isna(price):
            content_html += f"<p><strong>Price:</strong> ${price:.2f}</p>\n"
        else:
            content_html += f"<p><strong>Price:</strong> N/A</p>\n"
        if previous_close is not None:
            content_html += f"<p><strong>Previous Close:</strong> ${previous_close:.2f}</p>\n"
        content_html += f"<p><strong>Timestamp (ET):</strong> {ts.strftime('%Y-%m-%d %H:%M %Z')}</p>\n"
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
            print(f"Note: {src} not found in repo root; skipping copy. If you want an icon, add OCGN.png at repo root or put the image in docs/.")
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
