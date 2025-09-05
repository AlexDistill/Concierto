#!/usr/bin/env python3
"""
Optimized Source-to-Brand Translation Layer
Fast brand generation using optimized components
"""

import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime
import colorsys
from deep_source_analyzer_optimized import DeepSourceAnalyzerOptimized
from vibe_mapper_optimized import VibeMapperOptimized

class BrandTranslatorOptimized:
    """
    Fast brand translation using optimized analysis components
    Focuses on essential brand elements for speed
    """
    
    def __init__(self):
        self.deep_analyzer = DeepSourceAnalyzerOptimized()
        self.vibe_mapper = VibeMapperOptimized()
        
    def translate_source_to_brand(self, image_path: str, description: str = "") -> Dict:
        """
        Fast source-to-brand translation with essential elements
        """
        try:
            # Get optimized analyses
            deep_analysis = self.deep_analyzer.analyze_source_material(image_path, description)
            vibe_analysis = self.vibe_mapper.map_vibe_intensity(image_path, description)
            
            if 'error' in deep_analysis or 'error' in vibe_analysis:
                return {'error': 'Analysis failed'}
            
            # Fast brand translation
            brand_translation = {
                'analyzed_at': datetime.now().isoformat(),
                'source_path': str(image_path),
                'brand_concept': self._translate_to_brand_concept_fast(deep_analysis, vibe_analysis),
                'color_system': self._translate_to_color_system_fast(deep_analysis),
                'typography_system': self._translate_to_typography_fast(vibe_analysis),
                'logo_direction': self._translate_to_logo_fast(deep_analysis, vibe_analysis),
                'visual_style': self._translate_to_visual_style_fast(deep_analysis, vibe_analysis),
                'brand_voice': self._translate_to_brand_voice_fast(vibe_analysis),
                'implementation_priority': self._create_implementation_fast(deep_analysis, vibe_analysis),
                'analysis_type': 'brand_translation_optimized_v1'
            }
            
            return brand_translation
            
        except Exception as e:
            return {
                'error': str(e),
                'analyzed_at': datetime.now().isoformat()
            }
    
    def _translate_to_brand_concept_fast(self, deep_analysis: Dict, vibe_analysis: Dict) -> Dict:
        """Fast brand concept generation"""
        
        # Get archetype from deep analysis
        archetype = deep_analysis.get('brand_dna', {}).get('dominant_archetype', 'everyman')
        
        # Get vibe signature
        vibe_signature = vibe_analysis.get('vibe_spectrum', {}).get('vibe_signature', 'balanced')
        
        # Get energy level
        energy = vibe_analysis.get('emotional_intensity', {}).get('intensity_level', 'medium')
        
        # Fast concept mapping
        concept_map = {
            'innocent': 'honest and approachable',
            'explorer': 'adventurous and bold',
            'sage': 'wise and trustworthy',
            'hero': 'strong and reliable',
            'outlaw': 'rebellious and authentic',
            'everyman': 'relatable and dependable'
        }
        
        essence = concept_map.get(archetype, 'meaningful and distinctive')
        
        # Create personality based on vibe
        personality_traits = []
        if 'sophistication' in vibe_signature:
            personality_traits.append('refined')
        if 'energy' in vibe_signature:
            personality_traits.append('dynamic')
        if 'warmth' in vibe_signature:
            personality_traits.append('welcoming')
        
        if not personality_traits:
            personality_traits = ['balanced', 'professional']
        
        return {
            'core_essence': essence,
            'brand_archetype': archetype,
            'personality_traits': personality_traits,
            'energy_level': energy,
            'brand_promise': f"We deliver {essence} experiences"
        }
    
    def _translate_to_color_system_fast(self, deep_analysis: Dict) -> Dict:
        """Fast color system creation"""
        
        # Get colors from analysis
        colors = deep_analysis.get('colors', {}).get('most_common', [])
        brandable = deep_analysis.get('brandable_elements', {})
        
        if colors:
            primary = colors[0]['hex']
            secondary = colors[1]['hex'] if len(colors) > 1 else self._generate_secondary_fast(primary)
            
            # Quick accent color
            accent = '#FFC107'  # Default
            for color in colors:
                if color.get('saturation', 0) > 0.6:
                    accent = color['hex']
                    break
            
            mood = brandable.get('palette_mood', 'balanced')
            
        else:
            # Fallback palette
            primary = '#007BFF'
            secondary = '#6C757D'
            accent = '#FFC107'
            mood = 'professional'
        
        return {
            'primary_palette': {
                'brand_primary': primary,
                'brand_secondary': secondary,
                'accent': accent,
                'mood': mood
            },
            'usage_guidelines': {
                'primary_usage': 'Logo, main CTAs, key brand elements',
                'secondary_usage': 'Supporting elements, backgrounds',
                'accent_usage': 'Highlights, calls-to-action'
            }
        }
    
    def _generate_secondary_fast(self, primary_hex: str) -> str:
        """Generate secondary color from primary"""
        try:
            # Convert hex to RGB
            primary_hex = primary_hex.lstrip('#')
            r = int(primary_hex[0:2], 16) / 255
            g = int(primary_hex[2:4], 16) / 255
            b = int(primary_hex[4:6], 16) / 255
            
            # Convert to HSV
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            
            # Create analogous color (shift hue slightly, reduce saturation)
            new_h = (h + 0.1) % 1.0
            new_s = s * 0.7
            new_v = min(1.0, v * 1.1)
            
            # Convert back
            r, g, b = colorsys.hsv_to_rgb(new_h, new_s, new_v)
            return '#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255))
            
        except:
            return '#6C757D'  # Fallback
    
    def _translate_to_typography_fast(self, vibe_analysis: Dict) -> Dict:
        """Fast typography recommendations"""
        
        # Get sophistication and playfulness
        vibe_spectrum = vibe_analysis.get('vibe_spectrum', {})
        sophistication = vibe_spectrum.get('sophistication', {}).get('level', 'refined')
        playfulness = vibe_spectrum.get('playfulness', {}).get('level', 'balanced')
        
        # Fast typography mapping
        if sophistication == 'luxury':
            if playfulness == 'serious':
                primary = 'Serif - elegant and authoritative'
                character = 'sophisticated'
            else:
                primary = 'Sans-serif - modern luxury'
                character = 'refined'
        elif playfulness == 'playful':
            primary = 'Sans-serif - friendly and approachable'
            character = 'expressive'
        else:
            primary = 'Sans-serif - clean and professional'
            character = 'versatile'
        
        secondary = 'Sans-serif - readable body text'
        
        return {
            'primary_typeface': primary,
            'secondary_typeface': secondary,
            'character': character,
            'usage_guidelines': {
                'headings': 'Use primary typeface for impact',
                'body': 'Use secondary typeface for readability',
                'consistency': 'Maintain hierarchy across applications'
            }
        }
    
    def _translate_to_logo_fast(self, deep_analysis: Dict, vibe_analysis: Dict) -> Dict:
        """Fast logo direction"""
        
        archetype = deep_analysis.get('brand_dna', {}).get('dominant_archetype', 'everyman')
        layout_style = deep_analysis.get('layout_principles', {}).get('layout_style', 'balanced')
        energy = vibe_analysis.get('emotional_intensity', {}).get('intensity_level', 'medium')
        
        # Logo type mapping
        if archetype in ['sage', 'ruler']:
            logo_type = 'wordmark'  # Text-based
        elif energy == 'high':
            logo_type = 'symbol'  # Icon-based
        else:
            logo_type = 'combination'  # Text + symbol
        
        # Geometric approach
        if layout_style == 'vertical':
            geometric_approach = 'structured'
        elif energy == 'high':
            geometric_approach = 'dynamic'
        else:
            geometric_approach = 'balanced'
        
        return {
            'logo_type': logo_type,
            'geometric_approach': geometric_approach,
            'style_direction': f"{archetype}-inspired with {geometric_approach} geometry",
            'scalability': 'Designed for digital and print applications'
        }
    
    def _translate_to_visual_style_fast(self, deep_analysis: Dict, vibe_analysis: Dict) -> Dict:
        """Fast visual style guidelines"""
        
        brandable = deep_analysis.get('brandable_elements', {})
        visual_approach = brandable.get('visual_approach', 'balanced')
        
        energy = vibe_analysis.get('emotional_intensity', {}).get('intensity_level', 'medium')
        sophistication = vibe_analysis.get('vibe_spectrum', {}).get('sophistication', {}).get('level', 'refined')
        
        # Style mapping
        if sophistication == 'luxury':
            aesthetic = 'premium minimalist'
            imagery = 'refined and elegant'
        elif energy == 'high':
            aesthetic = 'bold and dynamic'
            imagery = 'energetic and vibrant'
        elif visual_approach == 'light':
            aesthetic = 'clean and airy'
            imagery = 'bright and optimistic'
        else:
            aesthetic = 'balanced contemporary'
            imagery = 'professional and approachable'
        
        return {
            'aesthetic_direction': aesthetic,
            'imagery_style': imagery,
            'visual_approach': visual_approach,
            'consistency_guidelines': 'Maintain visual coherence across all applications'
        }
    
    def _translate_to_brand_voice_fast(self, vibe_analysis: Dict) -> Dict:
        """Fast brand voice creation"""
        
        vibe_spectrum = vibe_analysis.get('vibe_spectrum', {})
        personality = vibe_analysis.get('brand_personality_mapping', {})
        
        # Get dominant personality trait
        if personality:
            dominant_trait = max(personality, key=personality.get)
        else:
            dominant_trait = 'competence'
        
        # Voice mapping
        voice_map = {
            'sincerity': {
                'tone': 'honest and warm',
                'style': 'conversational and genuine',
                'example': 'We believe in doing the right thing, always.'
            },
            'excitement': {
                'tone': 'energetic and inspiring',
                'style': 'active and engaging',
                'example': 'Ready to make something amazing happen?'
            },
            'competence': {
                'tone': 'professional and reliable',
                'style': 'clear and authoritative',
                'example': 'Trusted expertise you can count on.'
            },
            'sophistication': {
                'tone': 'refined and elegant',
                'style': 'polished and precise',
                'example': 'Excellence in every detail.'
            },
            'ruggedness': {
                'tone': 'strong and authentic',
                'style': 'direct and confident',
                'example': 'Built to last, built to perform.'
            }
        }
        
        voice_info = voice_map.get(dominant_trait, voice_map['competence'])
        
        return {
            'primary_tone': voice_info['tone'],
            'communication_style': voice_info['style'],
            'voice_example': voice_info['example'],
            'personality_base': dominant_trait
        }
    
    def _create_implementation_fast(self, deep_analysis: Dict, vibe_analysis: Dict) -> Dict:
        """Fast implementation priorities"""
        
        transferability = vibe_analysis.get('vibe_transferability', {})
        applications = transferability.get('brand_applications', ['logo_design', 'marketing_materials'])
        
        return {
            'phase_1_essentials': [
                'Logo design and variations',
                'Primary color palette implementation',
                'Typography system setup',
                'Brand voice guidelines'
            ],
            'phase_2_applications': [
                'Website design system',
                'Marketing material templates',
                'Social media guidelines'
            ],
            'recommended_applications': applications,
            'timeline': 'Phase 1: 1-2 weeks, Phase 2: 2-4 weeks'
        }


def translate_source_to_brand_optimized(image_path: str, description: str = "") -> Dict:
    """
    Fast source-to-brand translation using optimized components
    """
    translator = BrandTranslatorOptimized()
    return translator.translate_source_to_brand(image_path, description)


if __name__ == "__main__":
    import sys
    import time
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        description = sys.argv[2] if len(sys.argv) > 2 else ""
        
        print(f"Translating source to brand (optimized): {image_path}")
        
        start_time = time.time()
        result = translate_source_to_brand_optimized(image_path, description)
        elapsed = time.time() - start_time
        
        if result and 'error' not in result:
            print(f"\n=== OPTIMIZED BRAND TRANSLATION ({elapsed:.2f}s) ===")
            
            # Brand Concept
            if 'brand_concept' in result:
                concept = result['brand_concept']
                print(f"\n🎯 Brand Concept:")
                print(f"  Essence: {concept.get('core_essence', 'N/A')}")
                print(f"  Archetype: {concept.get('brand_archetype', 'N/A')}")
                print(f"  Traits: {', '.join(concept.get('personality_traits', []))}")
            
            # Color System
            if 'color_system' in result and 'primary_palette' in result['color_system']:
                palette = result['color_system']['primary_palette']
                print(f"\n🎨 Color System:")
                print(f"  Primary: {palette.get('brand_primary', 'N/A')}")
                print(f"  Secondary: {palette.get('brand_secondary', 'N/A')}")
                print(f"  Accent: {palette.get('accent', 'N/A')}")
                print(f"  Mood: {palette.get('mood', 'N/A')}")
            
            # Typography
            if 'typography_system' in result:
                typo = result['typography_system']
                print(f"\n📝 Typography:")
                print(f"  Primary: {typo.get('primary_typeface', 'N/A')}")
                print(f"  Character: {typo.get('character', 'N/A')}")
            
            # Logo Direction
            if 'logo_direction' in result:
                logo = result['logo_direction']
                print(f"\n🏷️  Logo Direction:")
                print(f"  Type: {logo.get('logo_type', 'N/A')}")
                print(f"  Approach: {logo.get('geometric_approach', 'N/A')}")
            
            # Brand Voice
            if 'brand_voice' in result:
                voice = result['brand_voice']
                print(f"\n🗣️  Brand Voice:")
                print(f"  Tone: {voice.get('primary_tone', 'N/A')}")
                print(f"  Example: \"{voice.get('voice_example', 'N/A')}\"")
            
            # Visual Style
            if 'visual_style' in result:
                style = result['visual_style']
                print(f"\n✨ Visual Style:")
                print(f"  Aesthetic: {style.get('aesthetic_direction', 'N/A')}")
                print(f"  Imagery: {style.get('imagery_style', 'N/A')}")
            
            print(f"\n⚡ Total Processing Time: {elapsed:.2f}s")
        else:
            print(f"Translation failed: {result.get('error', 'Unknown error')}")
    else:
        print("Usage: python brand_translator_optimized.py <image_path> [description]")