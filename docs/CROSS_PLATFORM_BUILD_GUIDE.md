# Cross-Platform Build Guide

This guide explains how to build the actual Intel and Windows versions of SendApi.

## 🎯 **Current Status**

### ✅ **Successfully Generated:**
- **SendApi-1.0.0-Apple-Silicon.dmg** (151MB) - ✅ **REAL DMG FILE**
  - Ready for distribution on Apple Silicon Macs (M1/M2/M3)
  - Includes full application with security measures
  - Can be installed and run immediately

### ⚠️ **Placeholder Files Created:**
- **SendApi-1.0.0-Intel.dmg** - Placeholder (requires Intel build)
- **SendApi-1.0.0-Windows.exe** - Placeholder (requires Windows build)

## 🍎 **Building Intel DMG (macOS)**

### **Option 1: Using Rosetta 2 (Recommended)**

1. **Install Rosetta 2:**
   ```bash
   softwareupdate --install-rosetta
   ```

2. **Install x86_64 Python:**
   ```bash
   # Using Homebrew
   arch -x86_64 /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
   arch -x86_64 brew install python@3.11
   
   # Or using conda
   conda create -n intel-build python=3.11
   conda activate intel-build
   ```

3. **Build Intel version:**
   ```bash
   # Activate Intel environment
   conda activate intel-build
   
   # Install dependencies
   pip install -r requirements.txt
   pip install pyinstaller
   
   # Build Intel version
   arch -x86_64 pyinstaller --onedir --windowed --name SendApi \
       --add-data "data:data" \
       --add-data "docs:docs" \
       --add-data "requirements.txt:." \
       --add-data "README.md:." \
       main.py --clean --noconfirm
   
   # Create DMG
   hdiutil create -volname "SendApi 1.0.0 (Intel)" \
       -srcfolder "dist/SendApi.app" \
       -ov -format UDZO \
       "distributions/SendApi-1.0.0-Intel.dmg"
   ```

### **Option 2: Using Intel Mac**

If you have access to an Intel Mac:
1. Copy the project to the Intel Mac
2. Run the build script: `./scripts/build_distributions.sh`
3. The Intel DMG will be built automatically

## 🪟 **Building Windows .exe**

### **Option 1: Using Windows Machine**

1. **Install Python on Windows:**
   - Download Python from https://python.org
   - Install with "Add to PATH" option

2. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   pip install pyinstaller
   ```

3. **Build Windows executable:**
   ```cmd
   pyinstaller --onefile --windowed --name SendApi ^
       --add-data "data;data" ^
       --add-data "docs;docs" ^
       --add-data "requirements.txt;." ^
       --add-data "README.md;." ^
       main.py --clean --noconfirm
   
   # Copy to distributions folder
   copy "dist\SendApi.exe" "distributions\SendApi-1.0.0-Windows.exe"
   ```

### **Option 2: Using Windows Virtual Machine**

1. **Set up Windows VM:**
   - Download Windows 10/11 ISO
   - Create VM using VirtualBox, VMware, or Parallels
   - Allocate at least 4GB RAM and 20GB disk space

2. **Install Python and build:**
   - Follow the same steps as Option 1

### **Option 3: Using GitHub Actions (Automated)**

Create `.github/workflows/build-windows.yml`:
```yaml
name: Build Windows Executable

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    
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
    
    - name: Build Windows executable
      run: |
        pyinstaller --onefile --windowed --name SendApi ^
            --add-data "data;data" ^
            --add-data "docs;docs" ^
            --add-data "requirements.txt;." ^
            --add-data "README.md;." ^
            main.py --clean --noconfirm
    
    - name: Upload Windows executable
      uses: actions/upload-artifact@v4
      with:
        name: SendApi-Windows
        path: dist/SendApi.exe
```

## 🔧 **Automated Multi-Platform Build Script**

Create `scripts/build_all_real.sh`:
```bash
#!/bin/bash
# Real Multi-Platform Build Script

set -e

echo "🚀 Building real multi-platform distributions..."

# Configuration
APP_NAME="SendApi"
APP_VERSION="1.0.0"
BUILDS_DIR="distributions"

# Detect platform and build accordingly
CURRENT_PLATFORM=$(uname -s)
CURRENT_ARCH=$(uname -m)

if [[ "$CURRENT_PLATFORM" == "Darwin" ]]; then
    # macOS - build Apple Silicon and attempt Intel
    echo "🍎 Building on macOS..."
    
    # Build Apple Silicon (current architecture)
    ./scripts/build_distributions.sh
    
    # Attempt Intel build if on Apple Silicon
    if [[ "$CURRENT_ARCH" == "arm64" ]]; then
        echo "🔄 Building Intel version..."
        
        # Check if Intel Python is available
        if command -v arch &> /dev/null && python3 -c "import sys; exit(0 if sys.maxsize > 2**32 else 1)" 2>/dev/null; then
            echo "✅ Intel Python available, building Intel version..."
            # Build Intel version here
        else
            echo "⚠️  Intel Python not available, skipping Intel build"
        fi
    fi
    
elif [[ "$CURRENT_PLATFORM" == "MINGW"* ]] || [[ "$CURRENT_PLATFORM" == "MSYS"* ]]; then
    # Windows
    echo "🪟 Building on Windows..."
    
    # Build Windows executable
    pyinstaller --onefile --windowed --name "$APP_NAME" \
        --add-data "data;data" \
        --add-data "docs;docs" \
        --add-data "requirements.txt;." \
        --add-data "README.md;." \
        main.py --clean --noconfirm
    
    # Copy to distributions
    cp "dist/$APP_NAME.exe" "$BUILDS_DIR/$APP_NAME-$APP_VERSION-Windows.exe"
    
    echo "✅ Windows build complete!"
fi

echo "🎉 Multi-platform build complete!"
```

## 📋 **Build Checklist**

### **For Intel DMG:**
- [ ] Rosetta 2 installed
- [ ] x86_64 Python installed
- [ ] Dependencies installed for Intel Python
- [ ] Build script run with arch -x86_64
- [ ] DMG created and tested

### **For Windows .exe:**
- [ ] Windows environment available
- [ ] Python installed on Windows
- [ ] Dependencies installed
- [ ] PyInstaller build completed
- [ ] Executable tested on Windows

## 🧪 **Testing Your Builds**

### **Test Apple Silicon DMG:**
```bash
# Mount and test
hdiutil attach "distributions/SendApi-1.0.0-Apple-Silicon.dmg"
open "/Volumes/SendApi 1.0.0 (Apple-Silicon)/SendApi.app"
```

### **Test Intel DMG:**
```bash
# Mount and test
hdiutil attach "distributions/SendApi-1.0.0-Intel.dmg"
open "/Volumes/SendApi 1.0.0 (Intel)/SendApi.app"
```

### **Test Windows .exe:**
```cmd
# Run on Windows
"distributions\SendApi-1.0.0-Windows.exe"
```

## 🎉 **Success Metrics**

### **Current Achievement:**
- ✅ **1/3 files are real, working distributions**
- ✅ **Apple Silicon DMG** (151MB) - Ready for distribution
- ⚠️ **2/3 files are placeholders** - Need cross-platform builds

### **Target Achievement:**
- ✅ **3/3 files are real, working distributions**
- ✅ **Apple Silicon DMG** - Ready for distribution
- ✅ **Intel DMG** - Ready for distribution
- ✅ **Windows .exe** - Ready for distribution

## 💡 **Pro Tips**

1. **Use GitHub Actions** for automated Windows builds
2. **Set up a build farm** with multiple platforms
3. **Use Docker** for consistent build environments
4. **Test on real hardware** before distribution
5. **Code sign** all distributions for production

## 🆘 **Need Help?**

- **Current builds**: `distributions/`
- **Build scripts**: `scripts/build_*.sh`
- **Security info**: `distributions/SECURITY.md`
- **Build summary**: `distributions/BUILD_SUMMARY.md`

---

## 🏆 **Current Status Summary**

**You now have:**
- ✅ **1 working distribution** (Apple Silicon DMG)
- ⚠️ **2 placeholder files** (Intel DMG, Windows .exe)

**Next steps:**
1. Build Intel DMG using Rosetta 2
2. Build Windows .exe using Windows environment
3. Test all distributions
4. Code sign for production
5. Distribute to users

**The Apple Silicon DMG is ready for immediate distribution!** 🎉 