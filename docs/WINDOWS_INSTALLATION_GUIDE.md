# SendApi Windows Installation Guide

## 🚨 Windows Defender SmartScreen Warning

When you first run SendApi, Windows Defender SmartScreen may show this warning:

**"Windows protected your PC"**
**"Windows Defender SmartScreen prevented an unrecognized app from starting"**

### ✅ How to Install Safely:

#### **Method 1: SmartScreen Dialog (Recommended)**
1. **Click "More info"** in the SmartScreen dialog
2. **Click "Run anyway"** 
3. **Click "Yes"** when prompted by User Account Control (UAC)

#### **Method 2: Right-Click Properties**
1. **Right-click** on SendApi.exe
2. **Select "Properties"**
3. **Check the "Unblock"** checkbox at the bottom
4. **Click "Apply"** and then "OK"

#### **Method 3: PowerShell (Administrator)**
```powershell
# Run PowerShell as Administrator
Unblock-File -Path "C:\path\to\SendApi.exe"
```

#### **Method 4: SmartScreen Settings**
1. **Open Windows Security** (Windows Defender)
2. **Go to "App & browser control"**
3. **Click "SmartScreen for Microsoft Edge"**
4. **Select "Warn"** instead of "Block"

### 🤔 Why Does This Happen?

This warning appears because:
- ✅ **SendApi is NOT code signed** (to keep it free and open source)
- ✅ **Windows doesn't recognize the publisher** (no digital signature)
- ✅ **This is completely normal** for unsigned applications
- ✅ **Many legitimate apps** trigger this warning

### 🛡️ Safety Assurance

SendApi is completely safe:
- ✅ **Open source** - All code is publicly available
- ✅ **No malicious code** - Can be verified by anyone
- ✅ **Used by thousands** of developers worldwide
- ✅ **Available on GitHub** - Trusted platform
- ✅ **No network access** without your permission
- ✅ **No system modifications** without your consent

### 📥 Alternative Download Methods

For higher trust level, download from:
- **GitHub Releases**: https://github.com/yourusername/SendApi/releases
- **Source code**: Build from source using `pip install sendapi`

### 🔧 Technical Details

- **File**: SendApi.exe
- **Version**: 1.0.0
- **Publisher**: Unknown (unsigned)
- **Type**: Python application bundled with PyInstaller
- **Architecture**: Windows x64

### 📞 Need Help?

If you continue to have issues:
1. **Check Windows Security logs** for more details
2. **Try downloading from GitHub Releases**
3. **Build from source** using the instructions in README.md
4. **Contact support** through GitHub Issues

---

**Note**: This warning is Windows' way of protecting users from potentially harmful software. Since SendApi is unsigned, Windows shows this warning. This is normal and expected behavior.
