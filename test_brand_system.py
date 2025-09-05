#!/usr/bin/env python3
"""
Test script for the brand generation system
Shows all components working together
"""

import json
from semantic_analyzer import analyze_semantic
from datetime import datetime

def test_brand_system(image_path: str, description: str = ""):
    """Test the brand system with just semantic analysis for now"""
    
    print(f"\n{'='*50}")
    print(f"BRAND GENERATION FROM SOURCE MATERIAL")
    print(f"{'='*50}")
    print(f"\nSource: {image_path}")
    print(f"Description: {description}")
    
    # Step 1: Semantic Analysis
    print(f"\n{'='*30}")
    print("Step 1: Analyzing Source Material")
    print(f"{'='*30}")
    
    semantic = analyze_semantic(image_path, description)
    
    if 'error' not in semantic:
        # Extract key information
        colors = semantic.get('colors', {}).get('most_common', [])
        composition = semantic.get('composition', {})
        visual_props = semantic.get('visual_properties', {})
        
        print(f"\n✅ Source Analysis Complete:")
        print(f"  - Found {len(colors)} dominant colors")
        print(f"  - {composition.get('orientation', 'unknown')} orientation")
        print(f"  - {visual_props.get('darkness', 'medium')} overall tone")
        
        # Step 2: Generate Brand Concept
        print(f"\n{'='*30}")
        print("Step 2: Brand Concept Generation")
        print(f"{'='*30}")
        
        brand_concept = generate_brand_concept(semantic, description)
        
        print(f"\n🎯 Brand Concept:")
        print(f"  Essence: {brand_concept['essence']}")
        print(f"  Personality: {brand_concept['personality']}")
        print(f"  Archetype: {brand_concept['archetype']}")
        
        # Step 3: Color System
        print(f"\n{'='*30}")
        print("Step 3: Color System Development")
        print(f"{'='*30}")
        
        color_system = create_color_system(colors)
        
        print(f"\n🎨 Color Palette:")
        print(f"  Primary: {color_system['primary']}")
        print(f"  Secondary: {color_system['secondary']}")
        print(f"  Accent: {color_system['accent']}")
        print(f"  Mood: {color_system['mood']}")
        
        # Step 4: Typography Direction
        print(f"\n{'='*30}")
        print("Step 4: Typography Direction")
        print(f"{'='*30}")
        
        typography = determine_typography(visual_props, brand_concept)
        
        print(f"\n📝 Typography:")
        print(f"  Primary: {typography['primary']}")
        print(f"  Secondary: {typography['secondary']}")
        print(f"  Character: {typography['character']}")
        
        # Step 5: Visual Style
        print(f"\n{'='*30}")
        print("Step 5: Visual Style Guidelines")
        print(f"{'='*30}")
        
        visual_style = define_visual_style(visual_props, composition)
        
        print(f"\n✨ Visual Style:")
        print(f"  Approach: {visual_style['approach']}")
        print(f"  Energy: {visual_style['energy']}")
        print(f"  Balance: {visual_style['balance']}")
        
        # Step 6: Brand Voice
        print(f"\n{'='*30}")
        print("Step 6: Brand Voice Development")
        print(f"{'='*30}")
        
        brand_voice = create_brand_voice(brand_concept, visual_props)
        
        print(f"\n🗣️ Brand Voice:")
        print(f"  Tone: {brand_voice['tone']}")
        print(f"  Style: {brand_voice['style']}")
        print(f"  Example: \"{brand_voice['example']}\"")
        
        # Summary
        print(f"\n{'='*50}")
        print("BRAND GENERATION COMPLETE")
        print(f"{'='*50}")
        
        print(f"\n📊 Brand Summary:")
        print(f"  A {brand_concept['personality']} brand with {color_system['mood']} colors,")
        print(f"  {typography['character']} typography, and {brand_voice['tone']} voice.")
        print(f"  Visual style is {visual_style['approach']} with {visual_style['energy']} energy.")
        
        return {
            'semantic_analysis': semantic,
            'brand_concept': brand_concept,
            'color_system': color_system,
            'typography': typography,
            'visual_style': visual_style,
            'brand_voice': brand_voice,
            'generated_at': datetime.now().isoformat()
        }
    
    else:
        print(f"❌ Error: {semantic.get('error')}")
        return None

def generate_brand_concept(semantic: dict, description: str) -> dict:
    """Generate brand concept from semantic analysis"""
    
    visual_props = semantic.get('visual_properties', {})
    brightness = visual_props.get('brightness', 0.5)
    contrast = visual_props.get('contrast', 0.5)
    saturation = visual_props.get('saturation', 0.5)
    
    # Determine personality based on visual properties
    if brightness > 0.7 and saturation > 0.5:
        personality = "energetic and optimistic"
        archetype = "Jester"
    elif brightness < 0.3:
        personality = "mysterious and sophisticated"
        archetype = "Magician"
    elif saturation < 0.3:
        personality = "minimal and refined"
        archetype = "Sage"
    elif contrast > 0.6:
        personality = "bold and confident"
        archetype = "Hero"
    else:
        personality = "balanced and approachable"
        archetype = "Everyman"
    
    # Generate essence
    if "motivational" in description.lower():
        essence = "empowerment through action"
    elif "luxury" in description.lower():
        essence = "refined excellence"
    elif "natural" in description.lower():
        essence = "authentic connection"
    else:
        essence = "meaningful experiences"
    
    return {
        'essence': essence,
        'personality': personality,
        'archetype': archetype
    }

def create_color_system(colors: list) -> dict:
    """Create color system from analyzed colors"""
    
    if not colors:
        return {
            'primary': '#007BFF',
            'secondary': '#6C757D',
            'accent': '#FFC107',
            'mood': 'professional'
        }
    
    # Use first color as primary
    primary = colors[0]['hex'] if colors else '#007BFF'
    
    # Use second color as secondary or create variation
    secondary = colors[1]['hex'] if len(colors) > 1 else '#6C757D'
    
    # Use third as accent or pick a vibrant one
    accent = '#FFC107'
    for color in colors:
        if color.get('saturation', 0) > 0.6:
            accent = color['hex']
            break
    
    # Determine mood
    avg_brightness = sum(c.get('brightness', 0.5) for c in colors[:3]) / min(3, len(colors))
    avg_saturation = sum(c.get('saturation', 0.5) for c in colors[:3]) / min(3, len(colors))
    
    if avg_brightness > 0.7 and avg_saturation > 0.5:
        mood = "vibrant and energetic"
    elif avg_brightness < 0.3:
        mood = "dramatic and bold"
    elif avg_saturation < 0.3:
        mood = "sophisticated and minimal"
    else:
        mood = "balanced and versatile"
    
    return {
        'primary': primary,
        'secondary': secondary,
        'accent': accent,
        'mood': mood
    }

def determine_typography(visual_props: dict, brand_concept: dict) -> dict:
    """Determine typography direction"""
    
    archetype = brand_concept.get('archetype', 'Everyman')
    brightness = visual_props.get('brightness', 0.5)
    
    # Map archetype to typography
    typography_map = {
        'Sage': ('Serif - elegant and trustworthy', 'Sans-serif - clean and readable', 'sophisticated'),
        'Hero': ('Sans-serif - bold and strong', 'Sans-serif - supportive', 'powerful'),
        'Jester': ('Display - playful and unique', 'Sans-serif - friendly', 'expressive'),
        'Magician': ('Serif - mysterious', 'Sans-serif - modern', 'intriguing'),
        'Everyman': ('Sans-serif - approachable', 'Sans-serif - readable', 'friendly')
    }
    
    primary, secondary, character = typography_map.get(archetype, 
        ('Sans-serif - versatile', 'Serif - supportive', 'balanced'))
    
    return {
        'primary': primary,
        'secondary': secondary,
        'character': character
    }

def define_visual_style(visual_props: dict, composition: dict) -> dict:
    """Define visual style guidelines"""
    
    brightness = visual_props.get('brightness', 0.5)
    contrast = visual_props.get('contrast', 0.5)
    orientation = composition.get('orientation', 'square')
    
    # Determine approach
    if contrast > 0.6:
        approach = "bold and impactful"
    elif brightness > 0.7:
        approach = "light and airy"
    elif brightness < 0.3:
        approach = "dark and moody"
    else:
        approach = "balanced and harmonious"
    
    # Determine energy
    if contrast > 0.5 and visual_props.get('saturation', 0.5) > 0.5:
        energy = "high"
    elif contrast < 0.3 and brightness > 0.5:
        energy = "calm"
    else:
        energy = "moderate"
    
    # Determine balance
    if orientation == 'square':
        balance = "symmetrical"
    else:
        balance = "dynamic"
    
    return {
        'approach': approach,
        'energy': energy,
        'balance': balance
    }

def create_brand_voice(brand_concept: dict, visual_props: dict) -> dict:
    """Create brand voice guidelines"""
    
    personality = brand_concept.get('personality', 'balanced')
    brightness = visual_props.get('brightness', 0.5)
    
    # Determine tone based on personality
    if 'energetic' in personality:
        tone = "enthusiastic and inspiring"
        style = "active and engaging"
        example = "Let's make something amazing together!"
    elif 'mysterious' in personality:
        tone = "intriguing and sophisticated"
        style = "thoughtful and refined"
        example = "Discover what lies beyond the ordinary."
    elif 'minimal' in personality:
        tone = "clear and direct"
        style = "simple and precise"
        example = "Less noise. More clarity."
    elif 'bold' in personality:
        tone = "confident and assertive"
        style = "strong and decisive"
        example = "Stand out. Lead the way."
    else:
        tone = "friendly and approachable"
        style = "conversational and warm"
        example = "We're here to help you succeed."
    
    return {
        'tone': tone,
        'style': style,
        'example': example
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        description = sys.argv[2] if len(sys.argv) > 2 else ""
        
        result = test_brand_system(image_path, description)
        
        if result:
            # Save result to file
            output_file = 'brand_generation_result.json'
            with open(output_file, 'w') as f:
                # Convert to serializable format
                result_clean = json.loads(json.dumps(result, default=str))
                json.dump(result_clean, f, indent=2)
            print(f"\n💾 Full results saved to: {output_file}")
    else:
        print("Usage: python test_brand_system.py <image_path> [description]")