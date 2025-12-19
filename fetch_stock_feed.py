#!/usr/bin/env python3
"""
fetch_stock_feed.py

Updated to:
- Trading window BRT 04:00 - 21:00 (BRT)
- Full-window 5-minute entries = 204
- Atom and RSS timestamps remain in BRT
- Keep behavior: fetch 1m bars, resample to 5m, copy OCGN.png -> docs/

This script fetches recent 1-minute bars for OCGN, resamples to 5-minute bars,
builds simple RSS and Atom feeds with timestamps in BRT, and writes feed files
into docs/. It also copies OCGN.png into docs/.

Requires: yfinance, pandas, pytz
"""

import os
import shutil
from datetime import datetime, date, time, timedelta
import pytz
import pandas as pd
import yfinance as yf
from email.utils import format_datetime
import xml.etree.ElementTree as ET

# --- Configuration ---
SYMBOL = "OCGN"
BRT_TZ = pytz.timezone("America/Sao_Paulo")  # BRT (UTC-3)
TRADING_START = time(4, 0)   # 04:00 BRT
TRADING_END = time(21, 0)    # 21:00 BRT (changed per user request)
FULL_WINDOW_ENTRIES_5M = 204  # 17 hours * 60 / 5 = 204
ONE_MIN_FETCH_PERIOD = "2d"  # fetch last 2 days of 1m bars to be safe
DOCS_DIR = "docs"
PNG_SOURCE = "OCGN.png"
PNG_DEST = os.path.join(DOCS_DIR, "OCGN.png")
RSS_PATH = os.path.join(DOCS_DIR, "ocgn.rss")
ATOM_PATH = os.path.join(DOCS_DIR, "ocgn.atom")

# Ensure docs directory exists
os.makedirs(DOCS_DIR, exist_ok=True)


def fetch_1m_data(symbol: str) -> pd.DataFrame:
    """Fetch recent 1-minute bars and return a DataFrame with timezone-aware index in BRT."""
    # yfinance returns tz-aware index (UTC) for intraday; convert to BRT
    df = yf.download(symbol, period=ONE_MIN_FETCH_PERIOD, interval="1m", progress=False, threads=False)
    if df.empty:
        raise RuntimeError("No data returned from yfinance for symbol {}".format(symbol))

    # Ensure index is tz-aware UTC, then convert to BRT
    if df.index.tz is None:
        df.index = df.index.tz_localize(pytz.UTC)
    df = df.tz_convert(BRT_TZ)
    return df


def filter_trading_window(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only rows whose local time (BRT) falls within the configured trading window.
    This will keep data across multiple days but only times between TRADING_START and TRADING_END.
    """
    # between_time works on the index's time component
    df_in_window = df.between_time(TRADING_START.strftime("%H:%M"), TRADING_END.strftime("%H:%M"))
    return df_in_window


def resample_to_5m(df: pd.DataFrame) -> pd.DataFrame:
    """Resample 1m bars to 5m bars. The timestamp of a 5m bar will be the right edge (end) of the interval.
    Keep OHLC and sum volume.
    """
    ohlc = df[['Open', 'High', 'Low', 'Close']].resample('5T', label='right', closed='right').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'})
    volume = df['Volume'].resample('5T', label='right', closed='right').sum()
    res = ohlc.join(volume).dropna(subset=['Open'])
    res.index = res.index.tz_convert(BRT_TZ)  # ensure index stays in BRT
    return res


def build_rss(latest_bar: pd.Series, feed_time: datetime) -> str:
    """Build a simple RSS 2.0 feed string. Timestamps are kept in BRT.
    feed_time must be timezone-aware in BRT.
    """
    title = f"{SYMBOL} 5m feed"
    link = "https://github.com/cm-fy/ocgn-stock-feed"  # example link
    description = f"{SYMBOL} latest 5m close: {latest_bar['Close']:.4f}"

    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'title').text = title
    ET.SubElement(channel, 'link').text = link
    ET.SubElement(channel, 'description').text = description

    # Item
    item = ET.SubElement(channel, 'item')
    ET.SubElement(item, 'title').text = f"{SYMBOL} {latest_bar.name.isoformat()}"
    ET.SubElement(item, 'description').text = description
    ET.SubElement(item, 'link').text = link
    # pubDate in RFC 2822, keep BRT tz
    ET.SubElement(item, 'pubDate').text = format_datetime(feed_time)

    xml_str = ET.tostring(rss, encoding='utf-8')
    return xml_str.decode('utf-8')


def build_atom(latest_bar: pd.Series, feed_time: datetime) -> str:
    """Build a simple Atom feed string. Timestamps are kept in BRT (ISO 8601 with offset).
    feed_time must be timezone-aware in BRT.
    """
    ns = 'http://www.w3.org/2005/Atom'
    feed = ET.Element('feed', xmlns=ns)
    ET.SubElement(feed, 'title').text = f"{SYMBOL} 5m feed"
    ET.SubElement(feed, 'updated').text = feed_time.isoformat()
    ET.SubElement(feed, 'id').text = f"urn:uuid:{SYMBOL}-feed"

    entry = ET.SubElement(feed, 'entry')
    ET.SubElement(entry, 'title').text = f"{SYMBOL} {latest_bar.name.isoformat()}"
    ET.SubElement(entry, 'id').text = f"urn:uuid:{SYMBOL}-{latest_bar.name.isoformat()}"
    ET.SubElement(entry, 'updated').text = feed_time.isoformat()
    ET.SubElement(entry, 'summary').text = f"Latest close: {latest_bar['Close']:.4f}"

    xml_str = ET.tostring(feed, encoding='utf-8')
    return xml_str.decode('utf-8')


def main():
    try:
        df1m = fetch_1m_data(SYMBOL)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    df_window = filter_trading_window(df1m)
    if df_window.empty:
        print("No data found in trading window. Exiting.")
        return

    df_5m = resample_to_5m(df_window)
    if df_5m.empty:
        print("No 5m bars after resampling. Exiting.")
        return

    # Keep only the latest FULL_WINDOW_ENTRIES_5M bars (full trading-day window)
    df_5m = df_5m.tail(FULL_WINDOW_ENTRIES_5M)

    latest_bar = df_5m.iloc[-1]
    latest_time = df_5m.index[-1]
    # Ensure feed timestamps are in BRT
    feed_time = latest_time.astimezone(BRT_TZ)

    # Build feeds
    rss_xml = build_rss(latest_bar, feed_time)
    atom_xml = build_atom(latest_bar, feed_time)

    # Write feed files
    with open(RSS_PATH, 'w', encoding='utf-8') as f:
        f.write(rss_xml)
    with open(ATOM_PATH, 'w', encoding='utf-8') as f:
        f.write(atom_xml)

    # Also write a simple HTML summary (optional, helps quick debugging/viewing on GH Pages)
    summary_path = os.path.join(DOCS_DIR, 'index.html')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"<html><body><h1>{SYMBOL} 5m feed</h1>")
        f.write(f"<p>Latest time (BRT): {feed_time.isoformat()}</p>")
        f.write(f"<p>Latest close: {latest_bar['Close']:.4f}</p>")
        f.write("</body></html>")

    # Copy image to docs/
    if os.path.exists(PNG_SOURCE):
        try:
            shutil.copyfile(PNG_SOURCE, PNG_DEST)
        except Exception as e:
            print(f"Warning: could not copy {PNG_SOURCE} to {PNG_DEST}: {e}")
    else:
        print(f"Warning: {PNG_SOURCE} not found; skipping copy to docs/.")

    print(f"Wrote feeds: {RSS_PATH}, {ATOM_PATH}. Copied image to {PNG_DEST} (if present).")


if __name__ == '__main__':
    main()
