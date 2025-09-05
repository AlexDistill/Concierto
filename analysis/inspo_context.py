#!/usr/bin/env python3
"""
Inspiration Context Merger - Atom Bus System

Merges per-image analysis JSON into atoms/merged.json. 
Canonicalizes tags, clusters palettes, weights tokens from inspiration images.

This integrates with Concierto's existing brand synthesis system to create
structured atoms that can be used by the prompt kitchen and other tools.
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter
import colorsys
from datetime import datetime
import os
import sys

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from semantic_analyzer import SemanticAnalyzer, analyze_semantic
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False
    print("Warning: semantic_analyzer not available")

class AtomBus:
    """
    Merges inspiration analysis into structured atoms for prompt generation
    """
    
    def __init__(self):
        self.semantic_analyzer = SemanticAnalyzer() if SEMANTIC_AVAILABLE else None
        
    def merge_inspiration_atoms(self, input_files: List[str], output_path: str) -> Dict:
        """
        Main entry point - merges multiple analysis JSON files into atoms
        
        Args:
            input_files: List of JSON file paths to merge
            output_path: Where to save the merged atoms
            
        Returns:
            Dict containing the merged atoms structure
        """
        print(f"🔄 Merging {len(input_files)} inspiration files into atoms...")
        
        all_items = []
        
        # Load all inspiration items
        for file_path in input_files:
            items = self._load_inspiration_file(file_path)
            all_items.extend(items)
        
        print(f"✓ Loaded {len(all_items)} inspiration items")
        
        # Process items through semantic analysis if needed
        enriched_items = []
        for item in all_items:
            # Skip non-dict items (malformed data)
            if not isinstance(item, dict):
                print(f"  Warning: Skipping malformed item: {type(item)} {str(item)[:50]}...")
                continue
                
            enriched_item = self._enrich_with_semantic_analysis(item)
            if enriched_item:
                enriched_items.append(enriched_item)
        
        # Create structured atoms
        atoms = self._create_atoms_structure(enriched_items)
        
        # Save merged atoms
        self._save_atoms(atoms, output_path)
        
        print(f"✓ Merged atoms saved to {output_path}")
        return atoms
    
    def _load_inspiration_file(self, file_path: str) -> List[Dict]:
        """Load items from a single inspiration file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Handle different file formats
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Single item or container with items
                if 'items' in data:
                    return data['items']
                else:
                    return [data]
            
            return []
            
        except Exception as e:
            print(f"Warning: Could not load {file_path}: {e}")
            return []
    
    def _enrich_with_semantic_analysis(self, item: Dict) -> Optional[Dict]:
        """Enrich an item with semantic analysis if it has an image"""
        if not self.semantic_analyzer:
            return item
            
        # Check if item has an image file
        image_path = None
        
        if 'filepath' in item and item['filepath']:
            # Convert relative path to absolute
            filepath = item['filepath']
            if filepath.startswith('../'):
                filepath = filepath[3:]  # Remove '../'
            
            full_path = Path(__file__).parent.parent / filepath
            if full_path.exists():
                image_path = str(full_path)
        
        elif 'filename' in item:
            # Try to find the image in common locations
            filename = item['filename']
            search_paths = [
                Path(__file__).parent.parent / "content" / "manual-input" / "images",
                Path(__file__).parent.parent / "content" / "images",
                Path(__file__).parent.parent / "images"
            ]
            
            for search_path in search_paths:
                potential_path = search_path / filename
                if potential_path.exists():
                    image_path = str(potential_path)
                    break
        
        if image_path:
            try:
                # Get existing description or use title
                description = item.get('description', item.get('title', ''))
                semantic_data = analyze_semantic(image_path, description)
                
                if semantic_data and 'error' not in semantic_data:
                    item['semantic_analysis'] = semantic_data
                    print(f"  ✓ Added semantic analysis for {item.get('filename', 'unknown')}")
                
            except Exception as e:
                print(f"  Warning: Semantic analysis failed for {image_path}: {e}")
        
        return item
    
    def _create_atoms_structure(self, items: List[Dict]) -> Dict:
        """Create the standardized atoms structure from inspiration items"""
        
        # Extract and canonicalize data
        colors = self._extract_colors(items)
        tags = self._canonicalize_tags(items)
        objects = self._extract_objects(items)
        themes = self._extract_themes(items)
        
        # Create atoms structure
        atoms = {
            'generated_at': datetime.now().isoformat(),
            'source_count': len(items),
            'version': '1.0',
            
            # Core visual atoms
            'colors': colors,
            'objects': objects,
            'tags': tags,
            'themes': themes,
            
            # Processed insights
            'palettes': self._create_palette_clusters(colors),
            'visual_tone': self._determine_visual_tone(items),
            'provenance': self._create_provenance(items),
            
            # Raw source data for reference
            'source_items': items
        }
        
        return atoms
    
    def _extract_colors(self, items: List[Dict]) -> Dict:
        """Extract and cluster colors from all items"""
        all_colors = []
        color_weights = defaultdict(float)
        
        for item in items:
            semantic = item.get('semantic_analysis', {})
            if 'colors' in semantic:
                colors_data = semantic['colors']
                if 'most_common' in colors_data:
                    for color_info in colors_data['most_common']:
                        hex_color = color_info['hex']
                        weight = color_info['percentage'] / 100.0
                        
                        all_colors.append({
                            'hex': hex_color,
                            'rgb': color_info['rgb'],
                            'weight': weight,
                            'saturation': color_info['saturation'],
                            'brightness': color_info['brightness'],
                            'hue': color_info['hue']
                        })
                        
                        color_weights[hex_color] += weight
        
        # Sort by total weight across all images
        weighted_colors = []
        for color_hex, total_weight in sorted(color_weights.items(), 
                                            key=lambda x: x[1], reverse=True):
            # Find color info
            color_info = next((c for c in all_colors if c['hex'] == color_hex), None)
            if color_info:
                color_info['total_weight'] = total_weight
                weighted_colors.append(color_info)
        
        return {
            'primary': weighted_colors[:8],
            'all_extracted': weighted_colors,
            'total_unique': len(color_weights)
        }
    
    def _canonicalize_tags(self, items: List[Dict]) -> Dict:
        """Extract and canonicalize tags from all sources"""
        all_tags = []
        
        for item in items:
            # From explicit tags
            if 'tags' in item and item['tags']:
                all_tags.extend(item['tags'])
            
            # From semantic analysis keywords
            semantic = item.get('semantic_analysis', {})
            if 'description_keywords' in semantic:
                all_tags.extend(semantic['description_keywords'])
            
            # From category
            if 'category' in item and item['category']:
                all_tags.append(item['category'])
        
        # Count and canonicalize
        tag_counts = Counter(all_tags)
        
        # Clean up tags
        canonical_tags = []
        for tag, count in tag_counts.most_common(50):
            clean_tag = self._clean_tag(tag)
            if clean_tag and len(clean_tag) > 2:
                canonical_tags.append({
                    'tag': clean_tag,
                    'frequency': count,
                    'weight': count / len(items)
                })
        
        return {
            'canonical': canonical_tags[:20],
            'all_counts': dict(tag_counts),
            'total_unique': len(tag_counts)
        }
    
    def _clean_tag(self, tag: str) -> str:
        """Clean and normalize a tag"""
        if not tag or not isinstance(tag, str):
            return ""
        
        # Clean up the tag
        clean = tag.lower().strip()
        clean = clean.replace('_', '-').replace(' ', '-')
        
        # Remove special characters except hyphens
        clean = ''.join(c for c in clean if c.isalnum() or c == '-')
        
        return clean
    
    def _extract_objects(self, items: List[Dict]) -> List[str]:
        """Extract visual objects/elements from semantic analysis"""
        objects = []
        
        for item in items:
            # From filename analysis
            filename = item.get('filename', '')
            if filename:
                # Simple object extraction from filename
                filename_clean = filename.lower().replace('_', ' ').replace('-', ' ')
                potential_objects = filename_clean.split()
                objects.extend([obj for obj in potential_objects if len(obj) > 3])
        
        # Get most common objects
        object_counts = Counter(objects)
        return [obj for obj, count in object_counts.most_common(10) if count > 1]
    
    def _extract_themes(self, items: List[Dict]) -> List[Dict]:
        """Extract thematic elements from the collection"""
        themes = []
        
        # Analyze visual properties for thematic patterns
        brightness_values = []
        saturation_values = []
        
        for item in items:
            semantic = item.get('semantic_analysis', {})
            if 'visual_properties' in semantic:
                props = semantic['visual_properties']
                if 'brightness' in props:
                    brightness_values.append(props['brightness'])
                if 'saturation' in props:
                    saturation_values.append(props['saturation'])
        
        # Determine themes based on visual characteristics
        if brightness_values:
            avg_brightness = sum(brightness_values) / len(brightness_values)
            if avg_brightness > 0.7:
                themes.append({
                    'theme': 'bright-optimistic',
                    'confidence': 0.8,
                    'evidence': f'High brightness average: {avg_brightness:.2f}'
                })
            elif avg_brightness < 0.3:
                themes.append({
                    'theme': 'dark-moody',
                    'confidence': 0.8,
                    'evidence': f'Low brightness average: {avg_brightness:.2f}'
                })
        
        if saturation_values:
            avg_saturation = sum(saturation_values) / len(saturation_values)
            if avg_saturation > 0.6:
                themes.append({
                    'theme': 'vibrant-energetic',
                    'confidence': 0.7,
                    'evidence': f'High saturation average: {avg_saturation:.2f}'
                })
            elif avg_saturation < 0.3:
                themes.append({
                    'theme': 'muted-sophisticated',
                    'confidence': 0.7,
                    'evidence': f'Low saturation average: {avg_saturation:.2f}'
                })
        
        return themes
    
    def _create_palette_clusters(self, colors_data: Dict) -> List[Dict]:
        """Create color palette clusters from extracted colors"""
        if 'primary' not in colors_data:
            return []
        
        primary_colors = colors_data['primary']
        if len(primary_colors) < 3:
            return []
        
        # Create a few different palette options
        palettes = []
        
        # Monochromatic palette from dominant color
        if primary_colors:
            dominant = primary_colors[0]
            mono_palette = self._create_monochromatic_palette(dominant)
            if mono_palette:
                palettes.append(mono_palette)
        
        # Complementary palette from top 2 colors
        if len(primary_colors) >= 2:
            comp_palette = self._create_complementary_palette(primary_colors[:2])
            if comp_palette:
                palettes.append(comp_palette)
        
        # Triadic from top 3 colors
        if len(primary_colors) >= 3:
            triadic_palette = {
                'name': 'triadic',
                'colors': [c['hex'] for c in primary_colors[:3]],
                'harmony': 'triadic',
                'confidence': 0.8
            }
            palettes.append(triadic_palette)
        
        return palettes
    
    def _create_monochromatic_palette(self, base_color: Dict) -> Optional[Dict]:
        """Create a monochromatic palette from a base color"""
        try:
            r, g, b = base_color['rgb']
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            
            # Create variations
            colors = []
            for v_mod in [0.3, 0.6, 1.0, 0.8]:
                new_r, new_g, new_b = colorsys.hsv_to_rgb(h, s, v_mod)
                hex_color = '#{:02x}{:02x}{:02x}'.format(
                    int(new_r * 255), int(new_g * 255), int(new_b * 255)
                )
                colors.append(hex_color)
            
            return {
                'name': 'monochromatic',
                'colors': colors,
                'harmony': 'monochromatic',
                'base_color': base_color['hex'],
                'confidence': 0.9
            }
        except:
            return None
    
    def _create_complementary_palette(self, colors: List[Dict]) -> Optional[Dict]:
        """Create complementary palette from two colors"""
        if len(colors) < 2:
            return None
        
        return {
            'name': 'complementary',
            'colors': [c['hex'] for c in colors],
            'harmony': 'complementary',
            'confidence': 0.7
        }
    
    def _determine_visual_tone(self, items: List[Dict]) -> Dict:
        """Determine overall visual tone of the collection"""
        tone_indicators = defaultdict(int)
        
        for item in items:
            semantic = item.get('semantic_analysis', {})
            if 'visual_properties' in semantic:
                props = semantic['visual_properties']
                
                # Brightness tone
                if props.get('brightness', 0) > 0.7:
                    tone_indicators['bright'] += 1
                elif props.get('brightness', 0) < 0.3:
                    tone_indicators['dark'] += 1
                
                # Saturation tone  
                if props.get('saturation', 0) > 0.6:
                    tone_indicators['vibrant'] += 1
                elif props.get('saturation', 0) < 0.3:
                    tone_indicators['muted'] += 1
                
                # Contrast tone
                if props.get('contrast', 0) > 0.7:
                    tone_indicators['high-contrast'] += 1
                elif props.get('contrast', 0) < 0.3:
                    tone_indicators['soft'] += 1
        
        # Determine primary tone
        if tone_indicators:
            primary_tone = max(tone_indicators.items(), key=lambda x: x[1])
            return {
                'primary': primary_tone[0],
                'confidence': primary_tone[1] / len(items),
                'all_indicators': dict(tone_indicators)
            }
        
        return {'primary': 'neutral', 'confidence': 0.5, 'all_indicators': {}}
    
    def _create_provenance(self, items: List[Dict]) -> Dict:
        """Create provenance information for the atoms"""
        sources = defaultdict(int)
        file_types = defaultdict(int)
        
        for item in items:
            source = item.get('source', 'unknown')
            sources[source] += 1
            
            if 'filename' in item:
                ext = Path(item['filename']).suffix.lower()
                if ext:
                    file_types[ext] += 1
        
        return {
            'sources': dict(sources),
            'file_types': dict(file_types),
            'total_items': len(items),
            'processing_date': datetime.now().isoformat()
        }
    
    def _save_atoms(self, atoms: Dict, output_path: str) -> None:
        """Save atoms to JSON file"""
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(atoms, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description='Merge inspiration analysis into atoms')
    parser.add_argument('--inputs', nargs='+', required=True,
                       help='Input JSON files to merge')
    parser.add_argument('--out', required=True,
                       help='Output path for merged atoms.json')
    
    args = parser.parse_args()
    
    # Validate input files
    valid_inputs = []
    for input_file in args.inputs:
        if os.path.exists(input_file):
            valid_inputs.append(input_file)
        else:
            print(f"Warning: {input_file} not found, skipping")
    
    if not valid_inputs:
        print("No valid input files found!")
        return 1
    
    # Create atom bus and merge
    atom_bus = AtomBus()
    atoms = atom_bus.merge_inspiration_atoms(valid_inputs, args.out)
    
    print(f"\n🎯 Atoms Summary:")
    print(f"   Colors: {len(atoms['colors']['primary'])} primary")
    print(f"   Tags: {len(atoms['tags']['canonical'])} canonical")
    print(f"   Objects: {len(atoms['objects'])}")
    print(f"   Themes: {len(atoms['themes'])}")
    print(f"   Palettes: {len(atoms['palettes'])}")
    
    return 0


if __name__ == "__main__":
    exit(main())