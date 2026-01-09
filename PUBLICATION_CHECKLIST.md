# Publication Checklist for GDML Editor

Use this checklist to ensure a smooth publication process to GitHub and PyPI.

## Pre-Publication ✓

- [x] Package structure created (`gdml_editor/` directory)
- [x] All code files moved to package
- [x] `__init__.py` created with proper exports
- [x] `setup.py` configured with metadata
- [x] `pyproject.toml` created for modern packaging
- [x] `requirements.txt` lists all dependencies
- [x] `README.md` comprehensive and well-formatted
- [x] `LICENSE` file added (MIT License)
- [x] `.gitignore` configured
- [x] `MANIFEST.in` includes necessary files
- [x] Documentation in `docs/` folder
- [x] Tests in `tests/` folder
- [x] CI/CD workflow configured (`.github/workflows/`)
- [x] `CHANGELOG.md` documenting changes
- [x] `CONTRIBUTING.md` with guidelines
- [x] Verification script passed (`./verify_setup.py`)

## GitHub Publication

### Step 1: Initialize Git Repository
```bash
cd /home/flei/gdml_editor
git init
git add .
git commit -m "Initial commit: GDML Editor v1.0.0"
```

- [ ] Git repository initialized
- [ ] Initial commit created
- [ ] All files staged and committed

### Step 2: Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `gdml-editor`
3. Description: `GUI for editing GDML geometry files with user-defined materials support`
4. Visibility: **Public** (recommended for open source)
5. **Do NOT** initialize with README, .gitignore, or license (we have these)
6. Click "Create repository"

- [ ] GitHub repository created
- [ ] Repository URL obtained

### Step 3: Push to GitHub
```bash
git remote add origin https://github.com/drflei/gdml-editor.git
git branch -M main
git push -u origin main
```

- [ ] Remote origin added
- [ ] Code pushed to GitHub
- [ ] Repository visible on GitHub

### Step 4: Configure GitHub Repository Settings
1. Go to repository Settings
2. **About** section (top right):
   - Add description
   - Add topics: `python`, `gdml`, `geant4`, `gui`, `geometry`, `materials`
   - Add website (if any)
3. **Pages** (optional):
   - Enable GitHub Pages from `docs/` folder
4. **Secrets and variables → Actions**:
   - Will add PYPI_API_TOKEN later

- [ ] Repository description added
- [ ] Topics added for discoverability
- [ ] Settings configured

## PyPI Publication

### Step 5: Create PyPI Account
1. Go to https://pypi.org/account/register/
2. Fill in registration form
3. Verify your email address
4. Enable 2FA (recommended)

- [ ] PyPI account created
- [ ] Email verified
- [ ] 2FA enabled (optional but recommended)

### Step 6: Build Package
```bash
cd /home/flei/gdml_editor
./publish.sh
```

Or manually:
```bash
# Install build tools
pip install --upgrade build twine

# Clean old builds
rm -rf build/ dist/ *.egg-info

# Build package
python -m build

# Check package
twine check dist/*
```

- [ ] Build tools installed
- [ ] Package built successfully
- [ ] Package verification passed
- [ ] Files in `dist/`: `.whl` and `.tar.gz`

### Step 7: Test on Test PyPI (Recommended)
```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Test installation
pip install -i https://test.pypi.org/simple/ gdml-editor
```

- [ ] Uploaded to Test PyPI
- [ ] Tested installation from Test PyPI
- [ ] Verified package works correctly

### Step 8: Publish to PyPI
```bash
twine upload dist/*
```
When prompted:
- Username: `__token__`
- Password: `pypi-...` (your API token)

- [ ] Generated PyPI API token
- [ ] Package uploaded to PyPI
- [ ] Package visible at https://pypi.org/project/gdml-editor/

### Step 9: Verify Installation
```bash
# In a fresh environment
pip install gdml-editor

# Test it works
gdml-editor
```

- [ ] Successfully installed from PyPI
- [ ] Command-line tool works
- [ ] GUI launches correctly

## Post-Publication

### Step 10: Add GitHub Release
1. Go to repository on GitHub
2. Click "Releases" → "Create a new release"
3. Tag: `v1.0.0`
4. Release title: `GDML Editor v1.0.0`
5. Description: Copy from CHANGELOG.md
6. Upload built packages from `dist/`
7. Click "Publish release"

- [ ] GitHub release created
- [ ] Release notes added
- [ ] Built packages attached

### Step 11: Configure Automated Publishing
1. Go to PyPI → Account Settings → API Tokens
2. Create project-specific token for `gdml-editor`
3. Copy the token
4. Go to GitHub repository → Settings → Secrets and variables → Actions
5. Click "New repository secret"
6. Name: `PYPI_API_TOKEN`
7. Value: (paste your token)
8. Save

Now GitHub Actions will automatically publish to PyPI on new releases!

- [ ] PyPI API token generated
- [ ] Token added to GitHub secrets
- [ ] Workflow tested (create a tag and push)

### Step 12: Update Documentation
1. Update README.md badges with actual URLs
2. Update QUICK_START.md with correct GitHub username
3. Update examples to use real repository URL

```bash
# Replace drflei with actual username
find . -type f -name "*.md" -exec sed -i 's/drflei/YOUR_ACTUAL_USERNAME/g' {} +
git add .
git commit -m "docs: Update documentation with actual URLs"
git push
```

- [ ] Documentation URLs updated
- [ ] Changes committed and pushed

### Step 13: Announce and Share
- [ ] Update project website (if any)
- [ ] Announce on relevant forums/communities
- [ ] Share on social media
- [ ] Add to awesome lists (e.g., awesome-python)

## Optional Enhancements

### Code Quality
```bash
# Add pre-commit hooks
pip install pre-commit
pre-commit install

# Run code formatters
pip install black isort flake8
black gdml_editor/
isort gdml_editor/
flake8 gdml_editor/
```

### Documentation Site
```bash
# Create documentation with Sphinx
pip install sphinx sphinx-rtd-theme
sphinx-quickstart docs
# Build docs
cd docs && make html
```

### Test Coverage
```bash
pip install pytest pytest-cov
pytest --cov=gdml_editor tests/
```

## Troubleshooting

### Issue: "Package name already taken"
**Solution**: Choose a different name in setup.py and pyproject.toml

### Issue: "Authentication failed" on PyPI upload
**Solution**: 
- Verify API token is correct
- Use `__token__` as username
- Token should start with `pypi-`

### Issue: GitHub Actions workflow fails
**Solution**:
- Check workflow logs in Actions tab
- Verify PYPI_API_TOKEN secret is set
- Ensure token has correct permissions

### Issue: Package installs but command not found
**Solution**:
- Check entry_points in setup.py
- Ensure PATH includes pip's bin directory
- Try `python -m gdml_editor.gui` instead

## Success Criteria

✅ Package published to PyPI
✅ Code on GitHub with proper documentation
✅ CI/CD pipeline working
✅ Users can `pip install gdml-editor`
✅ Command-line tool works: `gdml-editor`
✅ GitHub release created
✅ All tests passing

## Next Steps After Publication

1. Monitor GitHub Issues for bug reports
2. Respond to user questions
3. Accept pull requests from contributors
4. Plan future features (see CONTRIBUTING.md)
5. Maintain CHANGELOG.md for new versions
6. Regularly update dependencies

---

**Current Status**: Pre-publication complete ✓
**Next Action**: Initialize Git repository (Step 1)

**Ready to publish! 🚀**
