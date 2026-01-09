#!/bin/bash
# Script to update all documentation with your actual GitHub username
# Usage: ./update_github_username.sh YOUR_GITHUB_USERNAME

if [ -z "$1" ]; then
    echo "Usage: ./update_github_username.sh YOUR_GITHUB_USERNAME"
    echo "Example: ./update_github_username.sh flei"
    exit 1
fi

USERNAME="$1"
echo "Updating GitHub username to: $USERNAME"

# Files to update
FILES=(
    "README.md"
    "QUICK_START.md"
    "PUBLICATION_CHECKLIST.md"
    "PACKAGE_SUMMARY.md"
    "CONTRIBUTING.md"
    "setup.py"
    "pyproject.toml"
)

# Backup originals
echo "Creating backups..."
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$file.bak"
    fi
done

# Replace YOURUSERNAME with actual username
echo "Updating files..."
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        sed -i "s/YOURUSERNAME/$USERNAME/g" "$file"
        echo "  ✓ Updated $file"
    fi
done

echo ""
echo "Update complete! Files updated:"
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  - $file"
    fi
done

echo ""
echo "Backups created with .bak extension"
echo "If you need to revert: ./revert_username_changes.sh"
