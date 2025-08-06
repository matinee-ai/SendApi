# Troubleshooting Guide - API Tester

This guide helps you resolve common issues when running the API Tester application.

## 🐛 Common Issues and Solutions

### Python Version Compatibility

**Issue**: PySide6 compatibility with Python 3.13
```
ImportError: dlopen(...): Symbol not found: __Z13lcPermissionsv
```

**Solution**: 
- The application now uses PySide6 6.9.1 which supports Python 3.13
- If you still encounter issues, try using Python 3.11 or 3.12:
  ```bash
  # Install Python 3.11 or 3.12
  brew install python@3.11  # macOS
  # or
  python3.11 -m pip install -r requirements.txt
  ```

### Installation Issues

**Issue**: `pip install` fails
```
ERROR: Could not find a version that satisfies the requirement PySide6==6.9.1
```

**Solutions**:
1. **Update pip**:
   ```bash
   python3 -m pip install --upgrade pip
   ```

2. **Clear pip cache**:
   ```bash
   python3 -m pip cache purge
   ```

3. **Install with verbose output**:
   ```bash
   python3 -m pip install -r requirements.txt -v
   ```

4. **Use alternative installation**:
   ```bash
   python3 -m pip install PySide6 requests python-dotenv jsonschema pygments
   ```

### Import Errors

**Issue**: `ModuleNotFoundError: No module named 'PySide6'`
```
ModuleNotFoundError: No module named 'PySide6'
```

**Solutions**:
1. **Check Python version**:
   ```bash
   python3 --version
   # Should be 3.8 or higher
   ```

2. **Reinstall dependencies**:
   ```bash
   python3 -m pip uninstall PySide6 -y
   python3 -m pip install -r requirements.txt
   ```

3. **Check virtual environment**:
   ```bash
   # If using virtual environment
   source .venv/bin/activate  # macOS/Linux
   # or
   .venv\Scripts\activate     # Windows
   ```

### Application Won't Start

**Issue**: Application crashes on startup
```
Traceback (most recent call last):
  File "main.py", line X, in module Y
```

**Solutions**:
1. **Check dependencies**:
   ```bash
   python3 -c "import PySide6; print('PySide6 OK')"
   python3 -c "import requests; print('Requests OK')"
   ```

2. **Run with debug output**:
   ```bash
   python3 -u main.py
   ```

3. **Check file permissions**:
   ```bash
   chmod +x main.py
   chmod +x run.sh  # macOS/Linux
   ```

### GUI Issues

**Issue**: Application window doesn't appear
- **Solution**: Check if you're running in a headless environment
- **Solution**: Ensure you have a display server running (X11, Wayland, etc.)

**Issue**: Application appears but is unresponsive
- **Solution**: Check system resources (CPU, memory)
- **Solution**: Restart the application

### Network Issues

**Issue**: Requests fail with connection errors
```
requests.exceptions.ConnectionError: [Errno 61] Connection refused
```

**Solutions**:
1. **Check internet connection**
2. **Verify URL is correct**
3. **Check firewall settings**
4. **Try with different URLs**:
   ```
   https://jsonplaceholder.typicode.com/users/1
   https://httpbin.org/get
   ```

### Data Persistence Issues

**Issue**: Collections or environments not saving
```
PermissionError: [Errno 13] Permission denied
```

**Solutions**:
1. **Check file permissions**:
   ```bash
   ls -la collections.json environments.json
   ```

2. **Check disk space**:
   ```bash
   df -h
   ```

3. **Run with write permissions**:
   ```bash
   chmod 755 .
   ```

### Performance Issues

**Issue**: Application is slow or unresponsive
- **Solution**: Close other applications to free memory
- **Solution**: Restart the application
- **Solution**: Check system resources

**Issue**: Large collections cause lag
- **Solution**: Split large collections into smaller ones
- **Solution**: Use folders to organize requests

## 🔧 Platform-Specific Issues

### macOS Issues

**Issue**: "App is damaged" error
```
"API Tester" is damaged and can't be opened
```

**Solution**:
```bash
xattr -cr /path/to/application
```

**Issue**: Permission denied on first run
```
Permission denied: run.sh
```

**Solution**:
```bash
chmod +x run.sh
```

### Windows Issues

**Issue**: Python not found
```
'python' is not recognized as an internal or external command
```

**Solutions**:
1. **Add Python to PATH**
2. **Use full path**:
   ```cmd
   C:\Python311\python.exe main.py
   ```

**Issue**: PySide6 installation fails
```
Microsoft Visual C++ 14.0 is required
```

**Solution**: Install Visual Studio Build Tools or use pre-compiled wheels

### Linux Issues

**Issue**: Missing Qt dependencies
```
ImportError: libQt6Core.so.6: cannot open shared object file
```

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install python3-pyqt6

# Fedora
sudo dnf install python3-pyside6

# Arch
sudo pacman -S python-pyside6
```

## 🆘 Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Try the solutions above**
3. **Check the application logs**
4. **Verify your system meets requirements**

### System Requirements

- **Python**: 3.8 or higher
- **Operating System**: macOS 10.14+, Windows 10+, Linux
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 100MB free space
- **Display**: 1024x768 minimum resolution

### Debug Information

When reporting issues, include:
- Python version: `python3 --version`
- Operating system: `uname -a` (Linux/macOS) or `systeminfo` (Windows)
- PySide6 version: `python3 -c "import PySide6; print(PySide6.__version__)"`
- Error message: Full traceback
- Steps to reproduce: Detailed steps

### Contact Information

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check README.md and other docs
- **Community**: Join discussions and get help

## 🔄 Alternative Solutions

### If PySide6 Still Doesn't Work

1. **Use PyQt6** (older Python versions):
   ```bash
   pip install PyQt6==6.6.1
   # Update imports in code from PySide6 to PyQt6
   ```

2. **Use tkinter** (built-in):
   - Modify the application to use tkinter instead
   - Less feature-rich but more compatible

3. **Use web-based alternative**:
   - Consider using Postman or Insomnia
   - Or build a web-based version with Flask/Django

### Performance Alternatives

1. **Use command-line tools**:
   ```bash
   curl -X GET https://api.example.com/users
   ```

2. **Use Python requests directly**:
   ```python
   import requests
   response = requests.get('https://api.example.com/users')
   print(response.json())
   ```

## 📝 Logging and Debugging

### Enable Debug Mode

Add this to the beginning of `main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Application Logs

The application creates log files in the current directory:
- `app.log`: Application logs
- `error.log`: Error logs

### Common Debug Commands

```bash
# Check Python environment
python3 -c "import sys; print(sys.path)"

# Check installed packages
python3 -m pip list

# Test imports
python3 -c "import PySide6; print('PySide6 OK')"

# Run with verbose output
python3 -v main.py
``` 