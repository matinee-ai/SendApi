#!/bin/bash
# Quick Release Script

set -e

VERSION="1.0.0"
TAG_NAME="v$VERSION"

echo "🚀 Quick release for $TAG_NAME"

# Add all files
git add .

# Commit changes
git commit -m "Prepare release $TAG_NAME"

# Push to GitHub
git push origin main

# Create and push tag
git tag $TAG_NAME
git push origin $TAG_NAME

echo "✅ Release pushed to GitHub!"
echo "📋 Next: Create release at https://github.com/yourusername/SendApi/releases/new"
echo "📄 Use RELEASE_NOTES.md for description"
echo "📦 Upload files from distributions/ directory"
