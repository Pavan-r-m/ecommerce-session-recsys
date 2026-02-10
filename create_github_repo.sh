#!/bin/bash
# Create GitHub repository using GitHub CLI
# Make sure you have gh CLI installed and authenticated

set -e

REPO_NAME="ecommerce-session-recsys"
REPO_DESCRIPTION="Production-ready session-based recommender system with FastAPI, Redis, and LightGBM"

echo "===================================="
echo "Creating GitHub Repository"
echo "===================================="
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) is not installed."
    echo ""
    echo "Option 1: Install GitHub CLI"
    echo "  brew install gh"
    echo ""
    echo "Option 2: Create repository manually"
    echo "  1. Go to https://github.com/new"
    echo "  2. Repository name: $REPO_NAME"
    echo "  3. Description: $REPO_DESCRIPTION"
    echo "  4. Make it Public"
    echo "  5. DON'T initialize with README"
    echo ""
    echo "Then run these commands:"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/$REPO_NAME.git"
    echo "  git branch -M main"
    echo "  git push -u origin main"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "Not authenticated with GitHub CLI"
    echo "Run: gh auth login"
    exit 1
fi

echo "Creating repository: $REPO_NAME"
echo ""

# Create repository
gh repo create "$REPO_NAME" \
    --public \
    --description "$REPO_DESCRIPTION" \
    --source=. \
    --remote=origin

echo ""
echo "✅ Repository created successfully!"
echo ""
echo "Pushing code to GitHub..."

# Push to GitHub
git branch -M main
git push -u origin main

echo ""
echo "===================================="
echo "✅ Done!"
echo "===================================="
echo ""
echo "Your repository is live at:"
gh repo view --web

echo ""
echo "Next steps:"
echo "  1. Update README.md with your GitHub username"
echo "  2. Add topics/tags to your repo for discoverability"
echo "  3. Consider enabling GitHub Pages for documentation"
echo ""
