#!/bin/bash

# ============================================
# GITHUB SETUP SCRIPT
# FreeFire Level Up Bot - GitHub & Railway Setup
# ============================================

echo "=========================================="
echo "GITHUB SETUP SCRIPT"
echo "FreeFire Level Up Bot Setup"
echo "=========================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "ERROR: Git is not installed"
    echo "Please install Git from https://git-scm.com/download/win"
    exit 1
fi

echo "Git is installed!"
echo ""

# Ask for GitHub username
read -p "Enter your GitHub username: " github_username

if [ -z "$github_username" ]; then
    echo "ERROR: GitHub username is required"
    exit 1
fi

echo ""
echo "Setting up Git repository..."
echo ""

# Initialize git
git init
echo "✓ Git initialized"

# Add all files
git add .
echo "✓ Files staged"

# Commit
git commit -m "Initial commit - FreeFire Level Up Bot"
echo "✓ Files committed"

# Add remote
git remote add origin "https://github.com/${github_username}/toxic-bot.git"
echo "✓ Remote added"

# Rename branch to main
git branch -M main
echo "✓ Branch renamed to main"

echo ""
echo "=========================================="
echo "SETUP COMPLETED!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Create a new repository on GitHub:"
echo "   https://github.com/new"
echo "   - Name: toxic-bot"
echo "   - Make it PRIVATE"
echo ""
echo "2. Push to GitHub:"
echo "   git push -u origin main"
echo ""
echo "3. Go to Railway.app and deploy:"
echo "   https://railway.app/new"
echo "   - Select your toxic-bot repository"
echo "   - Click Deploy"
echo ""
echo "Note: You may need to authenticate with GitHub first:"
echo "   git config --global user.name 'Your Name'"
echo "   git config --global user.email 'your@email.com'"
echo ""
