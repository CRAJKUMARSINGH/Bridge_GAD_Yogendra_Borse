# Bridge GAD Generator - Deployment Guide

## 🚀 Quick Deploy Options

### Option 1: Streamlit Cloud (Easiest)

```bash
# 1. Push to GitHub
git add .
git commit -m "Add Streamlit UI"
git push origin main

# 2. Visit https://streamlit.io/cloud
# 3. Click "New App" → Connect to your GitHub repo
# 4. Select: Repository: your-repo, Branch: main, Main file path: streamlit_app.py
# 5. Deploy! 🚀
```

**URL will be**: `https://<username>-bridge-gad-<hash>.streamlit.app`

### Option 2: Vercel Deployment

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy
vercel

# 3. Follow prompts:
#    - Which scope? (your account)
#    - Link to existing project? (no)
#    - Project name? (bridge-gad)
#    - Directory? (.)
#    - Framework? (Other)

# Your app will be live at: https://bridge-gad.vercel.app
```

### Option 3: Docker + Cloud Run

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8080"]
```

Deploy to Google Cloud Run:
```bash
gcloud run deploy bridge-gad \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Option 4: PythonAnywhere (Simple)

1. Visit https://www.pythonanywhere.com
2. Create account (free or paid)
3. Upload files via Web interface
4. Configure WSGI file
5. Start web app

## Environment Variables

For Vercel/Cloud deployment, set:

```bash
PYTHONUNBUFFERED=1
STREAMLIT_SERVER_HEADLESS=true
```

## Local Testing

```bash
# Test Streamlit UI
streamlit run streamlit_app.py

# Test FastAPI
python3 main_server.py

# Visit:
# - Streamlit: http://localhost:8501
# - FastAPI: http://localhost:5000
# - API Docs: http://localhost:5000/docs
```

## File Structure for Deployment

```
bridge-gad/
├── streamlit_app.py          # Streamlit UI
├── main_server.py            # FastAPI server
├── requirements.txt          # Main dependencies
├── requirements-streamlit.txt # Streamlit dependencies
├── vercel.json               # Vercel config
├── api/
│   └── generate.py           # Serverless function
├── src/
│   └── bridge_gad/           # Core library
└── .gitignore                # Exclude large files
```

## API Endpoint Examples

### Generate Drawing (Streamlit)
```python
import requests

excel_file = open('bridge_data.xlsx', 'rb')
files = {'excel_file': excel_file}
response = requests.post('http://localhost:5000/predict', files=files)
```

### Generate Drawing (Vercel)
```python
import base64
import requests

with open('bridge_data.xlsx', 'rb') as f:
    excel_data = base64.b64encode(f.read()).decode('utf-8')

response = requests.post('https://bridge-gad.vercel.app/api/generate', json={
    'excel_data': excel_data,
    'acad_version': 'R2006',
    'output_format': 'dxf'
})
```

## Performance Tips

1. **Cache drawings** - Store generated files temporarily
2. **Use CDN** - Serve static files from CDN
3. **Lazy loading** - Load bridge_gad module only when needed
4. **Compression** - Gzip response bodies
5. **Rate limiting** - Prevent abuse

## Monitoring

### Streamlit Cloud
- View logs: Dashboard → App → View logs
- Monitor usage: Dashboard → Usage stats

### Vercel
- View logs: Deployments → Logs
- Monitor performance: Analytics → Performance

### Google Cloud Run
```bash
gcloud run logs read bridge-gad --limit 50
```

## Troubleshooting

### Port already in use
```bash
# Find process using port 8501
lsof -i :8501
# Kill it
kill -9 <PID>
```

### Missing dependencies
```bash
pip install -r requirements-streamlit.txt
```

### Streamlit caching issues
```bash
streamlit cache clear
```

### Large file uploads failing
- Increase timeout: `streamlit run app.py --client.maxUploadSize 200`
- Use chunked uploads for files > 200MB

## Scaling

- **Streamlit Cloud**: Auto-scales, pay per usage
- **Vercel**: Serverless, auto-scales to 0
- **Google Cloud Run**: Auto-scales, pay per request
- **Docker on VPS**: Manual scaling needed

## Support

For issues:
1. Check logs (see Monitoring section)
2. Test locally first
3. Verify dependencies installed
4. Check Python version (3.9+)
5. Ensure ezdxf/ezdxf dependencies available
