#!/usr/bin/env python3
"""
SVG Logo Scaffolder - Concierto Brand Generation

Turns a directions JSON (with svg_plan) into rough SVG logos.
Generates actual SVG files from structured logo concept directions.

Integrates with Concierto's brand synthesis system to create scaffolded
SVG logos based on concept directions and brand atoms.
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import math
import os
import sys
from datetime import datetime

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

class SVGLogoScaffolder:
    """
    Generates SVG logos from JSON directions containing structured logo concepts
    """
    
    def __init__(self):
        self.canvas_width = 200
        self.canvas_height = 200
        self.default_colors = ['#1f2937', '#6b7280', '#d1d5db', '#f3f4f6']
        
    def scaffold_logos(self, directions_path: str, output_dir: str = "outputs/logo_svgs") -> Dict:
        """
        Main entry point - generates SVG logos from directions JSON
        
        Args:
            directions_path: Path to logo directions JSON file
            output_dir: Directory to save generated SVG files
            
        Returns:
            Dict with generated logos metadata
        """
        print(f"🎨 Scaffolding SVG logos from directions...")
        
        # Load directions
        directions = self._load_directions(directions_path)
        if not directions:
            raise ValueError(f"Could not load directions from {directions_path}")
        
        # Generate SVG logos
        generated_logos = self._generate_all_logos(directions, output_dir)
        
        result = {
            'directions_file': directions_path,
            'output_directory': output_dir,
            'generated_logos': generated_logos,
            'total_logos': len(generated_logos),
            'generated_at': datetime.now().isoformat()
        }
        
        print(f"✓ Generated {len(generated_logos)} SVG logos")
        for logo in generated_logos:
            print(f"  • {logo['name']}: {logo['svg_file']}")
        
        return result
    
    def _load_directions(self, directions_path: str) -> Optional[Dict]:
        """Load logo directions from JSON file"""
        try:
            with open(directions_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading directions: {e}")
            return None
    
    def _generate_all_logos(self, directions: Dict, output_dir: str) -> List[Dict]:
        """Generate all logo variations from directions"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        generated_logos = []
        
        # Extract logo concepts from directions
        logo_concepts = self._extract_logo_concepts(directions)
        
        for i, concept in enumerate(logo_concepts):
            logo_name = concept.get('name', f'logo_{i+1}')
            svg_content = self._generate_svg_from_concept(concept)
            
            # Save SVG file
            svg_filename = f"{logo_name.replace(' ', '_').lower()}.svg"
            svg_path = output_path / svg_filename
            
            with open(svg_path, 'w') as f:
                f.write(svg_content)
            
            generated_logos.append({
                'name': logo_name,
                'svg_file': str(svg_path),
                'concept': concept,
                'file_size': len(svg_content)
            })
        
        return generated_logos
    
    def _extract_logo_concepts(self, directions: Dict) -> List[Dict]:
        """Extract individual logo concepts from directions"""
        concepts = []
        
        # Check for svg_plan in directions
        if 'svg_plan' in directions:
            svg_plan = directions['svg_plan']
            
            if isinstance(svg_plan, list):
                # Multiple logo concepts
                concepts.extend(svg_plan)
            elif isinstance(svg_plan, dict):
                # Single logo concept
                concepts.append(svg_plan)
        
        # Check for direct logo concepts
        if 'logo_concepts' in directions:
            logo_concepts = directions['logo_concepts']
            if isinstance(logo_concepts, list):
                concepts.extend(logo_concepts)
        
        # Check for concept variations
        if 'variations' in directions:
            variations = directions['variations']
            if isinstance(variations, list):
                concepts.extend(variations)
        
        # If no structured concepts, create from basic directions
        if not concepts and 'brand_name' in directions:
            concepts.append({
                'name': f"{directions['brand_name']}_logo",
                'type': 'text',
                'text': directions['brand_name'],
                'style': directions.get('style', 'modern'),
                'colors': directions.get('colors', self.default_colors[:2])
            })
        
        return concepts
    
    def _generate_svg_from_concept(self, concept: Dict) -> str:
        """Generate SVG content from a single logo concept"""
        svg_type = concept.get('type', 'text')
        
        if svg_type == 'text':
            return self._generate_text_logo(concept)
        elif svg_type == 'symbol':
            return self._generate_symbol_logo(concept)
        elif svg_type == 'combination':
            return self._generate_combination_logo(concept)
        else:
            return self._generate_text_logo(concept)  # Fallback
    
    def _generate_text_logo(self, concept: Dict) -> str:
        """Generate a text-based SVG logo"""
        text = concept.get('text', 'LOGO')
        colors = concept.get('colors', self.default_colors)
        style = concept.get('style', 'modern')
        
        # Choose colors
        primary_color = colors[0] if colors else self.default_colors[0]
        
        # Style-specific settings
        if style == 'bold':
            font_weight = '900'
            font_family = 'sans-serif'
            font_size = '28'
        elif style == 'elegant':
            font_weight = '300'
            font_family = 'serif'
            font_size = '24'
        elif style == 'playful':
            font_weight = '600'
            font_family = 'sans-serif'
            font_size = '26'
        else:  # modern
            font_weight = '500'
            font_family = 'sans-serif'
            font_size = '22'
        
        # Calculate text positioning
        text_length = len(text)
        x_pos = self.canvas_width // 2
        y_pos = self.canvas_height // 2 + int(font_size) // 3
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{self.canvas_width}" height="{self.canvas_height}" viewBox="0 0 {self.canvas_width} {self.canvas_height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .logo-text {{
        font-family: {font_family};
        font-weight: {font_weight};
        font-size: {font_size}px;
        text-anchor: middle;
        dominant-baseline: middle;
      }}
    </style>
  </defs>
  
  <!-- Background (optional) -->
  <rect width="{self.canvas_width}" height="{self.canvas_height}" fill="transparent"/>
  
  <!-- Logo text -->
  <text x="{x_pos}" y="{y_pos}" class="logo-text" fill="{primary_color}">
    {text}
  </text>
</svg>'''
        
        return svg_content
    
    def _generate_symbol_logo(self, concept: Dict) -> str:
        """Generate a symbol-based SVG logo"""
        symbol_type = concept.get('symbol_type', 'circle')
        colors = concept.get('colors', self.default_colors)
        text = concept.get('text', '')
        
        primary_color = colors[0] if colors else self.default_colors[0]
        secondary_color = colors[1] if len(colors) > 1 else self.default_colors[1]
        
        center_x = self.canvas_width // 2
        center_y = self.canvas_height // 2
        
        # Generate symbol based on type
        if symbol_type == 'circle':
            symbol_svg = f'<circle cx="{center_x}" cy="{center_y}" r="40" fill="{primary_color}" stroke="{secondary_color}" stroke-width="3"/>'
        elif symbol_type == 'square':
            symbol_svg = f'<rect x="{center_x-40}" y="{center_y-40}" width="80" height="80" fill="{primary_color}" stroke="{secondary_color}" stroke-width="3"/>'
        elif symbol_type == 'triangle':
            points = f"{center_x},{center_y-40} {center_x-35},{center_y+25} {center_x+35},{center_y+25}"
            symbol_svg = f'<polygon points="{points}" fill="{primary_color}" stroke="{secondary_color}" stroke-width="3"/>'
        elif symbol_type == 'diamond':
            points = f"{center_x},{center_y-40} {center_x+40},{center_y} {center_x},{center_y+40} {center_x-40},{center_y}"
            symbol_svg = f'<polygon points="{points}" fill="{primary_color}" stroke="{secondary_color}" stroke-width="3"/>'
        else:
            # Default to circle
            symbol_svg = f'<circle cx="{center_x}" cy="{center_y}" r="40" fill="{primary_color}" stroke="{secondary_color}" stroke-width="3"/>'
        
        # Add text if specified
        text_svg = ''
        if text:
            text_y = center_y + 70
            text_svg = f'<text x="{center_x}" y="{text_y}" font-family="sans-serif" font-size="16" font-weight="500" text-anchor="middle" fill="{primary_color}">{text}</text>'
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{self.canvas_width}" height="{self.canvas_height}" viewBox="0 0 {self.canvas_width} {self.canvas_height}" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="{self.canvas_width}" height="{self.canvas_height}" fill="transparent"/>
  
  <!-- Symbol -->
  {symbol_svg}
  
  <!-- Text (if any) -->
  {text_svg}
</svg>'''
        
        return svg_content
    
    def _generate_combination_logo(self, concept: Dict) -> str:
        """Generate a combination text + symbol logo"""
        text = concept.get('text', 'LOGO')
        symbol_type = concept.get('symbol_type', 'circle')
        colors = concept.get('colors', self.default_colors)
        layout = concept.get('layout', 'horizontal')  # horizontal, vertical, stacked
        
        primary_color = colors[0] if colors else self.default_colors[0]
        secondary_color = colors[1] if len(colors) > 1 else self.default_colors[1]
        
        if layout == 'vertical':
            # Symbol on top, text below
            symbol_x = self.canvas_width // 2
            symbol_y = 60
            text_x = self.canvas_width // 2
            text_y = 150
            symbol_size = 25
        elif layout == 'stacked':
            # Symbol and text centered, overlapping
            symbol_x = self.canvas_width // 2
            symbol_y = self.canvas_height // 2
            text_x = self.canvas_width // 2
            text_y = self.canvas_height // 2
            symbol_size = 35
        else:  # horizontal
            # Symbol on left, text on right
            symbol_x = 60
            symbol_y = self.canvas_height // 2
            text_x = 140
            text_y = self.canvas_height // 2 + 6
            symbol_size = 30
        
        # Generate symbol
        if symbol_type == 'circle':
            symbol_svg = f'<circle cx="{symbol_x}" cy="{symbol_y}" r="{symbol_size}" fill="{secondary_color}" stroke="{primary_color}" stroke-width="2"/>'
        elif symbol_type == 'square':
            symbol_svg = f'<rect x="{symbol_x-symbol_size}" y="{symbol_y-symbol_size}" width="{symbol_size*2}" height="{symbol_size*2}" fill="{secondary_color}" stroke="{primary_color}" stroke-width="2"/>'
        else:
            symbol_svg = f'<circle cx="{symbol_x}" cy="{symbol_y}" r="{symbol_size}" fill="{secondary_color}" stroke="{primary_color}" stroke-width="2"/>'
        
        # Text styling
        font_size = "20" if layout == 'horizontal' else "18"
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{self.canvas_width}" height="{self.canvas_height}" viewBox="0 0 {self.canvas_width} {self.canvas_height}" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="{self.canvas_width}" height="{self.canvas_height}" fill="transparent"/>
  
  <!-- Symbol -->
  {symbol_svg}
  
  <!-- Text -->
  <text x="{text_x}" y="{text_y}" font-family="sans-serif" font-size="{font_size}" font-weight="600" text-anchor="middle" dominant-baseline="middle" fill="{primary_color}">
    {text}
  </text>
</svg>'''
        
        return svg_content


def main():
    parser = argparse.ArgumentParser(description='Generate SVG logos from directions JSON')
    parser.add_argument('--directions', required=True, help='Path to logo directions JSON')
    parser.add_argument('--outdir', default='outputs/logo_svgs', help='Output directory for SVG files')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.directions):
        print(f"Error: Directions file not found: {args.directions}")
        return 1
    
    # Create scaffolder
    scaffolder = SVGLogoScaffolder()
    
    try:
        result = scaffolder.scaffold_logos(args.directions, args.outdir)
        
        print(f"\n🎯 SVG Logo Generation Summary:")
        print(f"   Total logos: {result['total_logos']}")
        print(f"   Output directory: {result['output_directory']}")
        
        return 0
        
    except Exception as e:
        print(f"Error generating SVG logos: {e}")
        return 1


if __name__ == "__main__":
    exit(main())