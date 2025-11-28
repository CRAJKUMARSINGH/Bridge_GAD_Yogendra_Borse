"""
Vercel serverless function for Bridge GAD drawing generation
"""

import json
import tempfile
from pathlib import Path
import sys
import base64

# Add src to path
sys.path.insert(0, '/var/task/src')
from bridge_gad.bridge_generator import BridgeGADGenerator
import pandas as pd


def handler(request):
    """Handle drawing generation requests"""
    try:
        # Parse request
        body = json.loads(request.body) if isinstance(request.body, str) else request.body
        
        # Get parameters
        excel_data = body.get('excel_data')
        acad_version = body.get('acad_version', 'R2010')
        output_format = body.get('output_format', 'dxf')
        
        if not excel_data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No Excel data provided'})
            }
        
        # Decode base64 Excel file
        excel_bytes = base64.b64decode(excel_data)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save Excel file
            excel_file = temp_path / 'input.xlsx'
            with open(excel_file, 'wb') as f:
                f.write(excel_bytes)
            
            # Generate drawing
            gen = BridgeGADGenerator(acad_version=acad_version)
            output_file = temp_path / f'bridge_gad.{output_format}'
            
            success = gen.generate_complete_drawing(excel_file, output_file)
            
            if success and output_file.exists():
                # Read generated file
                with open(output_file, 'rb') as f:
                    result_data = base64.b64encode(f.read()).decode('utf-8')
                
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'success': True,
                        'file_data': result_data,
                        'format': output_format,
                        'size': output_file.stat().st_size
                    }),
                    'headers': {
                        'Content-Type': 'application/json'
                    }
                }
            else:
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': 'Drawing generation failed'})
                }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
