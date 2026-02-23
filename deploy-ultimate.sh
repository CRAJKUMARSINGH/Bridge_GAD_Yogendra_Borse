#!/bin/bash

# Ultimate Bridge GAD Generator - Deployment Script
# Deploys the integrated application to Streamlit Cloud

echo "🚀 Ultimate Bridge GAD Generator - Deployment"
echo "=============================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit - Ultimate Bridge GAD Generator"
fi

# Check for uncommitted changes
if [[ `git status --porcelain` ]]; then
    echo "📝 Committing changes..."
    git add .
    git commit -m "Update: Ultimate integration complete"
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git branch -M main

# Check if remote exists
if git remote | grep -q "origin"; then
    echo "✅ Remote 'origin' exists"
    git push -u origin main
else
    echo "⚠️  No remote 'origin' found"
    echo "Please add your GitHub repository:"
    echo "git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo "git push -u origin main"
fi

echo ""
echo "✅ Deployment preparation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Go to https://streamlit.io/cloud"
echo "2. Click 'New app'"
echo "3. Connect your GitHub repository"
echo "4. Set main file: streamlit_app_ultimate.py"
echo "5. Click 'Deploy'"
echo ""
echo "🎉 Your app will be live in 2-3 minutes!"
echo ""
echo "📊 Features included:"
echo "   ✅ Bridge drawing generation"
echo "   ✅ Professional bill generation"
echo "   ✅ 10+ export formats"
echo "   ✅ Quality checking"
echo "   ✅ 3D visualization"
echo "   ✅ AI optimization"
echo "   ✅ Complete history tracking"
echo ""
echo "🌉 Ultimate Bridge GAD Generator - Ready for production!"
