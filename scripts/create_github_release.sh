#!/bin/bash
# GitHub Release Creation Script

set -e

echo "🚀 Creating GitHub Release..."

# Configuration
REPO_OWNER="yourusername"
REPO_NAME="SendApi"
VERSION="1.0.0"
TAG_NAME="v$VERSION"
RELEASE_NAME="SendApi $VERSION"
BUILDS_DIR="distributions"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "📋 Configuration:"
echo "  Repository: $REPO_OWNER/$REPO_NAME"
echo "  Version: $VERSION"
echo "  Tag: $TAG_NAME"
echo "  Builds directory: $BUILDS_DIR"
echo ""

# Check if builds directory exists
if [ ! -d "$BUILDS_DIR" ]; then
    echo "❌ Builds directory not found: $BUILDS_DIR"
    echo "   Run ./scripts/build_distributions.sh first"
    exit 1
fi

# Check if files exist
echo "🔍 Checking distribution files..."

if [ -f "$BUILDS_DIR/SendApi-$VERSION-Apple-Silicon.dmg" ]; then
    echo "✅ Apple Silicon DMG found"
    APPLE_SILICON_SIZE=$(du -h "$BUILDS_DIR/SendApi-$VERSION-Apple-Silicon.dmg" | cut -f1)
else
    echo "❌ Apple Silicon DMG not found!"
    exit 1
fi

if [ -f "$BUILDS_DIR/SendApi-$VERSION-Intel.dmg" ]; then
    echo "✅ Intel DMG found"
    INTEL_SIZE=$(du -h "$BUILDS_DIR/SendApi-$VERSION-Intel.dmg" | cut -f1)
else
    echo "⚠️  Intel DMG not found (will create placeholder)"
    INTEL_SIZE="Placeholder"
fi

if [ -f "$BUILDS_DIR/SendApi-$VERSION-Windows.exe" ]; then
    echo "✅ Windows EXE found"
    WINDOWS_SIZE=$(du -h "$BUILDS_DIR/SendApi-$VERSION-Windows.exe" | cut -f1)
else
    echo "⚠️  Windows EXE not found (will create placeholder)"
    WINDOWS_SIZE="Placeholder"
fi

# Create release notes
echo "📝 Creating release notes..."

cat > "RELEASE_NOTES.md" << EOF
# SendApi $VERSION

## 🎉 What's New

- **Initial release** of SendApi API testing tool
- **Cross-platform support** for macOS and Windows
- **Security measures** implemented for safe distribution
- **Professional GUI** built with PySide6
- **SmartScreen-friendly** distribution through GitHub Releases

## 📦 Downloads

### macOS
- **Apple Silicon (M1/M2/M3)**: [SendApi-$VERSION-Apple-Silicon.dmg]($BUILDS_DIR/SendApi-$VERSION-Apple-Silicon.dmg) ($APPLE_SILICON_SIZE)
- **Intel Macs**: [SendApi-$VERSION-Intel.dmg]($BUILDS_DIR/SendApi-$VERSION-Intel.dmg) ($INTEL_SIZE)

### Windows
- **Windows x64**: [SendApi-$VERSION-Windows.exe]($BUILDS_DIR/SendApi-$VERSION-Windows.exe) ($WINDOWS_SIZE)

## 🔧 Installation

### macOS
1. Download the appropriate DMG file for your Mac
2. Double-click to mount the DMG
3. Drag SendApi.app to Applications folder
4. Run from Applications

### Windows
1. Download the Windows executable
2. Right-click → Properties → Unblock (if needed)
3. Run the executable
4. If SmartScreen blocks, click "More info" → "Run anyway"

## 🛡️ Security

- ✅ **Built with security measures** to avoid false positives
- ✅ **Source code available** for verification
- ✅ **No malicious code** or suspicious behavior
- ✅ **Open source** and transparent
- ✅ **Distributed through GitHub** for higher trust

## 📋 System Requirements

- **macOS**: 10.13 or later
- **Windows**: Windows 10 or later
- **Memory**: 4GB RAM minimum
- **Storage**: 200MB free space

## 🐛 Known Issues

- Windows Intel and Windows builds are placeholders
- Requires actual Windows environment for Windows builds
- Intel DMG requires cross-compilation setup

## 📞 Support

- **GitHub Issues**: https://github.com/$REPO_OWNER/$REPO_NAME/issues
- **Documentation**: https://github.com/$REPO_OWNER/$REPO_NAME#readme
- **Security**: See SECURITY.md for details

## 🔄 Changelog

### $VERSION (Initial Release)
- Initial release of SendApi
- API testing interface
- Request/response handling
- Environment management
- Security measures implemented
- SmartScreen-friendly distribution

## 🚀 SmartScreen Solutions

This release includes solutions for Windows Defender SmartScreen:

- **GitHub Releases**: Higher trust with Windows Defender
- **Installation guides**: Clear instructions for users
- **Security documentation**: Transparency and verification
- **False positive reporting**: Help improve detection

See \`WINDOWS_INSTALLATION_GUIDE.md\` for detailed SmartScreen bypass instructions.
EOF

echo "✅ Release notes created: RELEASE_NOTES.md"

# Create GitHub release workflow
echo "🔧 Creating GitHub workflow..."

mkdir -p .github/workflows

cat > ".github/workflows/release.yml" << EOF
name: Create Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-release:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build distributions
      run: |
        chmod +x scripts/build_distributions.sh
        ./scripts/build_distributions.sh
    
    - name: Create Release
      uses: softprops/action-gh-release@v1
      with:
        files: |
          distributions/*.dmg
          distributions/*.exe
          distributions/SECURITY.md
          distributions/BUILD_SUMMARY.md
          WINDOWS_INSTALLATION_GUIDE.md
        body_path: RELEASE_NOTES.md
        draft: false
        prerelease: false
      env:
        GITHUB_TOKEN: \${{ secrets.GITHUB_TOKEN }}
EOF

echo "✅ GitHub workflow created: .github/workflows/release.yml"

# Create git commands
echo "📋 Git commands to run:"
echo ""
echo "${BLUE}# 1. Add all files${NC}"
echo "git add ."
echo ""
echo "${BLUE}# 2. Commit changes${NC}"
echo "git commit -m \"Prepare release $TAG_NAME\""
echo ""
echo "${BLUE}# 3. Push to GitHub${NC}"
echo "git push origin main"
echo ""
echo "${BLUE}# 4. Create and push tag${NC}"
echo "git tag $TAG_NAME"
echo "git push origin $TAG_NAME"
echo ""
echo "${BLUE}# 5. Manual release creation${NC}"
echo "Go to: https://github.com/$REPO_OWNER/$REPO_NAME/releases/new"
echo "Tag: $TAG_NAME"
echo "Title: $RELEASE_NAME"
echo "Description: Copy from RELEASE_NOTES.md"
echo "Upload files from: $BUILDS_DIR/"
echo ""

# Create quick release script
cat > "scripts/quick_release.sh" << 'EOF'
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
EOF

chmod +x scripts/quick_release.sh

echo "✅ Quick release script created: scripts/quick_release.sh"
echo ""
echo "${GREEN}🎉 GitHub release preparation complete!${NC}"
echo ""
echo "${YELLOW}📋 Next steps:${NC}"
echo "1. Update REPO_OWNER in this script to your GitHub username"
echo "2. Run: ./scripts/quick_release.sh"
echo "3. Go to GitHub and create the release manually"
echo "4. Upload your distribution files"
echo "5. Publish the release"
echo ""
echo "${BLUE}💡 GitHub Releases will significantly reduce SmartScreen warnings!${NC}" 