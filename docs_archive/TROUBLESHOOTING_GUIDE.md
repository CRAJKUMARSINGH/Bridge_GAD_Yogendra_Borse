# 🐛 Troubleshooting Guide - Bridge GAD Generator

## Quick Reference

| Error | Solution | Time |
|-------|----------|------|
| Module not found | `pip install -r requirements-streamlit.txt` | 30s |
| Port already in use | See Port Conflicts section | 1m |
| File upload fails | Check Excel format | 5m |
| DXF won't generate | Verify parameters | 2m |
| Performance slow | Clear cache, restart | 1m |

---

## Python Installation Issues

### Problem: "Python not found"
```bash
# Check Python version
python3 --version

# Should show: Python 3.9+
```

**Solution**:
- Download Python 3.9+ from python.org
- Or use: `brew install python3` (Mac) or `apt install python3` (Linux)

---

### Problem: "pip not found"
```bash
# Try this instead
python3 -m pip --version
```

**Solution**:
```bash
# Install pip
python3 -m ensurepip --upgrade
```

---

## Dependency Issues

### Problem: "ModuleNotFoundError: No module named 'ezdxf'"
```bash
pip install ezdxf==1.4.3
```

### Problem: "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install streamlit==1.32.0
```

### Problem: "ModuleNotFoundError: No module named 'pandas'"
```bash
pip install pandas openpyxl
```

### Problem: "ModuleNotFoundError: No module named 'fastapi'"
```bash
pip install fastapi uvicorn
```

### Solution: Clean Install
If individual installs don't work:
```bash
# Clear pip cache
pip cache purge

# Uninstall all
pip uninstall -y ezdxf streamlit pandas fastapi

# Fresh install from requirements
pip install -r requirements-streamlit.txt
```

---

## Port Conflicts

### Problem: "Error: Port 8501 already in use"

**Mac/Linux**:
```bash
# Find process using port
lsof -i :8501

# Kill the process
lsof -i :8501 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

**Windows**:
```bash
# Find process using port
netstat -ano | findstr :8501

# Kill the process (replace PID with actual number)
taskkill /PID 12345 /F
```

**Or use different port**:
```bash
streamlit run streamlit_app.py --server.port 8502
```

---

### Problem: "Vercel port 5000 already in use"

```bash
# Find and kill process
lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Then restart
python3 main_server.py
```

---

## File Upload Issues

### Problem: "Excel file upload fails"

**Check Excel Format**:
- Ensure file has 3 columns: Value, Variable, Description
- Column headers should be in Row 1
- All values should be numeric (except Variable/Description)

**Solution**:
```python
# Download template from UI and use it as reference
# Or create Excel with exact structure:
#
# Column A (Value):      186
# Column B (Variable):   SCALE1
# Column C (Description): Horizontal Scale
```

### Problem: "File too large (>50MB)"
- Streamlit has 50MB upload limit
- Your Excel should be <1MB
- For batch processing, split into multiple files

---

## Drawing Generation Issues

### Problem: "Drawing generation fails silently"

**Check the logs**:
```bash
# If using Streamlit
# Check the terminal output for error messages

# If using FastAPI
python3 main_server.py
# Errors will appear in console
```

**Common causes**:
- Invalid Excel parameters (non-numeric values where numbers expected)
- Missing required parameters (check column B names match exactly)
- File permissions (can't write to output directory)

**Solution**:
1. Verify Excel has all required parameters
2. Check parameter names match exactly (case-sensitive)
3. Ensure all numeric fields have valid numbers
4. Try with template Excel file first

### Problem: "DXF file won't open in AutoCAD"

**Verify AutoCAD compatibility**:
- Make sure you selected correct version (R2006 or R2010)
- Try opening in free viewer: Autodesk Design Review
- Check file size (should be 50-500KB)

**Solution**:
```python
# Try different AutoCAD version
# In Streamlit UI, change "AutoCAD Version" selector
# Try: R2006 (most compatible)
```

---

## Performance Issues

### Problem: "Streamlit is slow / takes 30+ seconds to start"

**Solution**:
```bash
# Clear Streamlit cache
streamlit cache clear

# Clear system pip cache
pip cache purge

# Restart from fresh
streamlit run streamlit_app.py
```

### Problem: "Drawing generation takes 10+ seconds"

**Check what's slow**:
- First run: May take longer (module loading)
- Subsequent runs: Should be 1-2 seconds
- If consistently slow: Check system resources

**Solution**:
```bash
# Check system memory
# If <2GB available, close other apps

# Monitor with top/Activity Monitor
# Look for python3 process using 100%+ CPU
```

### Problem: "Memory usage keeps growing"

**Solution**:
```bash
# Restart Streamlit (clears in-memory cache)
streamlit cache clear

# Stop and restart
Ctrl+C (in terminal)
streamlit run streamlit_app.py
```

---

## AutoCAD Compatibility

### Problem: "DXF opens but drawings look wrong"

**Possible causes**:
1. Wrong AutoCAD version selected
2. Missing DXF layers or styles
3. Scale factors not applied correctly

**Solution**:
1. Try different version: R2006 (most compatible)
2. Check in AutoCAD: View → Zoom → Extents
3. If elements missing: Verify drawing generated correctly

### Problem: "Cannot edit drawing in AutoCAD"

**Check permissions**:
```bash
# Make sure file isn't read-only
chmod 644 bridge_drawing.dxf  # Mac/Linux
```

**Try opening as new drawing**:
- AutoCAD → New → Open file
- Select your DXF
- Should be fully editable

---

## API Issues (FastAPI)

### Problem: "POST request fails with 400 error"

**Check request format**:
```bash
# Example working request
curl -X POST -F "excel_file=@bridge_data.xlsx" \
  http://localhost:5000/predict?output_format=dxf
```

**Solution**:
- Ensure file parameter is named "excel_file"
- File must be valid Excel format
- output_format must be: dxf, pdf, png, or svg

### Problem: "API returns 500 error"

**Check logs**:
```bash
# Terminal will show error
python3 main_server.py
# Look for error traceback
```

**Common causes**:
- Excel file format invalid
- Missing parameters
- Insufficient disk space

---

## Deployment Issues

### Problem: "Streamlit Cloud deployment fails"

**Check**:
- [ ] requirements-streamlit.txt exists
- [ ] Git repo is public
- [ ] All changes committed
- [ ] No .env file with secrets in repo
- [ ] Python version specified (add runtime.txt)

**Create runtime.txt**:
```
python-3.11
```

### Problem: "Vercel deployment fails"

**Check**:
- [ ] vercel.json exists and is valid JSON
- [ ] api/ folder exists
- [ ] Python 3.11 available
- [ ] requirements.txt is complete

---

## Memory/Storage Issues

### Problem: "Out of disk space"

**Solution**:
```bash
# Find large files
du -h -d 1

# Clean generated drawings
rm -rf *.dxf *.pdf *.png

# Clear cache directories
rm -rf __pycache__ .streamlit .vercel
```

### Problem: "Not enough memory to process file"

**Solution**:
- Limit to <50MB input files
- Process one file at a time
- Try on machine with more RAM
- Restart Streamlit to clear memory

---

## Git/GitHub Issues

### Problem: "Permission denied (publickey)"

**Solution**:
```bash
# Generate SSH key
ssh-keygen -t ed25519

# Add to GitHub
# Settings → SSH Keys → New SSH key
# Paste public key (~/.ssh/id_ed25519.pub)
```

### Problem: "Git remote fails after initial push"

**Solution**:
```bash
# Check remote is set correctly
git remote -v

# Should show:
# origin  https://github.com/YOU/bridge-gad.git

# If wrong, update:
git remote set-url origin https://github.com/YOU/bridge-gad.git
```

---

## Browser/UI Issues

### Problem: "Streamlit UI not loading / blank page"

**Solution**:
```bash
# Hard refresh browser
Cmd+Shift+R (Mac)
Ctrl+Shift+R (Windows/Linux)

# Or restart Streamlit
Ctrl+C
streamlit run streamlit_app.py
```

### Problem: "Can't download files from Streamlit"

**Check**:
- Browser pop-up blocker not blocking
- Sufficient disk space
- Browser not in private/incognito mode

**Solution**:
```bash
# Temporarily disable blockers
# Or try different browser (Chrome, Firefox, Safari)
```

---

## Email/Support

**Not Working?**

1. **Check logs** - Run with verbose output:
   ```bash
   streamlit run streamlit_app.py --logger.level=debug
   ```

2. **Search existing issues** - GitHub Issues may have solution

3. **Contact Support**:
   - Email: crajkumarsingh@hotmail.com
   - Include: Error message, Python version, OS
   - Attach: Screenshot or error log

---

## Quick Fix Checklist

When something breaks, try these in order:

1. **Restart**
   ```bash
   Ctrl+C (stop)
   streamlit run streamlit_app.py
   ```

2. **Clear Cache**
   ```bash
   streamlit cache clear
   pip cache purge
   ```

3. **Reinstall Requirements**
   ```bash
   pip install -r requirements-streamlit.txt
   ```

4. **Check Python**
   ```bash
   python3 --version  # Should be 3.9+
   ```

5. **Check Logs**
   - Look in terminal for error messages
   - Check browser console (F12)

6. **Search Documentation**
   - Check README.md
   - Check QUICK_START.md
   - Check this file

7. **Contact Support**
   - Email with error details
   - Include setup info (OS, Python, etc.)

---

**Last Updated**: November 28, 2025  
**Status**: ✅ Comprehensive Guide
