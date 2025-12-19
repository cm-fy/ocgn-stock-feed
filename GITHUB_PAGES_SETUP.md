# GitHub Pages Setup Instructions

This document provides instructions for enabling GitHub Pages to host the OCGN stock feed.

## Enabling GitHub Pages

To make the Atom feed publicly accessible, you need to enable GitHub Pages for this repository:

### Steps:

1. **Go to Repository Settings**
   - Navigate to your repository on GitHub
   - Click on "Settings" in the top menu

2. **Navigate to Pages Settings**
   - In the left sidebar, click on "Pages" (under "Code and automation")

3. **Configure Source**
   - Under "Build and deployment"
   - **Source**: Select "GitHub Actions" (not "Deploy from a branch")
   - This allows the workflow to deploy directly to GitHub Pages

4. **Save Configuration**
   - The settings should save automatically
   - GitHub Pages will be enabled and ready to receive deployments from the workflow

## Verification

After enabling GitHub Pages and the workflow runs successfully:

1. The feed will be available at: `https://cm-fy.github.io/ocgn-stock-feed/feed.atom`
2. The web interface will be at: `https://cm-fy.github.io/ocgn-stock-feed/`

## Workflow Behavior

- The workflow runs every 15 minutes automatically
- It can also be triggered manually from the Actions tab
- On the first run (or when pushing to main/master), it will:
  1. Fetch OCGN stock data
  2. Generate the Atom feed
  3. Commit the feed to the repository
  4. Deploy to GitHub Pages

## Troubleshooting

### If the feed is not accessible:

1. Check that GitHub Pages is enabled in Settings > Pages
2. Verify the source is set to "GitHub Actions"
3. Check the Actions tab to see if workflows are running successfully
4. Ensure the repository has the required permissions:
   - `contents: write` (to commit feed updates)
   - `pages: write` (to deploy to Pages)
   - `id-token: write` (for GitHub Pages authentication)

### If the workflow fails:

1. Check the Actions tab for error logs
2. Verify that the yfinance API is accessible (Yahoo Finance might have rate limits)
3. The script is designed to handle errors gracefully and will generate a placeholder feed if data is unavailable

## Feed Update Schedule

The cron expression `*/15 * * * *` means:
- Runs every 15 minutes
- 24/7, every day
- Approximately 96 times per day

This ensures near real-time updates including during:
- Pre-market hours (4:00 AM - 9:30 AM ET)
- Regular market hours (9:30 AM - 4:00 PM ET)
- After-hours trading (4:00 PM - 8:00 PM ET)

## Notes

- The first deployment may take a few minutes to become available
- Subsequent updates are typically faster
- The feed includes extended hours trading data when available
- All timestamps are in UTC
