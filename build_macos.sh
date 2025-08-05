#!/bin/bash

echo "Building SendApi for macOS..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed"
    exit 1
fi

echo "Installing/updating dependencies..."
pip3 install -r requirements.txt

echo
echo "Building application bundle with PyInstaller..."
pyinstaller --clean sendapi.spec

if [ $? -ne 0 ]; then
    echo "Error: PyInstaller build failed"
    exit 1
fi

echo
echo "Creating DMG file..."

# Create DMG directory structure
mkdir -p dmg_temp
cp -r dist/SendApi.app dmg_temp/

# Create DMG using hdiutil (macOS built-in tool)
hdiutil create -volname "SendApi" -srcfolder dmg_temp -ov -format UDZO SendApi.dmg

if [ $? -eq 0 ]; then
    echo
    echo "Build completed successfully!"
    echo
    echo "The DMG file can be found at: SendApi.dmg"
    echo
    echo "To install the application:"
    echo "1. Double-click SendApi.dmg"
    echo "2. Drag SendApi.app to Applications folder"
    echo "3. Launch from Applications"
    echo
else
    echo "Error: DMG creation failed"
    exit 1
fi

# Clean up
rm -rf dmg_temp
rm -rf build
rm -rf dist

echo "Cleanup completed." 