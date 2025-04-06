#!/usr/bin/env python3
"""
Script to run the Craniofacial Clinical Decision Support System.
"""

import os
import sys
import traceback
from craniofacial_cds.cds_system import CraniofacialCDS
from craniofacial_cds.config import app

def initialize_cds():
    # Set simple mode by default to avoid Weaviate/Memgraph dependencies
    os.environ["CDS_SIMPLE_MODE"] = "true"
    
    # Set OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("OpenAI API key not found. Please set it using:")
        print("export OPENAI_API_KEY=your_api_key_here")
        return None
    
    # Get the JSON file path from command line arguments or use the default
    json_file_path = sys.argv[1] if len(sys.argv) > 1 else "/Users/berkbarisozmen/Documents/Cursor/escargot/full_text_Craniofacial_Surgery.json"
    
    print(f"Running Craniofacial CDS with JSON file: {json_file_path}")
    
    try:
        # Initialize the CDS system
        print(f"Initializing CDS system with file: {json_file_path}")
        cds = CraniofacialCDS(json_file_path)
        
        # Process the papers
        print("Processing papers to build knowledge graph...")
        cds.process_papers()
        
        return cds
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nDetailed error information:")
        traceback.print_exc()
        print("\nTroubleshooting tips:")
        print("1. Make sure escargot is installed: pip install escargot")
        print("2. Check that your OpenAI API key is valid")
        print("3. Ensure your medical literature JSON file is properly formatted")
        print("4. Try running with a different JSON file: python run_cds.py /path/to/your/file.json")
        return None

if __name__ == "__main__":
    print("Starting Craniofacial Clinical Decision Support System...")
    print("Access the web interface at http://localhost:5002/")
    
    # Initialize CDS system
    cds = initialize_cds()
    if cds:
        # Store CDS instance in app config for routes to access
        app.config['CDS'] = cds
        # Run the Flask app
        app.run(debug=True, host='0.0.0.0', port=5002) 