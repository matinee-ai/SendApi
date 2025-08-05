#!/bin/bash

# Security Setup Script for SendApi Project
# This script installs and configures all security tools

set -e  # Exit on any error

echo "🔒 Setting up security tools for SendApi project..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python found: $PYTHON_VERSION"
    else
        print_error "Python3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip installation..."
    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
    else
        print_error "pip3 is not installed. Please install pip first."
        exit 1
    fi
}

# Upgrade pip
upgrade_pip() {
    print_status "Upgrading pip..."
    python3 -m pip install --upgrade pip
    print_success "pip upgraded"
}

# Install production dependencies
install_prod_deps() {
    print_status "Installing production dependencies..."
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        print_success "Production dependencies installed"
    else
        print_warning "requirements.txt not found, skipping production dependencies"
    fi
}

# Install security dependencies
install_security_deps() {
    print_status "Installing security tools..."
    if [ -f "requirements-security.txt" ]; then
        pip3 install -r requirements-security.txt
        print_success "Security tools installed"
    else
        print_warning "requirements-security.txt not found, installing individual tools..."
        pip3 install safety bandit semgrep pip-audit flake8 black isort mypy pylint pre-commit
        print_success "Security tools installed individually"
    fi
}

# Install pre-commit hooks
install_pre_commit() {
    print_status "Installing pre-commit hooks..."
    if command -v pre-commit &> /dev/null; then
        pre-commit install
        pre-commit install --hook-type commit-msg
        print_success "Pre-commit hooks installed"
    else
        print_warning "pre-commit not found, skipping hook installation"
    fi
}

# Create security reports directory
create_reports_dir() {
    print_status "Creating security reports directory..."
    mkdir -p security-reports
    print_success "Security reports directory created"
}

# Run initial security scan
run_initial_scan() {
    print_status "Running initial security scan..."
    if [ -f "scripts/security_scan.py" ]; then
        python3 scripts/security_scan.py --check all
        print_success "Initial security scan completed"
    else
        print_warning "Security scan script not found, skipping initial scan"
    fi
}

# Create .gitignore entries for security
setup_gitignore() {
    print_status "Setting up .gitignore for security..."
    if [ -f ".gitignore" ]; then
        # Add security-related entries if they don't exist
        if ! grep -q "security-reports/" .gitignore; then
            echo "" >> .gitignore
            echo "# Security reports" >> .gitignore
            echo "security-reports/" >> .gitignore
            echo "*.json" >> .gitignore
            echo "!package.json" >> .gitignore
            echo "!requirements*.json" >> .gitignore
        fi
        print_success ".gitignore updated"
    else
        print_warning ".gitignore not found, creating new one..."
        cat > .gitignore << EOF
# Security reports
security-reports/
*.json
!package.json
!requirements*.json

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
        print_success ".gitignore created"
    fi
}

# Verify installations
verify_installations() {
    print_status "Verifying installations..."
    
    tools=("safety" "bandit" "semgrep" "pip-audit" "flake8" "black" "isort" "mypy" "pylint")
    
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            print_success "$tool is installed"
        else
            print_warning "$tool is not installed"
        fi
    done
}

# Display next steps
show_next_steps() {
    echo ""
    echo "=================================================="
    echo "🎉 Security setup completed!"
    echo "=================================================="
    echo ""
    echo "Next steps:"
    echo "1. Run security scan: make security-scan"
    echo "2. Run code quality checks: make lint"
    echo "3. Format code: make format"
    echo "4. Run tests: make test"
    echo "5. Install pre-commit hooks: make pre-commit"
    echo ""
    echo "Available commands:"
    echo "- make help          - Show all available commands"
    echo "- make security-scan - Run all security checks"
    echo "- make safety        - Check dependencies"
    echo "- make bandit        - Security linting"
    echo "- make semgrep       - Static analysis"
    echo "- make pip-audit     - Package vulnerabilities"
    echo ""
    echo "For more information, see SECURITY.md"
    echo "=================================================="
}

# Main execution
main() {
    echo "Starting security setup..."
    echo ""
    
    check_python
    check_pip
    upgrade_pip
    install_prod_deps
    install_security_deps
    install_pre_commit
    create_reports_dir
    setup_gitignore
    verify_installations
    run_initial_scan
    show_next_steps
}

# Run main function
main "$@" 