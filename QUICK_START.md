🚀 QUICK START GUIDE - Bridge GAD Generator v2.1

## ⚡ One-Command Deploy to Streamlit Cloud

### Option 1: Use Deployment Script (Bash/Mac/Linux)
```bash
./deploy-streamlit.sh
```

### Option 2: Manual Streamlit Cloud Deploy
```bash
git add .
git commit -m "chore: deploy to streamlit cloud"
git push origin main
```
Then visit [Streamlit Cloud](https://streamlit.io/cloud) and connect your GitHub repo.

### Option 3: Deploy to Vercel
```bash
vercel
# Follow prompts → Select "Python" → Deploy
```

---

## 🛠️ Local Development

### Start Development Server
```bash
streamlit run streamlit_app.py
```
Visit: http://localhost:8501

### Or Start FastAPI Server
```bash
python3 main_server.py
```
Visit: http://localhost:5000 (API docs at /docs)

---

## 📦 Installation

### Prerequisites
- Python 3.9+
- pip package manager

### Quick Install
```bash
pip install -r requirements-streamlit.txt
streamlit run streamlit_app.py
```

---

## 🎯 Quick Commands Reference

| Command | Purpose | Time |
|---------|---------|------|
| `streamlit run streamlit_app.py` | Start UI | 5 sec |
| `python3 main_server.py` | Start API | 2 sec |
| `pip install -r requirements-streamlit.txt` | Install deps | 30 sec |
| `git push origin main` | Deploy (auto) | 1 min |
| `vercel` | Deploy to Vercel | 2 min |

---

## 📊 What's Included

### Core Features
- ✅ Bridge drawing generation (1-2 seconds)
- ✅ 4-sheet detailed package (pier, abutment, plan, section)
- ✅ Quality checker (IRC/IS standards)
- ✅ 3D visualization
- ✅ Design comparison tool
- ✅ 5 smart templates
- ✅ Multi-format export (DXF, PDF, PNG, SVG)

### Tech Stack
- **Frontend**: Streamlit (instant UI)
- **Backend**: FastAPI (async, fast)
- **Drawing**: ezdxf (native DXF)
- **Graphics**: Matplotlib, ReportLab
- **Deployment**: Streamlit Cloud, Vercel, Docker

---

## 🧹 Maintenance

### Clean Cache & Build
```bash
pip cache purge
rm -rf __pycache__ .streamlit/
```

### Full Fresh Install
```bash
pip cache purge
pip uninstall -y streamlit ezdxf pandas
pip install -r requirements-streamlit.txt
```

### Type Check (Python)
```bash
python3 -m py_compile src/bridge_gad/*.py
```

---

## 🐛 Troubleshooting

### Error: "No module named 'ezdxf'"
```bash
pip install ezdxf==1.4.3
```

### Error: "Streamlit not found"
```bash
pip install streamlit==1.32.0
```

### Error: "Port 8501 already in use"
```bash
# Mac/Linux
lsof -i :8501 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

### Error: "pandas/openpyxl not found"
```bash
pip install pandas openpyxl
```

### Memory/Performance Issues
```bash
# Restart and clear cache
pip cache purge
streamlit cache clear
streamlit run streamlit_app.py
```

---

## 📁 Project Structure

```
bridge-gad/
├── streamlit_app.py              # Web UI (6 tabs)
├── main_server.py                # FastAPI server
├── deploy-streamlit.sh            # Deploy script
├── deploy-vercel.sh               # Vercel deploy
├── src/bridge_gad/
│   ├── bridge_generator.py        # Core drawing engine
│   ├── multi_sheet_generator.py   # 4-sheet package ⭐
│   ├── advanced_features.py       # Templates, Quality, 3D, Compare
│   ├── api.py                     # REST API routes
│   └── [15+ modules]              # Supporting code
├── requirements-streamlit.txt     # Dependencies
└── README.md                      # Full documentation
```

---

## 🔗 Important Files

| File | Purpose |
|------|---------|
| `streamlit_app.py` | Main web UI |
| `main_server.py` | FastAPI backend |
| `requirements-streamlit.txt` | Python dependencies |
| `QUICK_START.md` | This file |
| `DEPLOYMENT_GUIDE.md` | Full deployment guide |
| `MULTI_SHEET_FEATURE.md` | 4-sheet feature details |
| `EXPERT_COMPETITIVE_ANALYSIS.md` | Technical comparison |

---

## ✅ Pre-Deployment Checklist

- [ ] `pip install -r requirements-streamlit.txt` succeeds
- [ ] `streamlit run streamlit_app.py` starts without errors
- [ ] Can upload Excel file and generate drawing
- [ ] Downloaded DXF file opens in AutoCAD
- [ ] 4-sheet package generates successfully
- [ ] No console errors or warnings

---

## 🌐 After Deployment

### Streamlit Cloud
1. Visit your Streamlit Cloud dashboard
2. Your app is live at: `https://<username>-bridge-gad-<hash>.streamlit.app`
3. Share the URL with team
4. Monitor activity in dashboard

### Vercel
1. Visit [vercel.com](https://vercel.com/dashboard)
2. Your app is live at: `https://bridge-gad.vercel.app`
3. Download CLI: `npm i -g vercel`
4. Deploy updates: `vercel --prod`

### Docker
```bash
docker build -t bridge-gad .
docker run -p 8501:8501 bridge-gad
```

---

## 📞 Support & Help

**Need Help?**
- Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions
- See [QUICK_START.md](QUICK_START.md) (this file) for quick commands
- Review troubleshooting section above

**Report Issues:**
- Create GitHub issue with error message
- Include Python version and OS
- Attach error screenshot

---

## 🎁 Tips & Tricks

### Faster Development
```bash
# Terminal 1: Run Streamlit
streamlit run streamlit_app.py

# Terminal 2: Watch for changes (auto-reload)
# Changes to .py files reload automatically
```

### Generate Test Drawings
- Use template Excel files in SAMPLE_INPUT_FILES/
- Or download template from UI
- Test all export formats

### Monitor Performance
- Streamlit metrics available in sidebar
- FastAPI docs at http://localhost:5000/docs
- Check response times in terminal

---

**Version**: 2.1
**Last Updated**: November 28, 2025
**Status**: ✅ Production Ready

🌉 Bridge drawings in seconds. Professional quality. Ready to submit.
