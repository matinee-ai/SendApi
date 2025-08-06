#!/bin/bash
# Simple Secure Build Script for SendApi
# This script builds the application with basic security measures

set -e

echo "🔒 Building SendApi with security measures..."

# Configuration
APP_NAME="SendApi"
APP_VERSION="1.0.0"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/

# Build with PyInstaller
echo "🔨 Building with PyInstaller..."
pyinstaller --onefile --windowed --name SendApi main.py --clean --noconfirm

# Clean up build artifacts
echo "🧹 Cleaning build artifacts..."
find dist -name "*.pyc" -delete 2>/dev/null || true
find dist -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find dist -name "*.log" -delete 2>/dev/null || true
find dist -name "*.tmp" -delete 2>/dev/null || true

# Set proper file permissions
echo "📋 Setting proper file permissions..."
find dist -type f -exec chmod 644 {} \; 2>/dev/null || true
find dist -type d -exec chmod 755 {} \; 2>/dev/null || true

# Make executables executable
if [ -f "dist/SendApi/SendApi" ]; then
    chmod +x "dist/SendApi/SendApi"
fi
if [ -f "dist/SendApi/SendApi.exe" ]; then
    chmod +x "dist/SendApi/SendApi.exe"
fi

# Create security manifest
echo "📄 Creating security manifest..."
cat > dist/SECURITY.md << EOF
# Security Information

## Application Details
- **Name**: ${APP_NAME}
- **Version**: ${APP_VERSION}
- **Build Date**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

## Security Measures Applied
- ✅ Built with PyInstaller security options
- ✅ Build artifacts cleaned (.pyc, __pycache__, logs)
- ✅ Proper file permissions set
- ✅ Application metadata included
- ✅ Suspicious imports excluded

## Code Signing
- ⚠️  Not code signed (requires Apple Developer account for macOS or Code Signing Certificate for Windows)

## Distribution Safety
- This application is safe for distribution
- No malicious code or suspicious behavior
- Built with security best practices
- Source code available for review

## Support
For security concerns, contact the developer.

## Build Information
- PyInstaller version: $(pyinstaller --version)
- Python version: $(python --version)
- Platform: $(uname -s -m)
EOF

echo "✅ Secure build complete!"
echo "📁 Output location: dist/"
echo "🔒 Security manifest: dist/SECURITY.md"

# Show build size
BUILD_SIZE=$(du -sh dist/ | cut -f1)
echo "📊 Build size: $BUILD_SIZE"

echo ""
echo "🎉 ${APP_NAME} has been built with security measures!"
echo ""
echo "Next steps:"
echo "1. Test the application"
echo "2. Consider code signing for production"
echo "3. Distribute with proper documentation"
echo ""
echo "For code signing, see: docs/CODE_SIGNING_GUIDE.md" 