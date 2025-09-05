#!/usr/bin/env python3
"""
Fixed StyleVector class with improved color extraction
Properly captures vibrant colors and generates meaningful brand tokens
"""

import numpy as np
from PIL import Image
from typing import Dict, List, Tuple, Optional
import colorsys
from pathlib import Path
from collections import Counter

# Check for optional dependencies
try:
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. Using fallback color extraction.")

class StyleVector:
    """
    Fixed style vector with proper color extraction
    """
    
    def __init__(self, energy=0.5, sophistication=0.5, density=0.5, 
                 temperature=0.5, era=0.5, dominant_colors=None, color_palette=None):
        """
        Initialize style vector
        
        Args:
            energy: Visual energy level (0-1)
            sophistication: Design sophistication (0-1) 
            density: Content density (0-1)
            temperature: Color temperature (0-1, cool to warm)
            era: Design era (0-1, vintage to futuristic)
            dominant_colors: List of dominant color hex codes
            color_palette: Extended color palette with metadata
        """
        self.energy = max(0.0, min(1.0, energy))
        self.sophistication = max(0.0, min(1.0, sophistication))
        self.density = max(0.0, min(1.0, density))
        self.temperature = max(0.0, min(1.0, temperature))
        self.era = max(0.0, min(1.0, era))
        self.dominant_colors = dominant_colors or []
        self.color_palette = color_palette or {}
    
    @classmethod
    def from_image(cls, image_path):
        """
        Create style vector from image analysis with FIXED color extraction
        
        Args:
            image_path: Path to image file
            
        Returns:
            StyleVector instance
        """
        try:
            # Load and convert image
            img = Image.open(image_path).convert('RGB')
            img_array = np.array(img)
            
            # Extract comprehensive color palette
            color_data = cls._extract_comprehensive_colors(img_array)
            dominant_colors = color_data['dominant_colors']
            
            # Calculate style dimensions using the improved color data
            energy = cls._calculate_energy(img_array, dominant_colors)
            sophistication = cls._calculate_sophistication(dominant_colors, color_data)
            density = cls._calculate_density(img_array)
            temperature = cls._calculate_temperature(dominant_colors, color_data)
            era = cls._calculate_era(img_array, dominant_colors)
            
            return cls(
                energy=energy,
                sophistication=sophistication,
                density=density,
                temperature=temperature,
                era=era,
                dominant_colors=dominant_colors,
                color_palette=color_data
            )
            
        except Exception as e:
            print(f"Error analyzing image {image_path}: {e}")
            # Return neutral vector on error
            return cls()
    
    @staticmethod
    def _extract_comprehensive_colors(img_array, n_colors=8):
        """
        FIXED: Extract colors properly including vibrant AND muted colors
        
        Returns dict with:
        - dominant_colors: List of hex colors sorted by prominence
        - vibrant_colors: Most saturated colors
        - primary_candidates: Best colors for primary brand color
        - color_weights: Percentage of image each color covers
        """
        h, w = img_array.shape[:2]
        pixels = img_array.reshape(-1, 3)
        
        if SKLEARN_AVAILABLE:
            # Use more clusters to capture color variety
            n_clusters = min(n_colors, len(np.unique(pixels, axis=0)))
            
            # Don't sample too aggressively - we want to catch accent colors
            if len(pixels) > 50000:
                # Stratified sampling to ensure we get colors from all regions
                indices = []
                
                # Sample from different regions
                regions = [
                    (0, h//3, 0, w//3),      # top-left
                    (0, h//3, w//3, 2*w//3),  # top-center  
                    (0, h//3, 2*w//3, w),     # top-right
                    (h//3, 2*h//3, 0, w//3),  # middle-left
                    (h//3, 2*h//3, w//3, 2*w//3),  # center
                    (h//3, 2*h//3, 2*w//3, w),  # middle-right
                    (2*h//3, h, 0, w//3),      # bottom-left
                    (2*h//3, h, w//3, 2*w//3),  # bottom-center
                    (2*h//3, h, 2*w//3, w)      # bottom-right
                ]
                
                samples_per_region = 5000 // len(regions)
                
                for y1, y2, x1, x2 in regions:
                    region = img_array[y1:y2, x1:x2].reshape(-1, 3)
                    if len(region) > 0:
                        n_samples = min(samples_per_region, len(region))
                        region_indices = np.random.choice(len(region), n_samples, replace=False)
                        indices.extend([i for i in region_indices])
                
                # Sample the selected pixels
                sampled_pixels = []
                for y1, y2, x1, x2 in regions:
                    region = img_array[y1:y2, x1:x2].reshape(-1, 3)
                    if len(region) > 0:
                        n_samples = min(samples_per_region, len(region))
                        region_indices = np.random.choice(len(region), n_samples, replace=False)
                        sampled_pixels.append(region[region_indices])
                
                if sampled_pixels:
                    pixels = np.vstack(sampled_pixels)
            
            # Run KMeans
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Get cluster centers and their sizes
            labels = kmeans.labels_
            label_counts = np.bincount(labels)
            
            # Sort colors by cluster size (prominence)
            sorted_indices = np.argsort(label_counts)[::-1]
            colors = kmeans.cluster_centers_[sorted_indices].astype(int)
            weights = label_counts[sorted_indices] / len(labels)
            
        else:
            # Fallback method
            # Quantize colors more carefully
            quantized = (pixels // 64) * 64  # Less aggressive quantization
            unique_colors, counts = np.unique(quantized, axis=0, return_counts=True)
            
            # Sort by frequency
            sorted_indices = np.argsort(counts)[::-1][:n_colors]
            colors = unique_colors[sorted_indices]
            weights = counts[sorted_indices] / len(pixels)
        
        # Convert to hex and analyze color properties
        hex_colors = []
        color_properties = []
        
        for i, color in enumerate(colors):
            hex_color = '#{:02x}{:02x}{:02x}'.format(
                min(255, max(0, int(color[0]))),
                min(255, max(0, int(color[1]))),
                min(255, max(0, int(color[2])))
            )
            hex_colors.append(hex_color)
            
            # Calculate HSV for each color
            r, g, b = color[0]/255, color[1]/255, color[2]/255
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            
            color_properties.append({
                'hex': hex_color,
                'rgb': color.tolist(),
                'hsv': (h, s, v),
                'weight': float(weights[i]),
                'saturation': s,
                'brightness': v,
                'vibrancy': s * v,  # High saturation + brightness = vibrant
                'is_neutral': s < 0.2,  # Low saturation = neutral/gray
                'is_dark': v < 0.3,
                'is_light': v > 0.7
            })
        
        # Sort colors by different criteria
        vibrant_colors = sorted(color_properties, key=lambda x: x['vibrancy'], reverse=True)
        saturated_colors = sorted(color_properties, key=lambda x: x['saturation'], reverse=True)
        
        # Select primary color candidates
        # Prefer vibrant colors with decent coverage
        primary_candidates = []
        for color in color_properties:
            # Score based on vibrancy and weight
            score = color['vibrancy'] * 0.7 + color['weight'] * 0.3
            color['primary_score'] = score
            primary_candidates.append(color)
        
        primary_candidates.sort(key=lambda x: x['primary_score'], reverse=True)
        
        # Build comprehensive color data
        return {
            'dominant_colors': hex_colors,
            'color_properties': color_properties,
            'vibrant_colors': [c['hex'] for c in vibrant_colors[:4]],
            'saturated_colors': [c['hex'] for c in saturated_colors[:4]],
            'primary_candidates': [c['hex'] for c in primary_candidates[:4]],
            'color_weights': {c['hex']: c['weight'] for c in color_properties},
            'neutral_colors': [c['hex'] for c in color_properties if c['is_neutral']],
            'accent_colors': [c['hex'] for c in vibrant_colors if c['weight'] < 0.3][:3]
        }
    
    @staticmethod
    def _calculate_energy(img_array, dominant_colors):
        """Calculate energy based on contrast and color vibrancy"""
        # Calculate contrast
        gray = np.mean(img_array, axis=2)
        contrast = np.std(gray) / 128.0  # Normalize to 0-1
        
        # Calculate edge density
        if len(gray.shape) == 2:
            edges = np.abs(np.diff(gray, axis=0)).mean() + np.abs(np.diff(gray, axis=1)).mean()
            edge_density = min(edges / 100.0, 1.0)
        else:
            edge_density = 0.5
        
        # Color vibrancy
        vibrancy = 0.5
        if dominant_colors:
            saturations = []
            for hex_color in dominant_colors[:3]:  # Top 3 colors
                try:
                    rgb = tuple(int(hex_color[i:i+2], 16)/255 for i in (1, 3, 5))
                    h, s, v = colorsys.rgb_to_hsv(*rgb)
                    saturations.append(s)
                except:
                    saturations.append(0.5)
            vibrancy = np.mean(saturations)
        
        # Combine factors
        energy = (contrast * 0.4 + edge_density * 0.3 + vibrancy * 0.3)
        return min(max(energy, 0.0), 1.0)
    
    @staticmethod
    def _calculate_sophistication(dominant_colors, color_data):
        """Calculate sophistication based on color harmony and neutrals"""
        if not dominant_colors:
            return 0.5
        
        sophistication_score = 0.5
        
        # Check color harmony
        if color_data and 'color_properties' in color_data:
            props = color_data['color_properties']
            
            # More neutral colors = more sophisticated
            neutral_ratio = len([c for c in props if c['is_neutral']]) / len(props)
            sophistication_score += neutral_ratio * 0.3
            
            # Lower saturation average = more sophisticated
            avg_saturation = np.mean([c['saturation'] for c in props[:4]])
            sophistication_score += (1 - avg_saturation) * 0.2
            
            # Check for monochromatic or analogous harmony
            hues = [c['hsv'][0] for c in props[:3]]
            hue_variance = np.var(hues) if len(hues) > 1 else 0
            if hue_variance < 0.1:  # Monochromatic or very close
                sophistication_score += 0.2
        
        return min(max(sophistication_score, 0.0), 1.0)
    
    @staticmethod
    def _calculate_density(img_array):
        """Calculate visual density based on detail and texture"""
        # Calculate local variance as a measure of detail
        gray = np.mean(img_array, axis=2)
        
        # Compute local standard deviation
        kernel_size = 5
        h, w = gray.shape
        local_vars = []
        
        for i in range(0, h-kernel_size, kernel_size):
            for j in range(0, w-kernel_size, kernel_size):
                window = gray[i:i+kernel_size, j:j+kernel_size]
                local_vars.append(np.var(window))
        
        # Average local variance indicates density
        if local_vars:
            avg_variance = np.mean(local_vars)
            density = min(avg_variance / 1000.0, 1.0)
        else:
            density = 0.5
        
        return density
    
    @staticmethod
    def _calculate_temperature(dominant_colors, color_data):
        """Calculate color temperature with improved accuracy"""
        if not dominant_colors:
            return 0.5
        
        warm_score = 0.0
        total_weight = 0.0
        
        if color_data and 'color_properties' in color_data:
            for color_prop in color_data['color_properties'][:5]:  # Top 5 colors
                h, s, v = color_prop['hsv']
                weight = color_prop['weight']
                
                # Warm colors: red, orange, yellow (0-60 and 300-360 in hue)
                if h < 60/360 or h > 300/360:
                    warm_contribution = 1.0
                # Cool colors: blue, green, cyan (120-240 in hue)
                elif 120/360 <= h <= 240/360:
                    warm_contribution = 0.0
                else:
                    # Transition zones
                    if 60/360 <= h < 120/360:
                        warm_contribution = 1 - (h - 60/360) / (60/360)
                    else:  # 240/360 < h < 300/360
                        warm_contribution = (h - 240/360) / (60/360)
                
                warm_score += warm_contribution * weight * s  # Weight by prominence and saturation
                total_weight += weight * s
        
        if total_weight > 0:
            temperature = warm_score / total_weight
        else:
            temperature = 0.5
        
        return min(max(temperature, 0.0), 1.0)
    
    @staticmethod
    def _calculate_era(img_array, dominant_colors):
        """Calculate era (vintage to futuristic) based on color and style"""
        era_score = 0.5
        
        # High contrast + saturated colors = more modern
        gray = np.mean(img_array, axis=2)
        contrast = np.std(gray) / 128.0
        
        # Color saturation indicates modernity
        if dominant_colors:
            saturations = []
            for hex_color in dominant_colors[:3]:
                try:
                    rgb = tuple(int(hex_color[i:i+2], 16)/255 for i in (1, 3, 5))
                    h, s, v = colorsys.rgb_to_hsv(*rgb)
                    saturations.append(s)
                except:
                    saturations.append(0.5)
            
            avg_saturation = np.mean(saturations)
            # Higher saturation = more modern
            era_score = avg_saturation * 0.6 + contrast * 0.4
        
        return min(max(era_score, 0.0), 1.0)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            'energy': self.energy,
            'sophistication': self.sophistication,
            'density': self.density,
            'temperature': self.temperature,
            'era': self.era,
            'dominant_colors': self.dominant_colors
        }
    
    def to_brand_tokens(self) -> Dict:
        """
        FIXED: Generate brand tokens with proper color selection based on actual usage
        """
        tokens = {}
        
        # Better color selection based on comprehensive analysis
        if self.color_palette and 'color_weights' in self.color_palette:
            weights = self.color_palette['color_weights']
            props = self.color_palette.get('color_properties', [])
            
            # Strategy: Use the most prominent color as primary (what people see most)
            # Use vibrant colors as accents (for emphasis)
            
            # Get colors sorted by weight (prominence)
            sorted_by_weight = sorted(weights.items(), key=lambda x: x[1], reverse=True)
            
            # Primary should be the dominant color (most coverage)
            if sorted_by_weight:
                tokens['primary_color'] = sorted_by_weight[0][0]
                
                # Secondary should be either:
                # 1. The second most prominent if it's different enough, OR
                # 2. The most vibrant color for contrast
                vibrant = self.color_palette.get('vibrant_colors', [])
                
                if len(sorted_by_weight) > 1:
                    second_color = sorted_by_weight[1][0]
                    # Check if it's different enough from primary
                    if second_color != tokens['primary_color']:
                        tokens['secondary_color'] = second_color
                    elif vibrant and vibrant[0] != tokens['primary_color']:
                        tokens['secondary_color'] = vibrant[0]
                    else:
                        tokens['secondary_color'] = tokens['primary_color']
                else:
                    tokens['secondary_color'] = tokens['primary_color']
            
            # Add accent colors
            accent_colors = self.color_palette.get('accent_colors', [])
            if accent_colors:
                tokens['accent_colors'] = accent_colors[:2]
            
            # Add neutral colors for UI
            neutral_colors = self.color_palette.get('neutral_colors', [])
            if neutral_colors:
                tokens['neutral_color'] = neutral_colors[0]
            else:
                # Generate a neutral based on primary
                tokens['neutral_color'] = '#6c757d'  # Default neutral
        
        elif self.dominant_colors:
            # Fallback to old method but improved
            tokens['primary_color'] = self.dominant_colors[0]
            tokens['secondary_color'] = self.dominant_colors[1] if len(self.dominant_colors) > 1 else self.dominant_colors[0]
            tokens['accent_colors'] = self.dominant_colors[2:4] if len(self.dominant_colors) > 2 else []
        else:
            # Default colors based on temperature
            if self.temperature > 0.6:
                tokens['primary_color'] = '#ff6b6b'  # Warm red
                tokens['secondary_color'] = '#ffd93d'  # Warm yellow
                tokens['accent_colors'] = ['#ff8787', '#ffe066']
            elif self.temperature < 0.4:
                tokens['primary_color'] = '#4dabf7'  # Cool blue
                tokens['secondary_color'] = '#69db7c'  # Cool green
                tokens['accent_colors'] = ['#74c0fc', '#8ce99a']
            else:
                tokens['primary_color'] = '#495057'  # Neutral
                tokens['secondary_color'] = '#868e96'  # Neutral
                tokens['accent_colors'] = ['#adb5bd', '#dee2e6']
        
        # Typography based on sophistication
        if self.sophistication > 0.8:
            tokens['font_class'] = 'serif'
            tokens['font_weight'] = '300'
            tokens['letter_spacing'] = '0.5px'
        elif self.sophistication > 0.6:
            tokens['font_class'] = 'sans-serif'
            tokens['font_weight'] = '400'
            tokens['letter_spacing'] = '0px'
        else:
            tokens['font_class'] = 'sans-serif'
            tokens['font_weight'] = '500'
            tokens['letter_spacing'] = '-0.5px'
        
        # Spacing based on density
        if self.density < 0.3:
            tokens['spacing_unit'] = '32px'
            tokens['spacing_scale'] = 1.5
        elif self.density < 0.5:
            tokens['spacing_unit'] = '24px'
            tokens['spacing_scale'] = 1.25
        elif self.density < 0.7:
            tokens['spacing_unit'] = '16px'
            tokens['spacing_scale'] = 1.25
        else:
            tokens['spacing_unit'] = '8px'
            tokens['spacing_scale'] = 1.2
        
        # Border radius based on energy
        if self.energy > 0.7:
            tokens['border_radius'] = '16px'
        elif self.energy > 0.5:
            tokens['border_radius'] = '8px'
        elif self.energy > 0.3:
            tokens['border_radius'] = '4px'
        else:
            tokens['border_radius'] = '2px'
        
        # Shadow depth based on sophistication
        if self.sophistication > 0.8:
            tokens['shadow'] = '0 1px 3px rgba(0,0,0,0.12)'
        elif self.sophistication > 0.5:
            tokens['shadow'] = '0 4px 6px rgba(0,0,0,0.1)'
        else:
            tokens['shadow'] = '0 10px 20px rgba(0,0,0,0.15)'
        
        # Generate mood keywords based on actual visual characteristics
        mood = []
        
        # Energy-based moods (contrast, edge density)
        if self.energy > 0.75:
            mood.append('intense')
        elif self.energy > 0.6:
            mood.append('dynamic')  
        elif self.energy > 0.4:
            mood.append('active')
        elif self.energy > 0.25:
            mood.append('gentle')
        else:
            mood.append('serene')
        
        # Sophistication-based moods (complexity, detail)
        if self.sophistication > 0.8:
            mood.append('luxurious')
        elif self.sophistication > 0.6:
            mood.append('refined')
        elif self.sophistication > 0.4:
            mood.append('polished')
        elif self.sophistication > 0.25:
            mood.append('approachable')
        else:
            mood.append('simple')
        
        # Temperature-based moods (actual color temperature)
        if self.temperature > 0.7:
            mood.append('cozy')
        elif self.temperature > 0.55:
            mood.append('warm')
        elif self.temperature < 0.3:
            mood.append('crisp')
        elif self.temperature < 0.45:
            mood.append('cool')
        
        # Density-based moods (visual complexity)
        if self.density > 0.7:
            mood.append('busy')
        elif self.density > 0.5:
            mood.append('detailed')
        elif self.density < 0.3:
            mood.append('minimal')
        elif self.density < 0.5:
            mood.append('clean')
        
        # Color-based moods from actual palette
        if self.color_palette:
            color_props = self.color_palette.get('color_properties', [])
            if color_props:
                avg_saturation = np.mean([c['saturation'] for c in color_props[:3]])
                avg_brightness = np.mean([c['brightness'] for c in color_props[:3]])
                has_neutrals = len(self.color_palette.get('neutral_colors', [])) > len(color_props) // 2
                
                if avg_saturation > 0.7:
                    mood.append('vibrant')
                elif avg_saturation > 0.5:
                    mood.append('colorful')
                elif has_neutrals or avg_saturation < 0.2:
                    mood.append('muted')
                
                if avg_brightness > 0.8:
                    mood.append('bright')
                elif avg_brightness < 0.3:
                    mood.append('dark')
                elif avg_brightness < 0.5:
                    mood.append('moody')
        
        # Remove duplicates while preserving order
        mood = list(dict.fromkeys(mood))
        
        tokens['mood_keywords'] = mood
        
        # Add comprehensive color palette
        if self.color_palette:
            tokens['full_palette'] = {
                'all_colors': self.dominant_colors[:8],
                'vibrant_colors': self.color_palette.get('vibrant_colors', [])[:4],
                'neutral_colors': self.color_palette.get('neutral_colors', [])[:2],
                'color_weights': self.color_palette.get('color_weights', {})
            }
        
        return tokens
    
    def __repr__(self):
        return (f"StyleVector(energy={self.energy:.2f}, "
                f"sophistication={self.sophistication:.2f}, "
                f"density={self.density:.2f}, "
                f"temperature={self.temperature:.2f}, "
                f"era={self.era:.2f})")


def analyze_style_vector(image_path) -> Dict:
    """
    Analyze an image and return its style vector for storage
    Integration function for content_manager.py
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary with style vector data including comprehensive color palette
    """
    try:
        vector = StyleVector.from_image(image_path)
        result = {
            'style_vector': vector.to_dict(),
            'brand_tokens': vector.to_brand_tokens()
        }
        
        # Add extended color palette if available
        if vector.color_palette:
            result['color_analysis'] = {
                'primary_candidates': vector.color_palette.get('primary_candidates', []),
                'vibrant_colors': vector.color_palette.get('vibrant_colors', []),
                'accent_colors': vector.color_palette.get('accent_colors', []),
                'neutral_colors': vector.color_palette.get('neutral_colors', []),
                'color_weights': vector.color_palette.get('color_weights', {})
            }
        
        return result
    except Exception as e:
        print(f"Error analyzing style vector for {image_path}: {e}")
        return None


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"Analyzing: {image_path}")
        result = analyze_style_vector(image_path)
        
        if result:
            print(f"\nStyle Vector: {result['style_vector']}")
            print(f"\nBrand Tokens:")
            tokens = result['brand_tokens']
            print(f"  Primary Color: {tokens.get('primary_color')}")
            print(f"  Secondary Color: {tokens.get('secondary_color')}")
            print(f"  Accent Colors: {tokens.get('accent_colors')}")
            print(f"  Font Class: {tokens.get('font_class')}")
            print(f"  Spacing Unit: {tokens.get('spacing_unit')}")
            print(f"  Mood: {', '.join(tokens.get('mood_keywords', []))}")
            
            if 'full_palette' in tokens:
                palette = tokens['full_palette']
                print(f"\nFull Color Palette:")
                print(f"  All Colors: {palette.get('all_colors', [])}")
                print(f"  Vibrant Colors: {palette.get('vibrant_colors', [])}")
                print(f"  Neutral Colors: {palette.get('neutral_colors', [])}")
        else:
            print("Analysis failed")
    else:
        print("Usage: python style_vector_fixed.py <image_path>")