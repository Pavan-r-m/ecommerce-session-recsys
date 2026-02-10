#!/bin/bash
# Initialize Git Repository and Push to GitHub
# Run this script to set up your new repository

set -e

echo "===================================="
echo "Git Repository Setup"
echo "===================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Error: git is not installed"
    exit 1
fi

# Initialize git repository (if not already)
if [ ! -d ".git" ]; then
    echo ""
    echo "Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo ""
    echo "Git repository already initialized"
fi

# Add all files
echo ""
echo "Staging files..."
git add .

# Check if there are changes to commit
if git diff-index --quiet HEAD --; then
    echo "No changes to commit"
else
    echo ""
    echo "Creating initial commit..."
    git commit -m "feat: Initial commit - Session-based recommender system

- FastAPI REST API with event tracking and recommendations
- Redis-backed session state management
- LightGBM ranking model for candidate scoring
- Item-to-item collaborative filtering
- Docker & docker-compose configuration
- Comprehensive test suite
- CI/CD pipeline with GitHub Actions
- Full training pipeline and evaluation metrics
- Deployment guides for Render, Fly.io, and AWS"
    
    echo "✅ Initial commit created"
fi

echo ""
echo "===================================="
echo "Next Steps:"
echo "===================================="
echo ""
echo "1. Create a new repository on GitHub:"
echo "   - Go to https://github.com/new"
echo "   - Name: ecommerce-session-recsys"
echo "   - Description: Production-ready session-based recommender system"
echo "   - Make it Public (for portfolio)"
echo "   - DON'T initialize with README (we already have one)"
echo ""
echo "2. Add the remote and push:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/ecommerce-session-recsys.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. (Optional) Replace README.md with README_RECSYS.md:"
echo "   mv README_RECSYS.md README.md"
echo "   git add README.md"
echo "   git commit -m 'docs: Update README for recommender system'"
echo "   git push"
echo ""
echo "4. Update README with your GitHub username:"
echo "   - Replace YOUR_USERNAME with your actual GitHub username"
echo "   - Replace YOUR_PROFILE with your LinkedIn profile ID"
echo ""
echo "===================================="
