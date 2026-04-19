#!/bin/bash
# Push PathoScan to GitHub

echo "PathoScan GitHub Setup Instructions"
echo "===================================="
echo ""
echo "1. Create a new repository on GitHub at: https://github.com/new"
echo "   - Repository name: pathoscan"
echo "   - Description: Offline AI skin lesion triage system"
echo "   - Do NOT initialize with README, .gitignore, or license"
echo ""
echo "2. Run these commands to push your code:"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/pathoscan.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Your repository will be live at:"
echo "   https://github.com/YOUR_USERNAME/pathoscan"
echo ""
echo "To automate:"
read -p "Enter your GitHub username: " github_user
read -p "Enter your GitHub personal access token: " github_token

git remote add origin "https://$github_user:$github_token@github.com/$github_user/pathoscan.git"
git branch -M main
git push -u origin main

echo "✓ Repository pushed successfully!"
echo "View at: https://github.com/$github_user/pathoscan"
