# Bridge GAD Generator - Development Roadmap

## ✅ Completed
- [x] Add shebang and format with Black
- [x] Expose version information
- [x] Add Typer CLI interface
- [x] Move configuration to YAML with pydantic-settings

## 🚧 Next Steps

### 1. Testing Setup
```bash
# Create tests directory and basic test file
mkdir tests
echo -e "def test_import():\n    import app" > tests/test_basic.py

# Install testing dependencies
pip install pytest pytest-cov

# Run tests with coverage
pytest --cov=app tests/
```

### 2. CI/CD Pipeline (GitHub Actions)
Create `.github/workflows/ci.yml`:
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.11"}
      - run: pip install -r requirements.txt pytest
      - run: pytest
```

### 3. Package Structure
```bash
# Create proper package structure
mkdir -p src/bridge_gad
mv app.py src/bridge_gad/__init__.py
touch pyproject.toml
```

### 4. Package Configuration
Create `pyproject.toml`:
```toml
[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "bridge-gad"
version = "0.2.0"
description = "Bridge GAD Generator"
requires-python = ">=3.9"
dependencies = [
  "typer[all]>=0.9",
  "pydantic>=2.0",
  "pyyaml>=6.0",
  "ezdxf>=1.0.0",
  "pandas>=1.0.0"
]

[project.scripts]
bridge-gad = "bridge_gad.__main__:app"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "--cov=bridge_gad --cov-report=term-missing"
```

### 5. (Optional) FastAPI Web Layer
```bash
# Install FastAPI and Uvicorn
pip install fastapi uvicorn

# Create a simple API (e.g., api.py)
# Add a /predict endpoint that wraps your core logic
```

### 6. Development Setup
```bash
# Install in development mode
pip install -e .

# Run tests
pytest

# Run the application
bridge-gad --help
```

## 🏗️ Project Structure
```
bridge_gad/
├── src/
│   └── bridge_gad/
│       ├── __init__.py
│       ├── __main__.py
│       ├── config.py
│       └── core.py
├── tests/
│   └── test_basic.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── pyproject.toml
├── README.md
└── requirements.txt
```

## 📦 Release Process
1. Update version in `pyproject.toml`
2. Commit changes with `git commit -am "Bump version to x.y.z"`
3. Tag the release: `git tag -a vx.y.z -m "Version x.y.z"`
4. Push with tags: `git push --follow-tags`
