#!/usr/bin/env python3
"""
Brand Synthesis Engine
Generates complete brand systems from mixed style vectors
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import colorsys
import math
from datetime import datetime

# Import the StyleVector for mixing capabilities
from style_vector import StyleVector

class BrandSynthesizer:
    """
    Synthesizes complete brand systems from multiple style vectors
    """
    
    def __init__(self, data_path: str = "content/data.json"):
        """Initialize the brand synthesizer"""
        self.data_path = Path(data_path)
        self.style_vector = StyleVector()
        self.load_data()
    
    def load_data(self):
        """Load the content data"""
        if self.data_path.exists():
            with open(self.data_path, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {"items": [], "brands": []}
    
    def save_data(self):
        """Save data back to file"""
        with open(self.data_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def synthesize(self, 
                   image_ids: List[str], 
                   brief: Optional[Dict] = None,
                   weights: Optional[List[float]] = None) -> Dict:
        """
        Main synthesis method - creates a complete brand system
        
        Args:
            image_ids: List of image IDs from data.json
            brief: Optional brand brief with name, category, audience, avoid_styles
            weights: Optional weights for each image (defaults to equal)
        
        Returns:
            Complete brand specification
        """
        # Get style vectors for selected images
        style_vectors = []
        for img_id in image_ids:
            item = self._get_item_by_id(img_id)
            if item and 'style_vector' in item:
                style_vectors.append(item['style_vector'])
        
        if not style_vectors:
            raise ValueError("No valid style vectors found for given image IDs")
        
        # Mix style vectors
        if weights is None:
            weights = [1.0 / len(style_vectors)] * len(style_vectors)
        
        # For now, manually mix the vectors since they're dictionaries
        # TODO: Could enhance StyleVector.mix to handle dict input
        mixed_vector = self._mix_vector_dicts(style_vectors, weights)
        
        # Generate brand specification
        brand_spec = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat(),
            "name": brief.get('name', 'Untitled Brand') if brief else 'Untitled Brand',
            "brief": brief or {},
            "source_images": image_ids,
            "weights": weights,
            "style_vector": mixed_vector
        }
        
        # Generate color palette
        brand_spec["colors"] = self._generate_color_palette(mixed_vector, brief)
        
        # Generate typography suggestions
        brand_spec["typography"] = self._generate_typography(mixed_vector, brief)
        
        # Generate spacing system
        brand_spec["spacing"] = self._generate_spacing_system(mixed_vector)
        
        # Generate brand personality
        brand_spec["personality"] = self._generate_personality(mixed_vector, brief)
        
        # Validate accessibility
        accessibility = self.validate_accessibility(brand_spec)
        brand_spec["accessibility"] = accessibility
        
        return brand_spec
    
    def _get_item_by_id(self, item_id: str) -> Optional[Dict]:
        """Get an item from data by ID"""
        for item in self.data.get('items', []):
            if item.get('id') == item_id:
                return item
        return None
    
    def _mix_vector_dicts(self, vectors: List[Dict], weights: List[float]) -> Dict:
        """Mix style vector dictionaries with weights"""
        if not vectors or not weights or len(vectors) != len(weights):
            raise ValueError("Invalid vectors or weights for mixing")
        
        # Initialize mixed vector
        mixed = {
            'energy': 0.0,
            'sophistication': 0.0,
            'density': 0.0,
            'temperature': 0.0,
            'era': 0.0,
            'dominant_colors': []
        }
        
        # Mix numeric values
        for key in ['energy', 'sophistication', 'density', 'temperature', 'era']:
            weighted_sum = 0.0
            for vector, weight in zip(vectors, weights):
                weighted_sum += vector.get(key, 0.5) * weight
            mixed[key] = weighted_sum
        
        # Collect and mix colors
        all_colors = []
        for vector, weight in zip(vectors, weights):
            colors = vector.get('dominant_colors', [])
            for color in colors:
                all_colors.append(color)
        
        # Remove duplicates and limit to reasonable number
        unique_colors = list(dict.fromkeys(all_colors))  # Preserve order, remove dupes
        mixed['dominant_colors'] = unique_colors[:8]  # Limit to 8 colors
        
        return mixed
    
    def _generate_color_palette(self, vector: Dict, brief: Optional[Dict]) -> Dict:
        """Generate accessible color palette from style vector"""
        colors = vector.get('dominant_colors', [])
        
        if len(colors) < 5:
            # Generate additional colors if needed
            colors = self._expand_color_palette(colors)
        
        # Sort by brightness for better organization
        sorted_colors = sorted(colors, key=lambda c: self._get_brightness(c))
        
        # Create palette with accessibility in mind
        palette = {
            "primary": sorted_colors[2],  # Mid-brightness for versatility
            "secondary": sorted_colors[1],  # Slightly darker
            "accent": self._adjust_saturation(sorted_colors[3], 1.2),  # Brighter, more saturated
            "neutral_dark": self._ensure_dark_enough(sorted_colors[0]),  # Darkest
            "neutral_light": self._ensure_light_enough(sorted_colors[-1])  # Lightest
        }
        
        # Ensure WCAG compliance
        palette = self._ensure_wcag_compliance(palette)
        
        return palette
    
    def _expand_color_palette(self, colors: List[str]) -> List[str]:
        """Expand color palette to 5 colors"""
        while len(colors) < 5:
            # Generate complementary or analogous colors
            base_color = colors[0]
            h, s, v = self._hex_to_hsv(base_color)
            
            # Add analogous color
            new_h = (h + 30/360) % 1.0
            new_color = self._hsv_to_hex(new_h, s * 0.8, v * 0.9)
            colors.append(new_color)
            
            if len(colors) < 5:
                # Add complementary color
                comp_h = (h + 0.5) % 1.0
                comp_color = self._hsv_to_hex(comp_h, s * 0.5, v)
                colors.append(comp_color)
        
        return colors[:5]
    
    def _ensure_wcag_compliance(self, palette: Dict) -> Dict:
        """Ensure color palette meets WCAG AA standards"""
        # Check contrast between primary and neutral_light
        primary_lum = self._get_relative_luminance(palette['primary'])
        light_lum = self._get_relative_luminance(palette['neutral_light'])
        
        contrast = self._calculate_contrast(primary_lum, light_lum)
        
        if contrast < 4.5:  # WCAG AA standard for normal text
            # Adjust neutral_light to be lighter
            palette['neutral_light'] = self._lighten_color(palette['neutral_light'], 0.2)
        
        # Check contrast between neutral_dark and neutral_light
        dark_lum = self._get_relative_luminance(palette['neutral_dark'])
        contrast = self._calculate_contrast(dark_lum, light_lum)
        
        if contrast < 7:  # Higher standard for primary text
            # Darken the dark color
            palette['neutral_dark'] = self._darken_color(palette['neutral_dark'], 0.3)
        
        return palette
    
    def _generate_typography(self, vector: Dict, brief: Optional[Dict]) -> Dict:
        """Generate typography recommendations based on style vector"""
        energy = vector.get('energy', 0.5)
        sophistication = vector.get('sophistication', 0.5)
        era = vector.get('era', 0.5)
        
        # Font suggestions based on metrics
        if sophistication > 0.7:
            if era < 0.4:
                heading_font = "Playfair Display, Georgia, serif"
                body_font = "Crimson Pro, Georgia, serif"
            else:
                heading_font = "Raleway, 'Helvetica Neue', sans-serif"
                body_font = "Inter, -apple-system, sans-serif"
        elif energy > 0.7:
            heading_font = "Montserrat, 'Arial Black', sans-serif"
            body_font = "Open Sans, Arial, sans-serif"
        else:
            heading_font = "Roboto, Helvetica, sans-serif"
            body_font = "Roboto, Helvetica, sans-serif"
        
        # Weight based on energy
        heading_weight = "700" if energy > 0.5 else "600"
        body_weight = "400"
        
        return {
            "heading": {
                "family": heading_font,
                "weight": heading_weight,
                "letter_spacing": "-0.02em" if sophistication > 0.6 else "0"
            },
            "body": {
                "family": body_font,
                "weight": body_weight,
                "line_height": "1.6" if sophistication > 0.5 else "1.5"
            },
            "scale": 1.25 if energy > 0.6 else 1.2  # Type scale ratio
        }
    
    def _generate_spacing_system(self, vector: Dict) -> Dict:
        """Generate spacing system based on style vector"""
        density = vector.get('density', 0.5)
        
        # Base unit depends on density
        base_unit = 8 if density < 0.6 else 4
        
        # Scale based on density (more dense = smaller scale)
        if density < 0.3:
            scale = [0.25, 0.5, 1, 2, 3, 5, 8, 13]  # Generous spacing
        elif density < 0.7:
            scale = [0.5, 1, 1.5, 2, 3, 5, 8]  # Balanced
        else:
            scale = [0.5, 1, 1.5, 2, 3, 4]  # Compact
        
        return {
            "unit": f"{base_unit}px",
            "scale": scale,
            "grid": base_unit * 2  # Grid unit for layouts
        }
    
    def _generate_personality(self, vector: Dict, brief: Optional[Dict]) -> Dict:
        """Generate brand personality traits"""
        energy = vector.get('energy', 0.5)
        sophistication = vector.get('sophistication', 0.5)
        temperature = vector.get('temperature', 0.5)
        era = vector.get('era', 0.5)
        
        # Generate traits based on metrics
        traits = []
        
        if energy > 0.7:
            traits.extend(['dynamic', 'bold', 'energetic'])
        elif energy < 0.3:
            traits.extend(['calm', 'serene', 'thoughtful'])
        else:
            traits.extend(['balanced', 'approachable', 'steady'])
        
        if sophistication > 0.7:
            traits.extend(['refined', 'elegant', 'premium'])
        elif sophistication < 0.3:
            traits.extend(['casual', 'friendly', 'accessible'])
        
        if temperature > 0.7:
            traits.append('warm')
        elif temperature < 0.3:
            traits.append('cool')
        
        if era > 0.7:
            traits.append('modern')
        elif era < 0.3:
            traits.append('classic')
        
        # Voice guidelines
        if sophistication > 0.6:
            voice = "Professional and refined, with attention to detail"
        elif energy > 0.6:
            voice = "Enthusiastic and direct, with a sense of urgency"
        else:
            voice = "Friendly and conversational, building trust"
        
        # Do's and don'ts based on personality
        dos = []
        donts = []
        
        if sophistication > 0.6:
            dos.append("Use precise language")
            donts.append("Avoid colloquialisms")
        
        if energy > 0.6:
            dos.append("Use active voice")
            dos.append("Be concise and punchy")
            donts.append("No long-winded explanations")
        else:
            dos.append("Take time to explain")
            donts.append("Don't rush the reader")
        
        if brief and 'avoid_styles' in brief:
            for style in brief['avoid_styles']:
                donts.append(f"Avoid {style} style")
        
        return {
            "traits": list(set(traits))[:5],  # Limit to 5 unique traits
            "voice": voice,
            "do": dos[:3],  # Top 3 do's
            "dont": donts[:3]  # Top 3 don'ts
        }
    
    def validate_accessibility(self, brand_spec: Dict) -> Dict:
        """
        Validate accessibility of brand specification
        
        Returns dict with:
        - passed: boolean
        - issues: list of issues found
        - suggestions: list of improvements
        """
        issues = []
        suggestions = []
        
        colors = brand_spec.get('colors', {})
        
        # Check contrast ratios
        contrasts = [
            ('primary', 'neutral_light', 4.5, 'normal text'),
            ('neutral_dark', 'neutral_light', 7.0, 'heading text'),
            ('accent', 'neutral_light', 3.0, 'large text'),
        ]
        
        for fg_key, bg_key, min_ratio, text_type in contrasts:
            if fg_key in colors and bg_key in colors:
                fg_lum = self._get_relative_luminance(colors[fg_key])
                bg_lum = self._get_relative_luminance(colors[bg_key])
                ratio = self._calculate_contrast(fg_lum, bg_lum)
                
                if ratio < min_ratio:
                    issues.append(f"{fg_key}/{bg_key} contrast {ratio:.1f}:1 fails WCAG AA for {text_type} (needs {min_ratio}:1)")
                    suggestions.append(f"Adjust {fg_key} or {bg_key} to improve contrast")
        
        # Check grayscale compatibility
        grayscale_distinct = self._check_grayscale_distinction(list(colors.values()))
        if not grayscale_distinct:
            issues.append("Colors may not be distinguishable in grayscale")
            suggestions.append("Ensure colors differ in brightness, not just hue")
        
        # Check color count
        if len(colors) > 5:
            suggestions.append("Consider reducing color palette to 5 or fewer colors for consistency")
        
        return {
            "passed": len(issues) == 0,
            "wcag_aa": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "contrast_ratios": self._get_all_contrast_ratios(colors)
        }
    
    def generate_alternatives(self, base_spec: Dict, count: int = 3) -> List[Dict]:
        """
        Generate alternative brand specifications
        
        Creates variations by:
        - Shifting style vector slightly
        - Rotating color palette
        - Adjusting typography weights
        """
        alternatives = []
        
        for i in range(count):
            alt_spec = json.loads(json.dumps(base_spec))  # Deep copy
            alt_spec['id'] = str(uuid.uuid4())
            alt_spec['variant'] = i + 1
            
            # Shift style vector
            if 'style_vector' in alt_spec:
                vector = alt_spec['style_vector']
                
                # Adjust metrics slightly
                shift_amount = 0.1 * (i + 1)
                vector['energy'] = min(1, max(0, vector.get('energy', 0.5) + shift_amount * (0.5 - i/count)))
                vector['sophistication'] = min(1, max(0, vector.get('sophistication', 0.5) + shift_amount * (i/count - 0.5)))
                
                # Rotate colors
                if 'dominant_colors' in vector:
                    colors = vector['dominant_colors']
                    # Rotate hue of all colors
                    rotated = []
                    for color in colors:
                        h, s, v = self._hex_to_hsv(color)
                        new_h = (h + (i + 1) * 0.1) % 1.0
                        rotated.append(self._hsv_to_hex(new_h, s, v))
                    vector['dominant_colors'] = rotated
            
            # Regenerate components with shifted vector
            if 'style_vector' in alt_spec:
                alt_spec['colors'] = self._generate_color_palette(
                    alt_spec['style_vector'], 
                    alt_spec.get('brief')
                )
                alt_spec['typography'] = self._generate_typography(
                    alt_spec['style_vector'],
                    alt_spec.get('brief')
                )
                
                # Vary typography weights
                if i == 0:
                    alt_spec['typography']['heading']['weight'] = "800"
                elif i == 2:
                    alt_spec['typography']['heading']['weight'] = "500"
                
                # Revalidate accessibility
                alt_spec['accessibility'] = self.validate_accessibility(alt_spec)
            
            alternatives.append(alt_spec)
        
        return alternatives
    
    # Helper methods for color operations
    
    def _hex_to_hsv(self, hex_color: str) -> Tuple[float, float, float]:
        """Convert hex to HSV"""
        hex_color = hex_color.lstrip('#')
        r, g, b = [int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4)]
        return colorsys.rgb_to_hsv(r, g, b)
    
    def _hsv_to_hex(self, h: float, s: float, v: float) -> str:
        """Convert HSV to hex"""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return '#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255))
    
    def _get_brightness(self, hex_color: str) -> float:
        """Get brightness of a color (0-1)"""
        h, s, v = self._hex_to_hsv(hex_color)
        return v
    
    def _get_relative_luminance(self, hex_color: str) -> float:
        """Calculate relative luminance for WCAG contrast"""
        hex_color = hex_color.lstrip('#')
        r, g, b = [int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4)]
        
        # Apply gamma correction
        r = r/12.92 if r <= 0.03928 else ((r + 0.055)/1.055) ** 2.4
        g = g/12.92 if g <= 0.03928 else ((g + 0.055)/1.055) ** 2.4
        b = b/12.92 if b <= 0.03928 else ((b + 0.055)/1.055) ** 2.4
        
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    def _calculate_contrast(self, lum1: float, lum2: float) -> float:
        """Calculate contrast ratio between two luminance values"""
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        return (lighter + 0.05) / (darker + 0.05)
    
    def _adjust_saturation(self, hex_color: str, factor: float) -> str:
        """Adjust saturation of a color"""
        h, s, v = self._hex_to_hsv(hex_color)
        s = min(1, s * factor)
        return self._hsv_to_hex(h, s, v)
    
    def _ensure_dark_enough(self, hex_color: str) -> str:
        """Ensure color is dark enough for text"""
        h, s, v = self._hex_to_hsv(hex_color)
        if v > 0.3:
            v = 0.3
        return self._hsv_to_hex(h, s, v)
    
    def _ensure_light_enough(self, hex_color: str) -> str:
        """Ensure color is light enough for background"""
        h, s, v = self._hex_to_hsv(hex_color)
        if v < 0.9:
            v = 0.9
        if s > 0.1:
            s = 0.1
        return self._hsv_to_hex(h, s, v)
    
    def _lighten_color(self, hex_color: str, amount: float) -> str:
        """Lighten a color"""
        h, s, v = self._hex_to_hsv(hex_color)
        v = min(1, v + amount)
        s = max(0, s - amount/2)  # Reduce saturation as we lighten
        return self._hsv_to_hex(h, s, v)
    
    def _darken_color(self, hex_color: str, amount: float) -> str:
        """Darken a color"""
        h, s, v = self._hex_to_hsv(hex_color)
        v = max(0, v - amount)
        return self._hsv_to_hex(h, s, v)
    
    def _check_grayscale_distinction(self, colors: List[str]) -> bool:
        """Check if colors are distinguishable in grayscale"""
        brightnesses = [self._get_brightness(c) for c in colors]
        
        # Check if there's enough variance
        for i, b1 in enumerate(brightnesses):
            for b2 in brightnesses[i+1:]:
                if abs(b1 - b2) < 0.15:  # Too similar
                    return False
        return True
    
    def _get_all_contrast_ratios(self, colors: Dict) -> Dict:
        """Get all contrast ratios between color pairs"""
        ratios = {}
        color_items = list(colors.items())
        
        for i, (name1, color1) in enumerate(color_items):
            for name2, color2 in color_items[i+1:]:
                lum1 = self._get_relative_luminance(color1)
                lum2 = self._get_relative_luminance(color2)
                ratio = self._calculate_contrast(lum1, lum2)
                ratios[f"{name1}/{name2}"] = round(ratio, 1)
        
        return ratios


# Integration function for simple_server.py
def synthesize_brand_from_images(image_ids: List[str], 
                                  brief: Optional[Dict] = None,
                                  weights: Optional[List[float]] = None) -> Dict:
    """
    Convenience function to synthesize a brand from image IDs
    """
    synthesizer = BrandSynthesizer()
    brand_spec = synthesizer.synthesize(image_ids, brief, weights)
    
    # Save to data.json under brands key
    if 'brands' not in synthesizer.data:
        synthesizer.data['brands'] = []
    
    synthesizer.data['brands'].append(brand_spec)
    synthesizer.save_data()
    
    return brand_spec


if __name__ == "__main__":
    # Test the synthesizer
    import sys
    
    if len(sys.argv) > 1:
        # Get image IDs from command line
        image_ids = sys.argv[1].split(',')
        
        # Optional brief
        brief = {
            "name": "Test Brand",
            "category": "Technology",
            "audience": "Developers",
            "avoid_styles": ["corporate", "playful"]
        }
        
        synthesizer = BrandSynthesizer()
        
        try:
            # Generate main brand
            brand = synthesizer.synthesize(image_ids, brief)
            print(json.dumps(brand, indent=2))
            
            # Generate alternatives
            print("\n=== Generating 3 alternatives ===")
            alternatives = synthesizer.generate_alternatives(brand, count=3)
            
            for i, alt in enumerate(alternatives):
                print(f"\n--- Alternative {i+1} ---")
                print(f"Colors: {alt['colors']}")
                print(f"Typography: {alt['typography']['heading']['family']}")
                print(f"Accessibility: {alt['accessibility']['passed']}")
                
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Usage: python synthesis_engine.py img_1,img_2,img_3")