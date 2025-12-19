# OCGN Stock Feed

This repository automatically fetches and publishes OCGN (Ocugen Inc.) stock price data as an Atom feed, updated every 15 minutes.

## 🔗 Feed URL

The Atom feed is publicly accessible at:
- **Feed URL**: [https://cm-fy.github.io/ocgn-stock-feed/feed.atom](https://cm-fy.github.io/ocgn-stock-feed/feed.atom)
- **Web Interface**: [https://cm-fy.github.io/ocgn-stock-feed/](https://cm-fy.github.io/ocgn-stock-feed/)

## 📊 Features

- **Real-time Updates**: Fetches stock prices every 15 minutes
- **Extended Hours**: Includes pre-market and after-hours trading data
- **Atom Feed Format**: Standard feed format compatible with all RSS/Atom readers
- **Automatic Publishing**: Uses GitHub Actions to automatically update and publish
- **GitHub Pages Hosting**: Publicly accessible feed hosted on GitHub Pages

## 🚀 How It Works

1. **GitHub Actions Workflow**: A scheduled workflow runs every 15 minutes
2. **Data Fetching**: The Python script uses yfinance to fetch OCGN stock data including extended hours
3. **Feed Generation**: Stock data is formatted into an Atom feed (XML)
4. **Auto-Commit**: Updated feed is committed to the repository
5. **GitHub Pages**: The feed is automatically deployed to GitHub Pages

## 📝 Feed Contents

Each feed entry includes:
- Current stock price
- Previous close
- Price change and percentage
- Market state (PRE, REGULAR, POST, CLOSED)
- Latest trading data (Open, High, Low, Close, Volume)
- Extended hours information
- Timestamp

## 🛠️ Technical Details

### Technologies Used
- **Python 3.11**: For data fetching and feed generation
- **yfinance**: Yahoo Finance API wrapper for stock data
- **GitHub Actions**: Automated workflow execution
- **GitHub Pages**: Static site hosting

### Files
- `fetch_stock_feed.py`: Python script that fetches data and generates the feed
- `.github/workflows/update-feed.yml`: GitHub Actions workflow configuration
- `requirements.txt`: Python dependencies
- `docs/feed.atom`: Generated Atom feed
- `docs/index.html`: Web interface for the feed

## 📖 Usage

### Subscribe to the Feed

Add the feed URL to your favorite RSS/Atom reader:
```
https://cm-fy.github.io/ocgn-stock-feed/feed.atom
```

### Manual Trigger

You can manually trigger the workflow from the Actions tab in GitHub.

### Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the script
python fetch_stock_feed.py
```

## ⚙️ Configuration

The workflow runs on the following schedule:
- **Frequency**: Every 15 minutes
- **Cron Expression**: `*/15 * * * *`

To modify the schedule, edit the cron expression in `.github/workflows/update-feed.yml`.

## 📄 License

This project is open source and available for public use.

## ⚠️ Disclaimer

This feed provides stock price information for informational purposes only. It should not be considered as financial advice. Always consult with a qualified financial advisor before making investment decisions.

Stock data is sourced from Yahoo Finance via the yfinance library.
