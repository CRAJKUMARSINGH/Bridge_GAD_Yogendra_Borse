# Bridge GAD Generator

A Python application for generating Bridge General Arrangement Drawings (GAD) from input parameters and Excel data.

## Features

- Generate bridge drawings from Excel input
- Support for multiple span configurations
- Customizable output settings
- Command-line interface with Typer
- Configuration via YAML files
- **NEW**: Web API with FastAPI

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/bridge-gad.git
   cd bridge-gad
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

   For production use (without development dependencies):
   ```bash
   pip install .
   ```

## Usage

### Command Line Interface

```bash
# Show help
bridge-gad --help

# Generate drawing with default config
bridge-gad generate input.xlsx output.dxf

# Specify custom config file
bridge-gad generate input.xlsx output.dxf --config config.yaml

# Show version
bridge-gad version
```

### Web API

Start the web server:
```bash
bridge-gad serve
```

This will start the FastAPI server on `http://localhost:8000` with the following endpoints:

- `GET /`: API documentation and available endpoints
- `POST /predict`: Generate a bridge drawing from an Excel file
- `GET /health`: Health check endpoint

#### Using the API

1. **Using curl**:
   ```bash
   # Generate drawing
   curl -X POST -F "excel_file=@input.xlsx" http://localhost:8000/predict -o output.dxf
   
   # With custom config
   curl -X POST -F "excel_file=@input.xlsx" -F "config_file=@config.yaml" http://localhost:8000/predict -o output.dxf
   ```

2. **Using Python requests**:
   ```python
   import requests
   
   url = "http://localhost:8000/predict"
   files = {
       'excel_file': ('input.xlsx', open('input.xlsx', 'rb'), 'application/vnd.ms-excel'),
       'config_file': ('config.yaml', open('config.yaml', 'rb'), 'application/yaml')
   }
   
   response = requests.post(url, files=files)
   with open('output.dxf', 'wb') as f:
       f.write(response.content)
   ```

#### Development Mode

For development with auto-reload:
```bash
bridge-gad serve --reload
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install -e ".[test]"

# Run tests
pytest

# Run with coverage report
pytest --cov=bridge_gad --cov-report=term-missing
```

### Code Style

This project uses `black` for code formatting and `isort` for import sorting.

```bash
# Format code
black .

# Sort imports
isort .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
