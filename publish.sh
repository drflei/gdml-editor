#!/bin/bash
# Script to prepare and publish GDML Editor to GitHub and PyPI

set -e  # Exit on error

echo "======================================"
echo "GDML Editor - Publication Script"
echo "======================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Clean up
echo -e "\n${YELLOW}Step 1: Cleaning up old builds...${NC}"
rm -rf build/ dist/ *.egg-info
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
echo -e "${GREEN}✓ Cleanup complete${NC}"

# Step 2: Run tests
echo -e "\n${YELLOW}Step 2: Running tests...${NC}"
if command -v pytest &> /dev/null; then
    pytest tests/ || {
        echo "Tests failed. Fix tests before publishing."
        exit 1
    }
    echo -e "${GREEN}✓ All tests passed${NC}"
else
    echo "pytest not found, skipping tests"
fi

# Step 3: Check code quality
echo -e "\n${YELLOW}Step 3: Checking code quality...${NC}"
if command -v flake8 &> /dev/null; then
    flake8 gdml_editor --count --select=E9,F63,F7,F82 --show-source --statistics || {
        echo "Code quality check failed"
        exit 1
    }
    echo -e "${GREEN}✓ Code quality check passed${NC}"
else
    echo "flake8 not found, skipping code quality check"
fi

# Step 4: Build package
echo -e "\n${YELLOW}Step 4: Building package...${NC}"
python -m pip install --upgrade build twine
python -m build
echo -e "${GREEN}✓ Package built successfully${NC}"

# Step 5: Check package
echo -e "\n${YELLOW}Step 5: Checking package...${NC}"
twine check dist/*
echo -e "${GREEN}✓ Package check passed${NC}"

# Step 6: Git initialization (if needed)
echo -e "\n${YELLOW}Step 6: Git repository...${NC}"
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: GDML Editor v1.0.0"
    echo -e "${GREEN}✓ Git repository initialized${NC}"
else
    echo "Git repository already exists"
fi

# Step 7: Instructions
echo -e "\n${GREEN}======================================"
echo "Package is ready for publication!"
echo "======================================${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo ""
echo "1. Create GitHub repository:"
echo "   - Go to https://github.com/new"
echo "   - Name: gdml-editor"
echo "   - Description: GUI for editing GDML geometry files"
echo "   - Public/Private: Your choice"
echo "   - Don't initialize with README (we have one)"
echo ""
echo "2. Push to GitHub:"
echo "   git remote add origin https://github.com/YOURUSERNAME/gdml-editor.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Create PyPI account:"
echo "   - Go to https://pypi.org/account/register/"
echo "   - Verify your email"
echo ""
echo "4. Generate PyPI API token:"
echo "   - Go to https://pypi.org/manage/account/token/"
echo "   - Create token for gdml-editor"
echo "   - Save the token (you'll need it once)"
echo ""
echo "5. Publish to PyPI:"
echo "   twine upload dist/*"
echo "   # Enter __token__ as username"
echo "   # Enter your API token as password"
echo ""
echo "6. Or publish to Test PyPI first:"
echo "   twine upload --repository testpypi dist/*"
echo "   # Test installation:"
echo "   pip install -i https://test.pypi.org/simple/ gdml-editor"
echo ""
echo "7. Add GitHub secrets for automated releases:"
echo "   - Go to repository Settings → Secrets → Actions"
echo "   - Add PYPI_API_TOKEN with your token"
echo "   - Now GitHub Actions will auto-publish on release"
echo ""
echo -e "${GREEN}Files ready in dist/:${NC}"
ls -lh dist/
echo ""
echo -e "${GREEN}Good luck with your publication! 🚀${NC}"
