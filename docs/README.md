# Bridge_GAD Documentation System

This directory contains the automated documentation generation system for Bridge_GAD.

## 📁 Structure

```
docs/
├── manual_template.md     # Markdown template for the user manual
├── build_manual.py        # Python script to generate the manual
├── Bridge_GAD_User_Manual.md  # Generated markdown manual
└── Bridge_GAD_User_Manual.pdf # Generated PDF manual (when dependencies available)
```

## 📖 User Manual Generation

### Automatic Generation

Run the batch script to generate the user manual:

```cmd
build_manual.bat
```

### Manual Generation

You can also run the Python script directly:

```cmd
python docs\build_manual.py
```

## 🧩 Dependencies

For full functionality, the following dependencies are required:

1. **pypandoc** - For PDF generation from markdown
   ```bash
   pip install pypandoc
   ```

2. **LaTeX distribution** - For PDF rendering (e.g., MiKTeX, TeX Live)

If these dependencies are not available, the system will generate a markdown version of the manual.

## 📝 Template Customization

The [manual_template.md](file:///c:/Users/Rajkumar/Bridge_GAD_Yogendra_Borse-main/docs/manual_template.md) file contains the base structure of the user manual. 
The build script automatically replaces the `VERSION` placeholder with the current package version.

## 🔄 Process

1. The script reads [manual_template.md](file:///c:/Users/Rajkumar/Bridge_GAD_Yogendra_Borse-main/docs/manual_template.md)
2. Replaces `VERSION` with the current package version from `src/bridge_gad/__init__.py`
3. Generates [Bridge_GAD_User_Manual.md](file:///c:/Users/Rajkumar/Bridge_GAD_Yogendra_Borse-main/docs/Bridge_GAD_User_Manual.md) (always)
4. Generates [Bridge_GAD_User_Manual.pdf](file:///c:/Users/Rajkumar/Bridge_GAD_Yogendra_Borse-main/docs/Bridge_GAD_User_Manual.pdf) (when dependencies available)

## 📤 Output

- **Markdown Manual**: Always generated, suitable for GitHub viewing
- **PDF Manual**: Generated when pypandoc and LaTeX are available, suitable for printing and distribution

## 🛠️ Maintenance

To update the manual content:
1. Edit [manual_template.md](file:///c:/Users/Rajkumar/Bridge_GAD_Yogendra_Borse-main/docs/manual_template.md)
2. Run the build script to regenerate the manuals
3. Commit the changes