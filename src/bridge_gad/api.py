"""
FastAPI web API for the Bridge GAD Generator.

This module provides a web interface to the bridge drawing functionality.
"""

from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import shutil

# Import the main application functionality
from . import __version__
from .config import Settings, load_settings
from .core import generate_bridge_drawing

# Create FastAPI app
app = FastAPI(
    title="Bridge GAD Generator API",
    description="REST API for generating Bridge General Arrangement Drawings",
    version=__version__,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load default settings
settings = load_settings()

@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "name": "Bridge GAD Generator API",
        "version": __version__,
        "description": "REST API for generating Bridge General Arrangement Drawings",
        "endpoints": [
            {"path": "/predict", "method": "POST", "description": "Generate bridge drawing from Excel file"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/docs", "method": "GET", "description": "API documentation"}
        ]
    }

@app.post("/predict")
async def predict(
    excel_file: UploadFile = File(...),
    config_file: Optional[UploadFile] = None,
    output_format: str = "dxf",
):
    """
    Generate a bridge drawing from an Excel file.
    
    Args:
        excel_file: The Excel file containing bridge data
        config_file: Optional YAML configuration file
        output_format: Output format (default: dxf)
        
    Returns:
        The generated drawing file
    """
    # Create a temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        
        # Save uploaded files
        excel_path = temp_dir_path / excel_file.filename
        with open(excel_path, "wb") as f:
            shutil.copyfileobj(excel_file.file, f)
        
        config_path = None
        if config_file:
            config_path = temp_dir_path / "config.yaml"
            with open(config_path, "wb") as f:
                shutil.copyfileobj(config_file.file, f)
        
        # Set up output path
        output_path = temp_dir_path / f"output.{output_format}"
        
        # Prepare command line arguments
        args = [
            "generate",  # The Typer command
            str(excel_path),
            "--output", str(output_path),
        ]
        
        if config_path:
            args.extend(["--config", str(config_path)])
        
        # Generate the drawing
        try:
            result_path = generate_bridge_drawing(
                excel_file=excel_path,
                config_file=config_path,
                output_path=output_path
            )
            
            # Return the generated file
            if not result_path.exists():
                raise HTTPException(
                    status_code=500,
                    detail="Drawing generation failed - no output file was created"
                )
                
            return FileResponse(
                result_path,
                media_type=f"application/{output_format}",
                filename=f"bridge_drawing.{output_format}"
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing request: {str(e)}"
            )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": __version__}

# This allows running the API directly with: python -m bridge_gad.api
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
