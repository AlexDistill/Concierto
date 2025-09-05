#!/usr/bin/env python3
"""
Script to add semantic analysis to existing items in content/data.json
"""

import json
import numpy as np
from pathlib import Path
from semantic_analyzer import analyze_semantic

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

def main():
    data_file = Path("content/data.json")
    
    if not data_file.exists():
        print("No data file found")
        return
    
    # Load existing data
    with open(data_file) as f:
        data = json.load(f)
    
    updated = 0
    for item in data['items']:
        if item.get('type') == 'image' and 'semantic_analysis' not in item:
            # Get image path
            image_path = item.get('path')
            if image_path and Path(image_path).exists():
                print(f"Adding semantic analysis to {item['filename']}...")
                
                # Run semantic analysis
                semantic_data = analyze_semantic(image_path, item.get('description', ''))
                if semantic_data and 'error' not in semantic_data:
                    item['semantic_analysis'] = semantic_data
                    updated += 1
                    print(f"  ✓ Added semantic analysis")
                else:
                    print(f"  ✗ Failed to analyze")
    
    if updated > 0:
        # Save updated data
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2, cls=NumpyEncoder)
        print(f"\n✅ Updated {updated} items with semantic analysis")
    else:
        print("No items needed semantic analysis updates")

if __name__ == "__main__":
    main()