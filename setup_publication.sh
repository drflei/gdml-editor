#!/bin/bash
# One-command setup script for GDML Editor publication
# This script will guide you through the entire publication process

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

clear
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              GDML Editor Publication Setup                ║
║                      Version 1.0.0                        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo "This script will help you publish GDML Editor to GitHub and PyPI"
echo ""

# Step 1: Get GitHub username
echo -e "${YELLOW}Step 1: GitHub Username${NC}"
echo "What is your GitHub username?"
read -p "Username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo -e "${RED}Error: GitHub username is required${NC}"
    exit 1
fi

echo -e "${GREEN}✓ GitHub username: $GITHUB_USERNAME${NC}"
echo ""

# Step 2: Update documentation
echo -e "${YELLOW}Step 2: Updating Documentation${NC}"
echo "Updating all files with your GitHub username..."
./update_github_username.sh "$GITHUB_USERNAME"
echo -e "${GREEN}✓ Documentation updated${NC}"
echo ""

# Step 3: Verify setup
echo -e "${YELLOW}Step 3: Verifying Package Setup${NC}"
python verify_setup.py
echo ""

# Step 4: Initialize Git
echo -e "${YELLOW}Step 4: Git Initialization${NC}"
if [ -d ".git" ]; then
    echo "Git repository already exists"
    echo -e "${GREEN}✓ Git repository ready${NC}"
else
    echo "Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: GDML Editor v1.0.0

Features:
- User-defined materials with JSON persistence
- Element dropdown with 118 elements and autocomplete
- Material CRUD operations (Create, Read, Update, Delete)
- Integration with pyg4ometry NIST database
- Refactored architecture (40% code reduction)
- Professional packaging for PyPI
- CI/CD with GitHub Actions
- Comprehensive documentation"
    
    echo -e "${GREEN}✓ Git repository initialized${NC}"
fi
echo ""

# Step 5: Build package
echo -e "${YELLOW}Step 5: Building Package${NC}"
echo "Installing build tools..."
pip install --upgrade build twine > /dev/null 2>&1

echo "Cleaning old builds..."
rm -rf build/ dist/ *.egg-info 2>/dev/null || true

echo "Building package..."
python -m build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Package built successfully${NC}"
    echo ""
    echo "Built files:"
    ls -lh dist/
else
    echo -e "${RED}✗ Package build failed${NC}"
    exit 1
fi
echo ""

# Step 6: Check package
echo -e "${YELLOW}Step 6: Checking Package${NC}"
twine check dist/*
echo -e "${GREEN}✓ Package check passed${NC}"
echo ""

# Final instructions
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║                  Setup Complete! 🎉                       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Next Steps - Manual Actions Required:${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}1. CREATE GITHUB REPOSITORY${NC}"
echo "   Go to: https://github.com/new"
echo "   Repository name: gdml-editor"
echo "   Description: GUI for editing GDML geometry files"
echo "   Visibility: Public"
echo "   Do NOT initialize with README, .gitignore, or license"
echo "   Click 'Create repository'"
echo ""

echo -e "${YELLOW}2. PUSH TO GITHUB${NC}"
echo "   Run these commands:"
echo -e "   ${GREEN}git remote add origin https://github.com/$GITHUB_USERNAME/gdml-editor.git${NC}"
echo -e "   ${GREEN}git branch -M main${NC}"
echo -e "   ${GREEN}git push -u origin main${NC}"
echo ""

echo -e "${YELLOW}3. CREATE PYPI ACCOUNT (if you don't have one)${NC}"
echo "   Go to: https://pypi.org/account/register/"
echo "   Verify your email"
echo "   Enable 2FA (recommended)"
echo ""

echo -e "${YELLOW}4. TEST ON TEST PYPI (recommended)${NC}"
echo "   Go to: https://test.pypi.org/account/register/"
echo "   Create account and verify email"
echo "   Generate API token at: https://test.pypi.org/manage/account/token/"
echo "   Upload package:"
echo -e "   ${GREEN}twine upload --repository testpypi dist/*${NC}"
echo "   Test installation:"
echo -e "   ${GREEN}pip install -i https://test.pypi.org/simple/ gdml-editor${NC}"
echo ""

echo -e "${YELLOW}5. PUBLISH TO PYPI${NC}"
echo "   Generate API token at: https://pypi.org/manage/account/token/"
echo "   Upload package:"
echo -e "   ${GREEN}twine upload dist/*${NC}"
echo "   Username: __token__"
echo "   Password: (paste your API token)"
echo ""

echo -e "${YELLOW}6. VERIFY INSTALLATION${NC}"
echo "   In a fresh environment:"
echo -e "   ${GREEN}pip install gdml-editor${NC}"
echo -e "   ${GREEN}gdml-editor${NC}"
echo ""

echo -e "${YELLOW}7. CREATE GITHUB RELEASE${NC}"
echo "   Go to: https://github.com/$GITHUB_USERNAME/gdml-editor/releases/new"
echo "   Tag: v1.0.0"
echo "   Title: GDML Editor v1.0.0"
echo "   Description: (copy from CHANGELOG.md)"
echo "   Upload files from dist/ folder"
echo "   Click 'Publish release'"
echo ""

echo -e "${YELLOW}8. CONFIGURE AUTOMATED PUBLISHING${NC}"
echo "   Add PyPI token to GitHub secrets:"
echo "   Go to: https://github.com/$GITHUB_USERNAME/gdml-editor/settings/secrets/actions"
echo "   Click 'New repository secret'"
echo "   Name: PYPI_API_TOKEN"
echo "   Value: (your PyPI API token)"
echo "   Save"
echo ""

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Helpful Resources:${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "📚 Documentation:"
echo "   - PUBLICATION_CHECKLIST.md (detailed checklist)"
echo "   - QUICK_START.md (user guide)"
echo "   - PACKAGE_SUMMARY.md (overview)"
echo "   - CONTRIBUTING.md (contributor guidelines)"
echo ""
echo "🔧 Package Info:"
echo "   - Version: 1.0.0"
echo "   - Package name: gdml-editor"
echo "   - Command: gdml-editor"
echo "   - GitHub: https://github.com/$GITHUB_USERNAME/gdml-editor"
echo "   - PyPI: https://pypi.org/project/gdml-editor/"
echo ""
echo "📦 Built Files:"
echo "   - Source: dist/gdml-editor-1.0.0.tar.gz"
echo "   - Wheel: dist/gdml_editor-1.0.0-py3-none-any.whl"
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Setup complete! Ready to publish! 🚀${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Press any key to continue..."
read -n 1 -s
