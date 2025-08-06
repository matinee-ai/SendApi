#!/bin/bash

echo "Building SendApi for macOS..."
echo

# Define target architecture variables
TARGET_OS_ARCH=""
CONDA_SUBDIR=""
DMG_ARCH_SUFFIX=""

# Parse command line arguments for target architecture
if [ "$#" -eq 1 ]; then
    if [ "$1" == "intel" ]; then
        TARGET_OS_ARCH="x86_64"
        CONDA_SUBDIR="osx-64"
        DMG_ARCH_SUFFIX="-intel"
        echo "Building for Intel (x86_64) architecture..."
    elif [ "$1" == "arm" ]; then
        TARGET_OS_ARCH="arm64"
        CONDA_SUBDIR="osx-arm64"
        DMG_ARCH_SUFFIX="-arm64"
        echo "Building for Apple Silicon (arm64) architecture..."
    else
        echo "Invalid argument. Usage: $0 [intel|arm]"
        exit 1
    fi
else
    echo "No specific architecture provided. Building for the host architecture."
    # Determine host architecture if no argument is provided
    HOST_ARCH=$(uname -m)
    if [ "$HOST_ARCH" == "x86_64" ]; then
        TARGET_OS_ARCH="x86_64"
        CONDA_SUBDIR="osx-64"
        DMG_ARCH_SUFFIX="-intel"
        echo "Host architecture detected: Intel (x86_64)"
    elif [ "$HOST_ARCH" == "arm64" ]; then
        TARGET_OS_ARCH="arm64"
        CONDA_SUBDIR="osx-arm64"
        DMG_ARCH_SUFFIX="-arm64"
        echo "Host architecture detected: Apple Silicon (arm64)"
    else
        echo "Unknown host architecture: $HOST_ARCH. Building without specific architecture target."
        TARGET_OS_ARCH=""
        CONDA_SUBDIR=""
        DMG_ARCH_SUFFIX=""
    fi
fi

# Check if conda or mamba is installed
if command -v mamba &> /dev/null; then
    CONDA_CMD="mamba"
    echo "Using mamba for environment management."
elif command -v conda &> /dev/null; then
    CONDA_CMD="conda"
    echo "Using conda for environment management."
else
    echo "Error: conda or mamba is not installed. Please install Miniconda or Anaconda."
    echo "  https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Define the conda environment name
CONDA_ENV_NAME="sendapi_build_env_${TARGET_OS_ARCH:-host}"

# Clean up previous environment if it exists
if ${CONDA_CMD} env list | grep -q "^${CONDA_ENV_NAME} "; then
    echo "Removing existing conda environment: ${CONDA_ENV_NAME}"
    ${CONDA_CMD} env remove --name ${CONDA_ENV_NAME} --yes
fi

echo "Creating conda environment: ${CONDA_ENV_NAME} with subdir ${CONDA_SUBDIR}..."
if [ -n "${CONDA_SUBDIR}" ]; then
    export CONDA_SUBDIR
fi

${CONDA_CMD} create --name ${CONDA_ENV_NAME} python=3.11 --yes

if [ $? -ne 0 ]; then
    echo "Error: Failed to create conda environment."
    exit 1
fi

# Removed: No explicit activation/deactivation. Using `conda run` instead.

echo "Installing/updating dependencies in conda environment..."
# Use the CONDA_SUBDIR environment variable to ensure correct architecture packages are installed
${CONDA_CMD} run --name ${CONDA_ENV_NAME} pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies in conda environment."
    exit 1
fi

echo
echo "Building application bundle with PyInstaller..."
# PyInstaller will automatically detect the architecture from the active conda environment
${CONDA_CMD} run --name ${CONDA_ENV_NAME} pyinstaller --clean ../sendapi.spec

if [ $? -ne 0 ]; then
    echo "Error: PyInstaller build failed"
    exit 1
fi

echo
echo "Creating DMG file..."

# Create DMG directory structure
mkdir -p dmg_temp
cp -r dist/SendApi.app dmg_temp/

# Define DMG filename based on architecture
DMG_FILE="SendApi${DMG_ARCH_SUFFIX}.dmg"

# Create DMG using hdiutil (macOS built-in tool)
hdiutil create -volname "SendApi" -srcfolder dmg_temp -ov -format UDZO "${DMG_FILE}"

if [ $? -eq 0 ]; then
    echo
    echo "Build completed successfully!"
    echo
    echo "The DMG file can be found at: ${DMG_FILE}"
    echo
    echo "To install the application:"
    echo "1. Double-click ${DMG_FILE}"
    echo "2. Drag SendApi.app to Applications folder"
    echo "3. Launch from Applications"
    echo
else
    echo "Error: DMG creation failed"
    exit 1
fi

# Clean up the conda environment
${CONDA_CMD} env remove --name ${CONDA_ENV_NAME} --yes

# Clean up build artifacts
rm -rf dmg_temp
rm -rf build
rm -rf dist

echo "Cleanup completed." 