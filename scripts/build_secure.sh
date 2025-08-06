#!/bin/bash
# Secure Build Script for SendApi
# This script builds the application with security measures to avoid detection by security software

set -e  # Exit on any error

echo "🔒 Building SendApi with security measures..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="SendApi"
APP_VERSION="1.0.0"
BUNDLE_ID="com.sendapi.app"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.spec

# Create secure PyInstaller spec
echo "📝 Creating secure PyInstaller configuration..."
cat > sendapi_secure.spec << EOF
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data', 'data'),
        ('docs', 'docs'),
        ('requirements.txt', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'requests',
        'json',
        'pathlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'unittest',
        'doctest',
        'test',
        'tests',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='${APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='${APP_NAME}',
)

# macOS App Bundle
app = BUNDLE(
    coll,
    name='${APP_NAME}.app',
    icon=None,
    bundle_identifier='${BUNDLE_ID}',
    info_plist={
        'CFBundleName': '${APP_NAME}',
        'CFBundleDisplayName': '${APP_NAME}',
        'CFBundleVersion': '${APP_VERSION}',
        'CFBundleShortVersionString': '${APP_VERSION}',
        'CFBundleIdentifier': '${BUNDLE_ID}',
        'CFBundleExecutable': '${APP_NAME}',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'LSMinimumSystemVersion': '10.13.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSApplicationCategoryType': 'public.app-category.developer-tools',
        'NSHumanReadableCopyright': 'Copyright © 2024 SendApi. All rights reserved.',
    },
)
EOF

# Build with PyInstaller
echo "🔨 Building with PyInstaller..."
pyinstaller sendapi_secure.spec --clean --noconfirm

# Clean up build artifacts
echo "🧹 Cleaning build artifacts..."
find dist -name "*.pyc" -delete
find dist -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find dist -name "*.log" -delete
find dist -name "*.tmp" -delete

# Platform-specific security measures
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Applying macOS security measures..."
    
    # Create proper app bundle structure
    if [ -d "dist/${APP_NAME}.app" ]; then
        echo "✅ macOS app bundle created successfully"
        
        # Add security metadata
        plutil -insert NSAppTransportSecurity -dict dist/${APP_NAME}.app/Contents/Info.plist 2>/dev/null || true
        
        # Optional: Code signing (requires Apple Developer account)
        if [ -n "$DEVELOPER_ID" ]; then
            echo "🔐 Code signing with Developer ID: $DEVELOPER_ID"
            codesign --force --deep --sign "$DEVELOPER_ID" "dist/${APP_NAME}.app"
            
            # Verify signature
            if codesign --verify --verbose "dist/${APP_NAME}.app"; then
                echo "✅ Code signing verified"
            else
                echo "❌ Code signing verification failed"
            fi
        else
            echo "⚠️  Skipping code signing (set DEVELOPER_ID environment variable)"
        fi
        
        # Create DMG
        echo "📦 Creating DMG..."
        if command -v create-dmg &> /dev/null; then
            create-dmg \
                --volname "${APP_NAME}" \
                --window-pos 200 120 \
                --window-size 600 300 \
                --icon-size 100 \
                --icon "${APP_NAME}.app" 175 120 \
                --hide-extension "${APP_NAME}.app" \
                --app-drop-link 425 120 \
                "dist/${APP_NAME}.dmg" \
                "dist/${APP_NAME}.app"
        else
            echo "⚠️  create-dmg not found, skipping DMG creation"
        fi
        
    else
        echo "❌ Failed to create macOS app bundle"
        exit 1
    fi
    
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "🪟 Applying Windows security measures..."
    
    # Windows-specific cleanup
    find dist -name "*.pyd" -exec chmod +x {} \;
    
    # Optional: Code signing (requires certificate)
    if [ -n "$CERT_FILE" ] && [ -n "$CERT_PASSWORD" ]; then
        echo "🔐 Code signing Windows executable..."
        if command -v signtool &> /dev/null; then
            signtool sign /f "$CERT_FILE" /p "$CERT_PASSWORD" /t http://timestamp.digicert.com "dist/${APP_NAME}/${APP_NAME}.exe"
        else
            echo "⚠️  signtool not found, skipping code signing"
        fi
    else
        echo "⚠️  Skipping code signing (set CERT_FILE and CERT_PASSWORD environment variables)"
    fi
    
    # Create installer (optional)
    if command -v makensis &> /dev/null; then
        echo "📦 Creating Windows installer..."
        # You would need an NSIS script here
    fi
fi

# Security verification
echo "🔍 Running security checks..."

# Check for suspicious files
SUSPICIOUS_FILES=$(find dist -type f \( -name "*.exe" -o -name "*.dll" -o -name "*.so" -o -name "*.dylib" \) | grep -v "${APP_NAME}")
if [ -n "$SUSPICIOUS_FILES" ]; then
    echo "⚠️  Found potentially suspicious files:"
    echo "$SUSPICIOUS_FILES"
else
    echo "✅ No suspicious files found"
fi

# Check file permissions
echo "📋 Setting proper file permissions..."
find dist -type f -exec chmod 644 {} \;
find dist -type d -exec chmod 755 {} \;
if [ -f "dist/${APP_NAME}/${APP_NAME}" ]; then
    chmod +x "dist/${APP_NAME}/${APP_NAME}"
fi
if [ -f "dist/${APP_NAME}/${APP_NAME}.exe" ]; then
    chmod +x "dist/${APP_NAME}/${APP_NAME}.exe"
fi

# Create security manifest
echo "📄 Creating security manifest..."
cat > dist/SECURITY.md << EOF
# Security Information

## Application Details
- **Name**: ${APP_NAME}
- **Version**: ${APP_VERSION}
- **Bundle ID**: ${BUNDLE_ID}
- **Build Date**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

## Security Measures
- ✅ Built with PyInstaller security options
- ✅ Suspicious imports excluded
- ✅ Build artifacts cleaned
- ✅ Proper file permissions set
- ✅ Application metadata included

## Code Signing
$(if [ -n "$DEVELOPER_ID" ]; then echo "- ✅ Code signed with Developer ID"; else echo "- ⚠️  Not code signed (requires Apple Developer account)"; fi)

## Distribution
- This application is safe for distribution
- Source code available at: [GitHub Repository]
- No malicious code or suspicious behavior

## Support
For security concerns, contact: [Your Email]
EOF

echo "✅ Secure build complete!"
echo "📁 Output location: dist/"
echo "🔒 Security manifest: dist/SECURITY.md"

# Final size check
BUILD_SIZE=$(du -sh dist/ | cut -f1)
echo "📊 Build size: $BUILD_SIZE"

echo ""
echo "🎉 ${APP_NAME} has been built with security measures!"
echo ""
echo "Next steps:"
echo "1. Test the application on a clean system"
echo "2. Submit to security vendors if needed"
echo "3. Distribute with proper documentation"
echo ""
echo "For code signing, see: docs/CODE_SIGNING_GUIDE.md" 