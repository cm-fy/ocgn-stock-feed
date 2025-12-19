# 🚀 SETUP GUIDE - Make Your Feed Live in 2 Minutes

## Step 1: Enable GitHub Pages (REQUIRED)

GitHub Pages is **disabled by default**. You MUST enable it manually:

### Visual Guide:

1. **Go to your repository**: https://github.com/cm-fy/ocgn-stock-feed

2. **Click "Settings"** at the top of the page
   - Look for the gear icon ⚙️ in the top navigation bar

3. **Click "Pages"** in the left sidebar
   - It's under the "Code and automation" section
   - Look for 📄 Pages icon

4. **Configure Build and Deployment**:
   - Find the "Source" dropdown
   - **SELECT "GitHub Actions"** (this is critical!)
   - Do NOT select "Deploy from a branch"

5. **Save your changes**

6. **Wait 30-60 seconds** for GitHub to process

## Step 2: Trigger the Workflow (Optional but Recommended)

Once GitHub Pages is enabled:

1. Go to the **Actions** tab
2. Click **"Update OCGN Stock Feed"** on the left
3. Click **"Run workflow"** button (top right)
4. Click the green **"Run workflow"** button in the dropdown
5. Wait about 30 seconds for it to complete

## Step 3: Verify It's Live

Your feed should now be accessible at:
**https://cm-fy.github.io/ocgn-stock-feed/feed.atom**

Landing page:
**https://cm-fy.github.io/ocgn-stock-feed/**

## Troubleshooting

### "404 - Page not found"
- Did you enable GitHub Pages in Settings → Pages?
- Did you select "GitHub Actions" as the source (not "Deploy from a branch")?
- Wait a few more minutes - initial deployment can take 2-3 minutes

### Workflow fails with "Resource not accessible by integration"
- The workflows need permission to deploy
- Go to Settings → Actions → General
- Under "Workflow permissions", select "Read and write permissions"
- Click Save

### Feed shows placeholder data
- Run the "Update OCGN Stock Feed" workflow manually (see Step 2)
- The scheduled runs happen every 15 minutes automatically

## What Happens After Setup?

1. ✅ Feed updates automatically every 15 minutes
2. ✅ Includes extended hours trading data
3. ✅ No maintenance required
4. ✅ Always accessible at the same URL

## Still Having Issues?

Check the Actions tab to see if workflows are running successfully. Any errors will be shown there with details.
