# Code Signing & Security Guide

This guide explains how to make your SendApi application safe from Windows Defender, macOS Gatekeeper, and other security software.

## 🍎 **macOS Code Signing**

### 1. **Apple Developer Account**
- Sign up for Apple Developer Program ($99/year)
- Required for App Store distribution and trusted code signing

### 2. **Code Signing Process**
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Create a Developer ID certificate
# Go to Apple Developer Portal → Certificates → Developer ID Application

# Code sign your app
codesign --force --deep --sign "Developer ID Application: Your Name" dist/SendApi.app

# Verify the signature
codesign --verify --verbose dist/SendApi.app
```

### 3. **Notarization (Required for macOS 10.15+)**
```bash
# Create a notarization request
xcrun altool --notarize-app \
  --primary-bundle-id "com.yourcompany.sendapi" \
  --username "your-apple-id@example.com" \
  --password "@env:APPLE_APP_PASSWORD" \
  --file "dist/SendApi.dmg"

# Check notarization status
xcrun altool --notarization-info [UUID] \
  --username "your-apple-id@example.com" \
  --password "@env:APPLE_APP_PASSWORD"

# Staple the notarization ticket
xcrun stapler staple dist/SendApi.dmg
```

## 🪟 **Windows Code Signing**

### 1. **Code Signing Certificate**
- Purchase a Code Signing Certificate from a trusted CA (DigiCert, Sectigo, etc.)
- Costs range from $200-500/year

### 2. **Code Signing Process**
```bash
# Using signtool (Windows)
signtool sign /f certificate.p12 /p password /t http://timestamp.digicert.com dist/SendApi.exe

# Using osslsigncode (Cross-platform)
osslsigncode sign -certs certificate.pem -key private_key.pem \
  -n "SendApi" -i "https://yourwebsite.com" \
  -t http://timestamp.digicert.com \
  -in dist/SendApi.exe -out dist/SendApi-signed.exe
```

## 🔧 **PyInstaller Security Best Practices**

### 1. **Update PyInstaller Configuration**
```python
# sendapi.spec
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('data', 'data'), ('docs', 'docs')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Add security options
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SendApi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress executable
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,  # Will be set during signing
    entitlements_file=None,
)
```

### 2. **Build Scripts with Security Options**
```bash
#!/bin/bash
# scripts/build_secure.sh

echo "🔒 Building secure application..."

# Clean previous builds
rm -rf build/ dist/

# Build with PyInstaller
pyinstaller sendapi.spec --clean

# Code sign for macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Code signing for macOS..."
    codesign --force --deep --sign "Developer ID Application: Your Name" dist/SendApi.app
    
    # Create DMG
    create-dmg dist/SendApi.dmg dist/SendApi.app
    
    # Notarize (if you have Apple Developer account)
    # xcrun altool --notarize-app --primary-bundle-id "com.yourcompany.sendapi" \
    #   --username "your-apple-id@example.com" \
    #   --password "@env:APPLE_APP_PASSWORD" \
    #   --file "dist/SendApi.dmg"
fi

# Code sign for Windows (if on Windows or using cross-compilation)
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    echo "🪟 Code signing for Windows..."
    signtool sign /f certificate.p12 /p "$CERT_PASSWORD" /t http://timestamp.digicert.com dist/SendApi.exe
fi

echo "✅ Secure build complete!"
```

## 🛡️ **Additional Security Measures**

### 1. **Remove Suspicious Imports**
```python
# Avoid these imports that might trigger security software
# import subprocess  # Use with caution
# import os.system   # Use with caution
# import eval        # NEVER use
# import exec        # NEVER use

# Instead, use safer alternatives
import shutil
import pathlib
import json
```

### 2. **Clean Up PyInstaller Output**
```python
# Remove unnecessary files that might trigger security software
import os
import shutil

def cleanup_build():
    """Remove unnecessary files from build"""
    files_to_remove = [
        '*.pyc',
        '__pycache__',
        '*.log',
        '*.tmp'
    ]
    
    for pattern in files_to_remove:
        for file in pathlib.Path('dist').glob(pattern):
            if file.is_file():
                file.unlink()
            elif file.is_dir():
                shutil.rmtree(file)
```

### 3. **Add Application Metadata**
```python
# Add proper application metadata
APP_METADATA = {
    'name': 'SendApi',
    'version': '1.0.0',
    'description': 'API Testing Application',
    'author': 'Your Name',
    'author_email': 'your-email@example.com',
    'url': 'https://yourwebsite.com',
    'license': 'MIT',
}
```

## 📋 **Checklist for Security Software Compatibility**

### **Before Distribution:**
- [ ] Code sign your application
- [ ] Notarize (macOS)
- [ ] Test on clean systems
- [ ] Submit to security vendors for whitelisting
- [ ] Use HTTPS for downloads
- [ ] Provide clear documentation
- [ ] Include privacy policy
- [ ] Add application metadata

### **Common Triggers to Avoid:**
- [ ] No unsigned executables
- [ ] No suspicious file operations
- [ ] No network connections to unknown servers
- [ ] No file system access without user permission
- [ ] No process creation without user consent
- [ ] No registry modifications (Windows)
- [ ] No system directory modifications

## 🚨 **Emergency Measures**

### **If Your App Gets Flagged:**

1. **Submit to Security Vendors:**
   - Microsoft Security Response Center
   - Apple Security
   - Submit false positive reports

2. **Provide Evidence:**
   - Source code repository
   - Code signing certificates
   - Notarization receipts
   - Clear documentation

3. **Alternative Distribution:**
   - GitHub Releases
   - Source code distribution
   - Package managers (pip, brew, chocolatey)

## 📞 **Support Resources**

- **Apple Developer Support**: https://developer.apple.com/support/
- **Microsoft Security Response**: https://www.microsoft.com/en-us/msrc
- **PyInstaller Security**: https://pyinstaller.readthedocs.io/en/stable/usage.html#security

## 🔍 **Testing Your App**

```bash
# Test on clean macOS
# 1. Create a new user account
# 2. Install your app
# 3. Check Gatekeeper behavior

# Test on clean Windows
# 1. Use Windows Sandbox
# 2. Check Windows Defender behavior
# 3. Test SmartScreen

# Test with security tools
# - VirusTotal
# - Hybrid Analysis
# - Any.Run
```

Remember: **Code signing is essential for trusted distribution!** 