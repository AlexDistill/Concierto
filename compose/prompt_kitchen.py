#!/usr/bin/env python3
"""
Prompt Kitchen - Concierto Brand Generation

Composes 3 prompt variants (faithful, exploratory, weird) for each deliverable,
blending brand_concept, territory, brand_system, expression_matrix, and atoms.

Integrates with Concierto's existing brand synthesis system to generate 
contextual prompts for various deliverables using structured atoms data.
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
import sys
from datetime import datetime

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

class PromptKitchen:
    """
    Generates prompts for brand deliverables using Jinja templates and structured data
    """
    
    def __init__(self, templates_dir: str = "compose/templates"):
        self.templates_dir = Path(templates_dir)
        
        # Set up Jinja environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Add custom filters
        self.jinja_env.filters['first_or'] = self._first_or_filter
        self.jinja_env.filters['join'] = self._join_filter
        self.jinja_env.filters['primary_colors'] = self._primary_colors_filter
        self.jinja_env.filters['visual_tone'] = self._visual_tone_filter
        
    def compose_deliverable_prompts(self, 
                                   concept_path: str,
                                   territory_path: Optional[str] = None,
                                   system_path: Optional[str] = None,
                                   expr_path: Optional[str] = None,
                                   atoms_path: str = "atoms/merged.json",
                                   deliverable: str = "product_card",
                                   output_dir: str = "outputs/prompts") -> Dict:
        """
        Main entry point - generates 3 prompt variants for a deliverable
        
        Args:
            concept_path: Path to brand concept JSON
            territory_path: Path to territory JSON (optional)
            system_path: Path to brand system JSON (optional) 
            expr_path: Path to expression matrix JSON (optional)
            atoms_path: Path to atoms/merged.json
            deliverable: Template name to use
            output_dir: Where to save generated prompts
            
        Returns:
            Dict with generated prompts and metadata
        """
        print(f"🍳 Cooking up {deliverable} prompts...")
        
        # Load all data sources
        data = self._load_all_data(concept_path, territory_path, system_path, expr_path, atoms_path)
        
        # Load template
        template = self._load_template(deliverable)
        if not template:
            raise ValueError(f"Template {deliverable} not found")
        
        # Generate 3 variants
        variants = self._generate_variants(template, data, deliverable)
        
        # Save to output directory
        output_files = self._save_variants(variants, deliverable, output_dir)
        
        result = {
            'deliverable': deliverable,
            'variants': variants,
            'output_files': output_files,
            'generated_at': datetime.now().isoformat(),
            'data_sources': {
                'concept': concept_path if os.path.exists(concept_path) else None,
                'territory': territory_path if territory_path and os.path.exists(territory_path) else None,
                'system': system_path if system_path and os.path.exists(system_path) else None,
                'expression': expr_path if expr_path and os.path.exists(expr_path) else None,
                'atoms': atoms_path if os.path.exists(atoms_path) else None
            }
        }
        
        print(f"✓ Generated {len(variants)} variants for {deliverable}")
        for variant_name, files in output_files.items():
            print(f"  • {variant_name}: {files['prompt_file']}")
        
        return result
    
    def _load_all_data(self, concept_path: str, territory_path: Optional[str],
                      system_path: Optional[str], expr_path: Optional[str], 
                      atoms_path: str) -> Dict:
        """Load and structure all data for template rendering"""
        
        data = {}
        
        # Load brand concept (required)
        try:
            with open(concept_path, 'r') as f:
                data['concept'] = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load concept from {concept_path}: {e}")
            data['concept'] = {}
        
        # Load atoms (required)
        try:
            with open(atoms_path, 'r') as f:
                data['atoms'] = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load atoms from {atoms_path}: {e}")
            data['atoms'] = {}
        
        # Load optional data sources
        optional_sources = [
            ('territory', territory_path),
            ('system', system_path),
            ('expression', expr_path)
        ]
        
        for key, path in optional_sources:
            if path and os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        data[key] = json.load(f)
                except Exception as e:
                    print(f"Warning: Could not load {key} from {path}: {e}")
                    data[key] = {}
            else:
                data[key] = {}
        
        # Create derived data for templates
        data['tokens'] = self._create_design_tokens(data)
        data['brand'] = self._create_brand_context(data)
        
        return data
    
    def _create_design_tokens(self, data: Dict) -> Dict:
        """Create design tokens from atoms and brand data"""
        atoms = data.get('atoms', {})
        concept = data.get('concept', {})
        
        tokens = {
            'colors': {},
            'typography': {},
            'layout': {
                'grid': {'columns': 12},  # Default
                'spacing': {'base': '1rem'},
                'breakpoints': {'mobile': '768px', 'desktop': '1200px'}
            },
            'brand': {}
        }
        
        # Extract color tokens from atoms
        if 'colors' in atoms and 'primary' in atoms['colors']:
            primary_colors = atoms['colors']['primary']
            
            if len(primary_colors) >= 1:
                tokens['colors']['primary'] = primary_colors[0]['hex']
            if len(primary_colors) >= 2:
                tokens['colors']['secondary'] = primary_colors[1]['hex']
            if len(primary_colors) >= 3:
                tokens['colors']['accent'] = primary_colors[2]['hex']
            
            # Create palette
            tokens['colors']['palette'] = [c['hex'] for c in primary_colors[:6]]
        
        # Extract typography hints from visual tone
        visual_tone = atoms.get('visual_tone', {})
        tone_primary = visual_tone.get('primary', 'neutral')
        
        if tone_primary in ['bright', 'vibrant']:
            tokens['typography']['weight'] = 'bold'
            tokens['typography']['style'] = 'modern'
        elif tone_primary in ['dark', 'muted']:
            tokens['typography']['weight'] = 'light'
            tokens['typography']['style'] = 'elegant'
        else:
            tokens['typography']['weight'] = 'regular'
            tokens['typography']['style'] = 'clean'
        
        # Brand-specific tokens
        if 'name' in concept:
            tokens['brand']['name'] = concept['name']
        
        return tokens
    
    def _create_brand_context(self, data: Dict) -> Dict:
        """Create unified brand context for templates"""
        concept = data.get('concept', {})
        atoms = data.get('atoms', {})
        territory = data.get('territory', {})
        
        brand = {
            'name': concept.get('name', 'Brand'),
            'personality': concept.get('personality', {}),
            'visual_identity': {},
            'messaging': {},
            'context': {}
        }
        
        # Visual identity from atoms
        if 'visual_tone' in atoms:
            brand['visual_identity']['tone'] = atoms['visual_tone']
        
        if 'themes' in atoms and atoms['themes']:
            brand['visual_identity']['themes'] = [t['theme'] for t in atoms['themes']]
        
        # Territory context
        if 'thesis' in territory:
            brand['context']['thesis'] = territory['thesis']
        
        # Objects and tags for context
        if 'objects' in atoms:
            brand['context']['objects'] = atoms['objects']
        
        if 'tags' in atoms and 'canonical' in atoms['tags']:
            brand['context']['tags'] = [t['tag'] for t in atoms['tags']['canonical'][:10]]
        
        return brand
    
    def _load_template(self, deliverable: str) -> Optional[Any]:
        """Load Jinja template for deliverable"""
        template_file = f"{deliverable}.jinja.txt"
        
        try:
            template = self.jinja_env.get_template(template_file)
            return template
        except Exception as e:
            print(f"Warning: Could not load template {template_file}: {e}")
            return None
    
    def _generate_variants(self, template: Any, data: Dict, deliverable: str) -> Dict[str, str]:
        """Generate faithful, exploratory, and weird variants"""
        variants = {}
        
        # Base context for all variants
        base_context = data.copy()
        
        # Faithful variant - stays close to brand data
        faithful_context = base_context.copy()
        faithful_context['variant_style'] = 'faithful'
        faithful_context['creativity_level'] = 'conservative'
        
        # Exploratory variant - moderate creative liberty
        exploratory_context = base_context.copy()
        exploratory_context['variant_style'] = 'exploratory' 
        exploratory_context['creativity_level'] = 'moderate'
        
        # Weird variant - maximum creative freedom
        weird_context = base_context.copy()
        weird_context['variant_style'] = 'weird'
        weird_context['creativity_level'] = 'maximum'
        
        # Apply variant-specific modifiers
        self._apply_variant_modifiers(faithful_context, 'faithful')
        self._apply_variant_modifiers(exploratory_context, 'exploratory')
        self._apply_variant_modifiers(weird_context, 'weird')
        
        # Render templates
        try:
            variants['faithful'] = template.render(**faithful_context)
            variants['exploratory'] = template.render(**exploratory_context)
            variants['weird'] = template.render(**weird_context)
        except Exception as e:
            print(f"Error rendering templates: {e}")
            # Fallback with minimal context
            minimal_context = {
                'atoms': data.get('atoms', {}),
                'brand': data.get('brand', {}),
                'tokens': data.get('tokens', {}),
                'territory': data.get('territory', {}),
                'concept': data.get('concept', {}),
                'variant_style': 'faithful'
            }
            variants['faithful'] = template.render(**minimal_context)
            variants['exploratory'] = variants['faithful']
            variants['weird'] = variants['faithful']
        
        return variants
    
    def _apply_variant_modifiers(self, context: Dict, variant_type: str) -> None:
        """Apply variant-specific modifications to context"""
        
        if variant_type == 'faithful':
            # Use primary elements, stay conservative
            if 'atoms' in context and 'colors' in context['atoms']:
                # Use only primary colors
                colors = context['atoms']['colors'].get('primary', [])
                context['atoms']['colors']['active'] = colors[:3]
            
        elif variant_type == 'exploratory':
            # Mix primary and secondary elements
            if 'atoms' in context and 'colors' in context['atoms']:
                colors = context['atoms']['colors'].get('primary', [])
                context['atoms']['colors']['active'] = colors[:5]
            
            # Add experimental tags
            if 'atoms' in context and 'tags' in context['atoms']:
                tags = context['atoms']['tags'].get('canonical', [])
                context['atoms']['tags']['active'] = [t['tag'] for t in tags[:15]]
            
        elif variant_type == 'weird':
            # Use all available elements, mix unexpectedly
            if 'atoms' in context and 'colors' in context['atoms']:
                colors = context['atoms']['colors'].get('all_extracted', [])
                context['atoms']['colors']['active'] = colors[:8]
            
            # Use all tags
            if 'atoms' in context and 'tags' in context['atoms']:
                tags = context['atoms']['tags'].get('canonical', [])
                context['atoms']['tags']['active'] = [t['tag'] for t in tags]
            
            # Add unconventional elements
            context['experimental'] = True
            context['style_mix'] = 'unexpected'
    
    def _save_variants(self, variants: Dict[str, str], deliverable: str, output_dir: str) -> Dict:
        """Save variant prompts to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        output_files = {}
        
        for variant_name, prompt_text in variants.items():
            # Create filename
            filename = f"{deliverable}_{variant_name}.txt"
            file_path = output_path / filename
            
            # Save prompt
            with open(file_path, 'w') as f:
                f.write(f"# {deliverable.replace('_', ' ').title()} - {variant_name.title()} Variant\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
                f.write(prompt_text)
            
            output_files[variant_name] = {
                'prompt_file': str(file_path),
                'length': len(prompt_text)
            }
        
        return output_files
    
    # Jinja2 custom filters
    def _first_or_filter(self, items, default=""):
        """Return first item or default"""
        if isinstance(items, list) and items:
            return items[0]
        return default
    
    def _join_filter(self, items, separator=", "):
        """Join items with separator"""
        if isinstance(items, list):
            return separator.join(str(item) for item in items)
        return str(items)
    
    def _primary_colors_filter(self, colors_data):
        """Extract primary colors from atoms color data"""
        if isinstance(colors_data, dict) and 'primary' in colors_data:
            return [c['hex'] for c in colors_data['primary'][:5]]
        return []
    
    def _visual_tone_filter(self, visual_tone_data):
        """Extract visual tone description"""
        if isinstance(visual_tone_data, dict):
            return visual_tone_data.get('primary', 'neutral')
        return 'neutral'


def main():
    parser = argparse.ArgumentParser(description='Generate prompts for brand deliverables')
    parser.add_argument('--concept', required=True, help='Path to brand concept JSON')
    parser.add_argument('--territory', help='Path to territory JSON')
    parser.add_argument('--system', help='Path to brand system JSON')
    parser.add_argument('--expr', help='Path to expression matrix JSON')
    parser.add_argument('--atoms', default='atoms/merged.json', help='Path to atoms JSON')
    parser.add_argument('--deliverable', required=True, help='Deliverable template name')
    parser.add_argument('--templates', default='compose/templates', help='Templates directory')
    parser.add_argument('--outdir', default='outputs/prompts', help='Output directory')
    
    args = parser.parse_args()
    
    # Validate required files
    if not os.path.exists(args.concept):
        print(f"Error: Concept file not found: {args.concept}")
        return 1
    
    if not os.path.exists(args.atoms):
        print(f"Error: Atoms file not found: {args.atoms}")
        return 1
    
    # Create prompt kitchen
    kitchen = PromptKitchen(args.templates)
    
    try:
        result = kitchen.compose_deliverable_prompts(
            concept_path=args.concept,
            territory_path=args.territory,
            system_path=args.system,
            expr_path=args.expr,
            atoms_path=args.atoms,
            deliverable=args.deliverable,
            output_dir=args.outdir
        )
        
        print(f"\n🎯 Prompt Generation Summary:")
        print(f"   Deliverable: {result['deliverable']}")
        print(f"   Variants: {len(result['variants'])}")
        print(f"   Output files: {len(result['output_files'])}")
        
        return 0
        
    except Exception as e:
        print(f"Error generating prompts: {e}")
        return 1


if __name__ == "__main__":
    exit(main())