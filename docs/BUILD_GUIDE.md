# Build Guide - Creating Executables

This guide explains how to create standalone executable files (.exe for Windows, .dmg for macOS) for the SendApi application.

## Prerequisites

### For Windows:
- Python 3.8+ installed
- pip package manager
- Windows 10/11

### For macOS:
- Python 3.8+ installed
- pip3 package manager
- macOS 10.13+ (High Sierra or later)

## Quick Build Instructions

### Windows (.exe file)

1. **Open Command Prompt** in the project directory
2. **Run the build script:**
   ```cmd
   build_windows.bat
   ```
3. **Find the executable** at: `dist\SendApi.exe`

### macOS (.dmg file)

1. **Open Terminal** in the project directory
2. **Run the build script:**
   ```bash
   ./build_macos.sh
   ```
3. **Find the DMG file** at: `SendApi.dmg`

## Manual Build Instructions

If the automated scripts don't work, you can build manually:

### 1. Install Dependencies
```bash
# Windows
pip install -r requirements.txt

# macOS
pip3 install -r requirements.txt
```

### 2. Build with PyInstaller
```bash
# Windows
pyinstaller --clean sendapi.spec

# macOS
pyinstaller --clean sendapi.spec
```

### 3. Create DMG (macOS only)
```bash
# Create temporary directory
mkdir -p dmg_temp
cp -r dist/SendApi.app dmg_temp/

# Create DMG
hdiutil create -volname "SendApi" -srcfolder dmg_temp -ov -format UDZO SendApi.dmg

# Clean up
rm -rf dmg_temp
```

## Output Files

### Windows
- **Location**: `dist\SendApi.exe`
- **Type**: Standalone executable
- **Size**: ~50-100 MB
- **Usage**: Double-click to run

### macOS
- **Location**: `SendApi.dmg`
- **Type**: Disk image containing .app bundle
- **Size**: ~50-100 MB
- **Usage**: 
  1. Double-click DMG to mount
  2. Drag SendApi.app to Applications
  3. Launch from Applications folder

## Troubleshooting

### Common Issues

#### 1. "Python not found"
- **Solution**: Install Python and add to PATH
- **Windows**: Download from python.org
- **macOS**: Use Homebrew: `brew install python`

#### 2. "pip not found"
- **Solution**: Install pip
- **Windows**: Usually comes with Python
- **macOS**: `python3 -m ensurepip --upgrade`

#### 3. "PyInstaller not found"
- **Solution**: Install PyInstaller
```bash
pip install pyinstaller
```

#### 4. Build fails with import errors
- **Solution**: Check that all dependencies are installed
```bash
pip install -r requirements.txt
```

#### 5. Large file size
- **Normal**: PyInstaller bundles Python runtime and all dependencies
- **Expected**: 50-100 MB for GUI applications

### Platform-Specific Issues

#### Windows
- **Antivirus warnings**: Common with PyInstaller executables
- **Solution**: Add exception or sign the executable
- **Missing DLLs**: Usually resolved by PyInstaller automatically

#### macOS
- **Gatekeeper warnings**: "App is from unidentified developer"
- **Solution**: Right-click → Open, or disable Gatekeeper temporarily
- **Code signing**: Optional but recommended for distribution

## Distribution

### Windows
- Share the `SendApi.exe` file directly
- Users can run without installation
- Consider creating an installer with tools like Inno Setup

### macOS
- Share the `SendApi.dmg` file
- Users mount and install to Applications
- Consider code signing for App Store distribution

## Advanced Configuration

### Custom Icons
1. Create .ico file (Windows) or .icns file (macOS)
2. Update the spec file:
```python
exe = EXE(
    # ... other options ...
    icon='path/to/icon.ico',  # Windows
)

app = BUNDLE(
    exe,
    icon='path/to/icon.icns',  # macOS
    # ... other options ...
)
```

### Code Signing (macOS)
```bash
# Sign the app bundle
codesign --force --deep --sign "Developer ID Application: Your Name" dist/SendApi.app

# Create DMG with signed app
hdiutil create -volname "SendApi" -srcfolder dmg_temp -ov -format UDZO SendApi.dmg
```

### Optimizing Size
- Use `--exclude-module` to remove unused modules
- Use UPX compression (already enabled in spec file)
- Consider using `--onefile` vs `--onedir` mode

## File Structure After Build

```
project/
├── dist/
│   ├── SendApi.exe               # Windows executable
│   └── SendApi.app/              # macOS app bundle
├── build/                        # Build artifacts
├── SendApi.dmg                   # macOS disk image
└── sendapi.spec                  # PyInstaller spec file
```

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify Python and pip versions
3. Try manual build steps
4. Check PyInstaller documentation: https://pyinstaller.org/ 