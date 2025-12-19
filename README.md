# OCGN Stock Feed

An automated Atom feed for OCGN (Ocugen, Inc.) stock prices, updated every 15 minutes.

## 🌐 Live Feed

Subscribe to the feed: [https://cm-fy.github.io/ocgn-stock-feed/feed.atom](https://cm-fy.github.io/ocgn-stock-feed/feed.atom)

Visit the web page: [https://cm-fy.github.io/ocgn-stock-feed/](https://cm-fy.github.io/ocgn-stock-feed/)

## 📊 Features

- **Real-time Updates**: Automatically fetches OCGN stock data every 15 minutes
- **Extended Hours**: Includes pre-market and after-hours trading data
- **Comprehensive Data**: Open, High, Low, Close prices and trading volume
- **Atom Feed Format**: Compatible with all major feed readers
- **GitHub Pages Hosting**: Publicly accessible feed hosted on GitHub Pages

## 🔧 How It Works

1. **Data Fetching**: A Python script uses the `yfinance` library to fetch OCGN stock data including extended hours trading
2. **Feed Generation**: The script generates an Atom feed in XML format with the latest stock prices
3. **Automation**: GitHub Actions runs the script every 15 minutes on a schedule
4. **Publishing**: The updated feed is automatically committed to the repository
5. **Hosting**: GitHub Pages serves the feed at a public URL

## 📁 Repository Structure

```
.
├── fetch_stock_feed.py       # Python script to fetch data and generate feed
├── requirements.txt           # Python dependencies
├── feed.atom                  # Generated Atom feed (auto-updated)
├── index.html                 # Landing page for GitHub Pages
├── .github/workflows/
│   ├── update-feed.yml       # Workflow to update the feed every 15 minutes
│   └── pages.yml             # Workflow to deploy to GitHub Pages
└── README.md                  # This file
```

## 🚀 Setup Instructions

### ⚠️ CRITICAL: Enable GitHub Pages First

**The feed will NOT be accessible until you enable GitHub Pages in repository settings:**

1. Go to your repository on GitHub: `https://github.com/cm-fy/ocgn-stock-feed`
2. Click **Settings** (top menu)
3. Click **Pages** (left sidebar under "Code and automation")
4. Under "Build and deployment":
   - **Source**: Select **"GitHub Actions"** (NOT "Deploy from a branch")
5. Click **Save**
6. The feed will be live at `https://cm-fy.github.io/ocgn-stock-feed/feed.atom` within 1-2 minutes

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Local Testing

1. Clone the repository:
   ```bash
   git clone https://github.com/cm-fy/ocgn-stock-feed.git
   cd ocgn-stock-feed
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the script:
   ```bash
   python fetch_stock_feed.py
   ```

4. Check the generated `feed.atom` file

### Manual Trigger

After enabling GitHub Pages, you can manually trigger the feed update:
1. Go to Actions tab
2. Select "Update OCGN Stock Feed" workflow
3. Click "Run workflow"
4. Wait for it to complete (about 30 seconds)
5. The "Deploy GitHub Pages" workflow will automatically trigger
6. Your feed will be live at `https://cm-fy.github.io/ocgn-stock-feed/feed.atom`

## 📡 Using the Feed

### In Feed Readers

Copy this URL into your favorite RSS/Atom reader:
```
https://cm-fy.github.io/ocgn-stock-feed/feed.atom
```

### Supported Feed Readers

- Feedly
- Inoreader
- NewsBlur
- RSS readers in email clients (Thunderbird, Outlook)
- Browser extensions
- Any Atom-compatible feed reader

## 🛠️ Technologies Used

- **Python**: Core scripting language
- **yfinance**: Python library for fetching Yahoo Finance data
- **GitHub Actions**: Automation and scheduling
- **GitHub Pages**: Static site hosting
- **Atom/XML**: Feed format

## ⚠️ Disclaimer

This feed provides stock market data for informational purposes only. It is not financial advice. The data is provided by Yahoo Finance through the yfinance library. Always conduct your own research and consult with financial advisors before making investment decisions.

## 📝 License

This project is open source and available for use.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📧 Contact

For questions or issues, please open an issue on GitHub.
