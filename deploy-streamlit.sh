#!/bin/bash
# Streamlit Cloud Deployment Script
# One-click deploy to Streamlit Cloud

set -e

echo "🚀 Bridge GAD Generator - Streamlit Cloud Deployment"
echo "====================================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "❌ Error: Not a git repository"
    echo "Run: git init && git add . && git commit -m 'initial'"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "📝 Uncommitted changes detected"
    echo "Committing changes..."
    git add .
    git commit -m "chore: update bridge gad - $(date +'%Y-%m-%d %H:%M:%S')"
    echo "✅ Changes committed"
fi

# Push to GitHub
echo ""
echo "📤 Pushing to GitHub..."
git push origin main
echo "✅ Pushed to GitHub"

echo ""
echo "✨ Deployment initiated!"
echo ""
echo "📍 Next steps:"
echo "1. Visit: https://streamlit.io/cloud"
echo "2. Click 'New app'"
echo "3. Select your repository"
echo "4. Select main branch"
echo "5. Set main file path: streamlit_app.py"
echo "6. Click Deploy!"
echo ""
echo "🎉 Your app will be live in ~2 minutes"
echo "URL: https://<username>-bridge-gad-<hash>.streamlit.app"
echo ""
