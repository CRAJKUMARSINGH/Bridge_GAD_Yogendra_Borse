#!/usr/bin/env python3
"""
Test System for Enhanced BridgeGAD-00
"""

import os
import sys
import logging
import pandas as pd
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_features import EnhancedBridgeGenerator

class TestSystem:
    """Test system for BridgeGAD-00"""
    
    def __init__(self):
        self.enhanced_generator = EnhancedBridgeGenerator()
        
    def create_sample_documents(self):
        """Create sample SweetWilled documents"""
        documents = [
            {
                'name': 'SweetWilledDocument-01',
                'type': 'slab',
                'span_length': 20.0,
                'deck_width': 7.5,
                'height': 15.0,
                'supports': 0,
                'material': 'concrete',
                'load_capacity': 40.0
            },
            {
                'name': 'SweetWilledDocument-02', 
                'type': 'beam',
                'span_length': 45.0,
                'deck_width': 12.0,
                'height': 25.0,
                'supports': 2,
                'material': 'steel',
                'load_capacity': 60.0
            }
        ]
        return documents
    
    def run_tests(self):
        """Run comprehensive tests"""
        print("🚀 Starting BridgeGAD-00 Test System...")
        
        documents = self.create_sample_documents()
        results = {}
        
        for doc in documents:
            print(f"Testing {doc['name']}...")
            try:
                result = self.enhanced_generator.generate_comprehensive_output(doc)
                results[doc['name']] = {'status': 'success', 'files': result}
                print(f"✅ {doc['name']} completed successfully")
            except Exception as e:
                results[doc['name']] = {'status': 'error', 'error': str(e)}
                print(f"❌ {doc['name']} failed: {e}")
        
        return results

if __name__ == "__main__":
    test_system = TestSystem()
    results = test_system.run_tests()
    
    print(f"\n📊 Test Results:")
    for name, result in results.items():
        status = "✅" if result['status'] == 'success' else "❌"
        print(f"  {status} {name}: {result['status']}")
