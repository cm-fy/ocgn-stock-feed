#!/usr/bin/env python3
"""
Fetch OCGN stock data including extended hours and generate an Atom feed.
"""

import yfinance as yf
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
import os


def fetch_ocgn_data():
    """Fetch OCGN stock data including extended hours."""
    ticker = yf.Ticker("OCGN")
    
    # Get historical data for the last 5 days including pre/post market
    hist = ticker.history(period="5d", prepost=True)
    
    # Get current info
    info = ticker.info
    
    return hist, info


def generate_atom_feed(hist, info):
    """Generate an Atom feed from stock data."""
    # Create root element
    feed = ET.Element('feed', xmlns="http://www.w3.org/2005/Atom")
    
    # Add feed metadata
    title = ET.SubElement(feed, 'title')
    title.text = 'OCGN Stock Feed'
    
    link = ET.SubElement(feed, 'link', href='https://cm-fy.github.io/ocgn-stock-feed/feed.atom', rel='self')
    
    feed_id = ET.SubElement(feed, 'id')
    feed_id.text = 'https://cm-fy.github.io/ocgn-stock-feed/'
    
    updated = ET.SubElement(feed, 'updated')
    updated.text = datetime.now(timezone.utc).isoformat()
    
    author = ET.SubElement(feed, 'author')
    name = ET.SubElement(author, 'name')
    name.text = 'OCGN Stock Feed Bot'
    
    # Add entries for each data point (most recent first)
    for idx, (timestamp, row) in enumerate(hist.iterrows()):
        if idx >= 20:  # Limit to 20 most recent entries
            break
            
        entry = ET.SubElement(feed, 'entry')
        
        entry_title = ET.SubElement(entry, 'title')
        entry_title.text = f"OCGN: ${row['Close']:.2f}"
        
        entry_link = ET.SubElement(entry, 'link', href=f'https://finance.yahoo.com/quote/OCGN')
        
        entry_id = ET.SubElement(entry, 'id')
        entry_id.text = f"https://cm-fy.github.io/ocgn-stock-feed/{timestamp.isoformat()}"
        
        entry_updated = ET.SubElement(entry, 'updated')
        entry_updated.text = timestamp.isoformat()
        
        # Summary with stock details
        summary = ET.SubElement(entry, 'summary', type='html')
        summary_text = f"""
        <![CDATA[
        <h3>OCGN Stock Data</h3>
        <p><strong>Time:</strong> {timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')}</p>
        <p><strong>Open:</strong> ${row['Open']:.2f}</p>
        <p><strong>High:</strong> ${row['High']:.2f}</p>
        <p><strong>Low:</strong> ${row['Low']:.2f}</p>
        <p><strong>Close:</strong> ${row['Close']:.2f}</p>
        <p><strong>Volume:</strong> {int(row['Volume']):,}</p>
        ]]>
        """
        summary.text = summary_text.strip()
    
    return feed


def save_feed(feed, filename='feed.atom'):
    """Save the Atom feed to a file."""
    tree = ET.ElementTree(feed)
    ET.indent(tree, space='  ')
    tree.write(filename, encoding='utf-8', xml_declaration=True)
    print(f"Feed saved to {filename}")


def main():
    """Main function to fetch data and generate feed."""
    try:
        print("Fetching OCGN stock data...")
        hist, info = fetch_ocgn_data()
        
        if hist.empty:
            print("Warning: No historical data available")
            return
        
        print(f"Fetched {len(hist)} data points")
        print(f"Latest close: ${hist['Close'].iloc[-1]:.2f}")
        
        print("Generating Atom feed...")
        feed = generate_atom_feed(hist, info)
        
        print("Saving feed...")
        save_feed(feed)
        
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
