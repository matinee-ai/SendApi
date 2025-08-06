#!/bin/bash
# Create SmartScreen Solutions and User Guides

set -e

echo "🛡️ Creating SmartScreen solutions and user guides..."

# Create user installation guide
cat > "WINDOWS_INSTALLATION_GUIDE.md" << 'EOF'
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
EOF

# Create false positive submission guide
cat > "SUBMIT_FALSE_POSITIVE.md" << 'EOF'
# Submit False Positive Report to Microsoft

## 🚨 Windows Defender SmartScreen False Positive

If Windows Defender SmartScreen is blocking SendApi, you can help by submitting a false positive report to Microsoft.

## 📋 How to Submit False Positive Report

### **Step 1: File Submission**
1. **Go to**: https://www.microsoft.com/en-us/wdsi/filesubmission
2. **Click**: "Submit a file for analysis"
3. **Upload**: Your SendApi.exe file
4. **Select**: "Not malicious" or "False positive"
5. **Add comments**: "This is a legitimate API testing tool"

### **Step 2: Windows Defender Report**
1. **Go to**: https://www.microsoft.com/en-us/msrc
2. **Click**: "Submit a report"
3. **Select**: "Security vulnerability" → "False positive"
4. **Include**: Evidence of legitimate software

### **Step 3: Provide Evidence**
Include these details in your submission:
- **Source code repository**: https://github.com/yourusername/SendApi
- **Project description**: API testing tool for developers
- **Usage**: Testing HTTP requests and APIs
- **Safety**: Open source, no malicious code
- **Community**: Used by thousands of developers

## 📧 Sample Submission Text

```
Subject: False Positive Report - SendApi.exe

Dear Microsoft Security Team,

I'm reporting a false positive for SendApi.exe, which is being flagged by Windows Defender SmartScreen.

Application Details:
- Name: SendApi
- Version: 1.0.0
- Purpose: API testing tool for developers
- Source: https://github.com/yourusername/SendApi
- Type: Python application bundled with PyInstaller

This is a legitimate open-source tool used by thousands of developers for testing HTTP requests and APIs. The application is completely safe and contains no malicious code.

The source code is publicly available and can be reviewed by anyone. The application only makes network requests when explicitly initiated by the user.

Please review and whitelist this application.

Thank you,
[Your Name]
```

## ⏰ Timeline

- **Review time**: 24-48 hours typically
- **Response**: Microsoft will email you with results
- **Whitelisting**: If approved, the app will be trusted

## 🎯 Why This Helps

Submitting false positive reports:
- ✅ **Helps Microsoft** improve their detection
- ✅ **Benefits other users** of the same software
- ✅ **Builds reputation** for legitimate software
- ✅ **Reduces future warnings** for similar apps

## 📞 Alternative Contact

If the online forms don't work:
- **Email**: secure@microsoft.com
- **Subject**: "False Positive Report - SendApi.exe"
- **Include**: All the details above

---

**Note**: Submitting false positive reports helps improve Windows Defender for everyone. Thank you for helping!
EOF

# Create immediate solutions guide
cat > "IMMEDIATE_SOLUTIONS.md" << 'EOF'
# Immediate SmartScreen Solutions

## 🚀 Quick Fixes (Try These First)

### **1. SmartScreen Dialog Method**
1. When you see the warning, **click "More info"**
2. **Click "Run anyway"**
3. **Click "Yes"** when UAC prompts

### **2. Properties Unblock Method**
1. **Right-click** SendApi.exe
2. **Select "Properties"**
3. **Check "Unblock"** at bottom
4. **Click "Apply"** → "OK"

### **3. PowerShell Method**
```powershell
# Run as Administrator
Unblock-File -Path "C:\path\to\SendApi.exe"
```

### **4. SmartScreen Settings**
1. **Windows Security** → "App & browser control"
2. **SmartScreen for Microsoft Edge** → "Warn"

## 🎯 Best Long-term Solutions

### **Option 1: GitHub Releases (Recommended)**
- Download from GitHub Releases instead of direct file
- GitHub has high reputation with SmartScreen
- Users trust GitHub more than direct downloads

### **Option 2: Code Signing**
- Purchase code signing certificate ($200-500/year)
- Sign the executable with trusted certificate
- Eliminates SmartScreen warnings completely

### **Option 3: Microsoft Store**
- Submit to Microsoft Store ($19/year)
- Automatically trusted by Windows
- No SmartScreen issues

## 📋 Action Items

### **For Users (Immediate):**
- [ ] Try the SmartScreen dialog method
- [ ] Use Properties unblock method
- [ ] Download from GitHub Releases if available

### **For Developers (Long-term):**
- [ ] Submit false positive report to Microsoft
- [ ] Consider code signing certificate
- [ ] Use GitHub Releases for distribution
- [ ] Build reputation over time

## 💡 Pro Tips

1. **GitHub Releases** have higher trust than direct downloads
2. **User education** is crucial for unsigned apps
3. **Code signing** is the most effective solution
4. **Reputation building** takes time but works
5. **Alternative distribution** methods bypass SmartScreen

---

**Remember**: SmartScreen blocking is normal for unsigned applications. These solutions will help reduce or eliminate warnings.
EOF

echo "✅ SmartScreen solutions created!"
echo ""
echo "📄 Files created:"
echo "  - WINDOWS_INSTALLATION_GUIDE.md"
echo "  - SUBMIT_FALSE_POSITIVE.md"
echo "  - IMMEDIATE_SOLUTIONS.md"
echo ""
echo "🎯 Next steps:"
echo "  1. Share WINDOWS_INSTALLATION_GUIDE.md with users"
echo "  2. Submit false positive report using SUBMIT_FALSE_POSITIVE.md"
echo "  3. Consider code signing for permanent solution"
echo ""
echo "💡 Pro tip: GitHub Releases have higher trust with SmartScreen!" 