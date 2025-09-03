#!/usr/bin/env python3
"""
Style Vector Analysis for Concierto
Analyzes images to extract style dimensions and brand tokens
"""

import numpy as np
from PIL import Image
import colorsys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json

try:
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    print("Warning: scikit-learn not available. Using fallback color extraction.")
    SKLEARN_AVAILABLE = False

class StyleVector:
    """
    Represents the style characteristics of an image as a multi-dimensional vector
    """
    
    def __init__(self, energy=0.5, sophistication=0.5, density=0.5, 
                 temperature=0.5, era=0.5, dominant_colors=None):
        """
        Initialize a style vector with dimensions from 0-1
        
        Args:
            energy: calm (0) to energetic (1)
            sophistication: playful (0) to serious (1) 
            density: minimal (0) to maximal (1)
            temperature: cold (0) to warm (1)
            era: classic (0) to futuristic (1)
            dominant_colors: list of hex colors
        """
        self.energy = np.clip(energy, 0, 1)
        self.sophistication = np.clip(sophistication, 0, 1)
        self.density = np.clip(density, 0, 1)
        self.temperature = np.clip(temperature, 0, 1)
        self.era = np.clip(era, 0, 1)
        self.dominant_colors = dominant_colors or []
        
    @classmethod
    def from_image(cls, image_path):
        """
        Extract style vector from an image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            StyleVector object
        """
        try:
            # Open and prepare image
            img = Image.open(image_path).convert('RGB')
            img_array = np.array(img)
            
            # Resize for faster processing
            if img.width > 800 or img.height > 800:
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                img_array = np.array(img)
            
            # Extract dominant colors
            dominant_colors = cls._extract_dominant_colors(img_array)
            
            # Calculate style dimensions
            energy = cls._calculate_energy(img_array, dominant_colors)
            sophistication = cls._calculate_sophistication(dominant_colors)
            density = cls._calculate_density(img_array)
            temperature = cls._calculate_temperature(dominant_colors)
            era = cls._calculate_era(img_array, dominant_colors)
            
            return cls(
                energy=energy,
                sophistication=sophistication,
                density=density,
                temperature=temperature,
                era=era,
                dominant_colors=[cls._rgb_to_hex(c) for c in dominant_colors]
            )
            
        except Exception as e:
            print(f"Error analyzing image {image_path}: {e}")
            # Return neutral vector on error
            return cls()
    
    @staticmethod
    def _extract_dominant_colors(img_array, n_colors=5):
        """Extract dominant colors using KMeans clustering or fallback method"""
        # Reshape image to be a list of pixels
        pixels = img_array.reshape(-1, 3)
        
        # Sample pixels for faster processing
        if len(pixels) > 5000:
            indices = np.random.choice(len(pixels), 5000, replace=False)
            pixels = pixels[indices]
        
        if SKLEARN_AVAILABLE:
            # Use KMeans clustering
            kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
            kmeans.fit(pixels)
            colors = kmeans.cluster_centers_.astype(int)
        else:
            # Fallback: simple quantization
            # Reduce color space and find most common colors
            quantized = (pixels // 32) * 32  # Reduce to 8 levels per channel
            unique_colors, counts = np.unique(quantized, axis=0, return_counts=True)
            # Get top n colors by frequency
            top_indices = np.argsort(counts)[-n_colors:][::-1]
            colors = unique_colors[top_indices]
        
        return colors
    
    @staticmethod
    def _calculate_energy(img_array, dominant_colors):
        """
        Calculate energy based on color vibrancy and contrast
        High saturation and high contrast = high energy
        """
        # Calculate saturation of dominant colors
        saturations = []
        for color in dominant_colors:
            r, g, b = color / 255.0
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            saturations.append(s)
        avg_saturation = np.mean(saturations)
        
        # Calculate contrast using standard deviation of luminance
        gray = np.dot(img_array[...,:3], [0.299, 0.587, 0.114])
        contrast = np.std(gray) / 128.0  # Normalize to 0-1
        
        # Combine saturation and contrast
        energy = (avg_saturation * 0.6 + contrast * 0.4)
        return np.clip(energy, 0, 1)
    
    @staticmethod
    def _calculate_sophistication(dominant_colors):
        """
        Calculate sophistication based on color palette complexity
        Muted colors and limited hue variance = more sophisticated
        """
        saturations = []
        hues = []
        
        for color in dominant_colors:
            r, g, b = color / 255.0
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            saturations.append(s)
            hues.append(h)
        
        # Low saturation = more sophisticated
        avg_saturation = np.mean(saturations)
        
        # Low hue variance = more sophisticated (monochromatic/analogous)
        hue_variance = np.std(hues)
        
        # Calculate sophistication (inverse of playfulness)
        sophistication = 1.0 - (avg_saturation * 0.5 + hue_variance * 0.5)
        return np.clip(sophistication, 0, 1)
    
    @staticmethod
    def _calculate_density(img_array):
        """
        Calculate visual density based on edge detection and complexity
        More edges and detail = higher density
        """
        # Convert to grayscale
        gray = np.dot(img_array[...,:3], [0.299, 0.587, 0.114])
        
        # Simple edge detection using gradient
        gy, gx = np.gradient(gray)
        edge_magnitude = np.sqrt(gx**2 + gy**2)
        
        # Calculate density as proportion of significant edges
        threshold = np.mean(edge_magnitude) + np.std(edge_magnitude)
        density = np.sum(edge_magnitude > threshold) / edge_magnitude.size
        
        # Scale to reasonable range (typically 0.05-0.3 becomes 0-1)
        density = np.clip(density * 5, 0, 1)
        return density
    
    @staticmethod
    def _calculate_temperature(dominant_colors):
        """
        Calculate color temperature
        Warm colors (red, orange, yellow) vs cool colors (blue, green, purple)
        """
        warm_score = 0
        cool_score = 0
        
        for color in dominant_colors:
            r, g, b = color / 255.0
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            
            # Hue wheel: 0-60 and 300-360 are warm, 120-240 are cool
            hue_degrees = h * 360
            
            if hue_degrees <= 60 or hue_degrees >= 300:
                # Red, orange, yellow, magenta
                warm_score += s * v  # Weight by saturation and value
            elif 120 <= hue_degrees <= 240:
                # Green, cyan, blue
                cool_score += s * v
            # 60-120 and 240-300 are neutral, don't contribute
        
        # Normalize and calculate temperature
        total = warm_score + cool_score
        if total > 0:
            temperature = warm_score / total
        else:
            temperature = 0.5  # Neutral if no clear warm/cool colors
        
        return temperature
    
    @staticmethod
    def _calculate_era(img_array, dominant_colors):
        """
        Calculate era from classic to futuristic based on style indicators
        High contrast + saturated colors + clean edges = more futuristic
        Muted colors + soft edges = more classic
        """
        # Check saturation levels
        saturations = []
        for color in dominant_colors:
            r, g, b = color / 255.0
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            saturations.append(s)
        avg_saturation = np.mean(saturations)
        
        # Check for neon/electric colors (very high saturation + specific hues)
        has_neon = any(s > 0.8 for s in saturations)
        
        # Check contrast
        gray = np.dot(img_array[...,:3], [0.299, 0.587, 0.114])
        contrast = np.std(gray) / 128.0
        
        # Calculate era score
        era = 0.3  # Start at slightly classic
        if has_neon:
            era += 0.3
        era += avg_saturation * 0.2
        era += contrast * 0.2
        
        return np.clip(era, 0, 1)
    
    @staticmethod
    def _rgb_to_hex(rgb):
        """Convert RGB array to hex color string"""
        r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def _hex_to_rgb(hex_color):
        """Convert hex color string to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def mix(self, vectors: List['StyleVector'], weights: Optional[List[float]] = None):
        """
        Mix multiple style vectors into a blended vector
        
        Args:
            vectors: List of StyleVector objects to blend
            weights: Optional weights for each vector (default: equal weights)
            
        Returns:
            New blended StyleVector
        """
        if not vectors:
            return StyleVector()
        
        # Include self in the mix
        all_vectors = [self] + list(vectors)
        
        # Set default equal weights if not provided
        if weights is None:
            weights = [1.0 / len(all_vectors)] * len(all_vectors)
        else:
            # Ensure weights includes weight for self
            weights = [1.0 / len(all_vectors)] + list(weights)
            # Normalize weights
            total = sum(weights)
            weights = [w / total for w in weights]
        
        # Calculate weighted average for each dimension
        energy = sum(v.energy * w for v, w in zip(all_vectors, weights))
        sophistication = sum(v.sophistication * w for v, w in zip(all_vectors, weights))
        density = sum(v.density * w for v, w in zip(all_vectors, weights))
        temperature = sum(v.temperature * w for v, w in zip(all_vectors, weights))
        era = sum(v.era * w for v, w in zip(all_vectors, weights))
        
        # Mix dominant colors
        all_colors = []
        for v, w in zip(all_vectors, weights):
            # Weight the contribution of colors by vector weight
            for _ in range(int(w * 10)):  # Sample proportionally
                all_colors.extend(v.dominant_colors[:3])  # Take top 3 colors
        
        # Get unique colors and select most common
        unique_colors = list(set(all_colors))[:5] if all_colors else []
        
        return StyleVector(
            energy=energy,
            sophistication=sophistication,
            density=density,
            temperature=temperature,
            era=era,
            dominant_colors=unique_colors
        )
    
    def to_brand_tokens(self) -> Dict:
        """
        Convert style vector to brand design tokens
        
        Returns:
            Dictionary with brand tokens including colors, typography, spacing, and mood
        """
        tokens = {}
        
        # Select primary and secondary colors
        if self.dominant_colors:
            tokens['primary_color'] = self.dominant_colors[0]
            tokens['secondary_color'] = self.dominant_colors[1] if len(self.dominant_colors) > 1 else self.dominant_colors[0]
        else:
            # Default colors based on temperature
            if self.temperature > 0.6:
                tokens['primary_color'] = '#ff6b6b'  # Warm red
                tokens['secondary_color'] = '#ffd93d'  # Warm yellow
            elif self.temperature < 0.4:
                tokens['primary_color'] = '#4dabf7'  # Cool blue
                tokens['secondary_color'] = '#69db7c'  # Cool green
            else:
                tokens['primary_color'] = '#868e96'  # Neutral gray
                tokens['secondary_color'] = '#495057'  # Darker gray
        
        # Suggest font classification based on sophistication and era
        if self.sophistication > 0.7:
            if self.era > 0.6:
                tokens['font_class'] = 'sans-serif'  # Modern and sophisticated
            else:
                tokens['font_class'] = 'serif'  # Classic and sophisticated
        elif self.sophistication < 0.3:
            tokens['font_class'] = 'display'  # Playful
        else:
            tokens['font_class'] = 'sans-serif'  # Neutral default
        
        # Determine spacing unit based on density
        if self.density < 0.3:
            tokens['spacing_unit'] = '16px'  # Generous spacing for minimal designs
        elif self.density > 0.7:
            tokens['spacing_unit'] = '4px'  # Tight spacing for dense designs
        else:
            tokens['spacing_unit'] = '8px'  # Standard spacing
        
        # Generate mood keywords
        mood_keywords = []
        
        # Energy keywords
        if self.energy > 0.7:
            mood_keywords.append('energetic')
        elif self.energy > 0.5:
            mood_keywords.append('dynamic')
        elif self.energy > 0.3:
            mood_keywords.append('balanced')
        else:
            mood_keywords.append('calm')
        
        # Sophistication keywords
        if self.sophistication > 0.7:
            mood_keywords.append('refined')
        elif self.sophistication > 0.5:
            mood_keywords.append('professional')
        elif self.sophistication > 0.3:
            mood_keywords.append('approachable')
        else:
            mood_keywords.append('playful')
        
        # Density keywords
        if self.density > 0.7:
            mood_keywords.append('rich')
        elif self.density < 0.3:
            mood_keywords.append('minimal')
        
        # Temperature keywords
        if self.temperature > 0.7:
            mood_keywords.append('warm')
        elif self.temperature < 0.3:
            mood_keywords.append('cool')
        
        # Era keywords
        if self.era > 0.7:
            mood_keywords.append('futuristic')
        elif self.era > 0.5:
            mood_keywords.append('contemporary')
        elif self.era > 0.3:
            mood_keywords.append('timeless')
        else:
            mood_keywords.append('classic')
        
        tokens['mood_keywords'] = mood_keywords[:5]  # Limit to 5 keywords
        
        return tokens
    
    def to_dict(self) -> Dict:
        """
        Convert style vector to dictionary for JSON serialization
        """
        return {
            'energy': float(self.energy),
            'sophistication': float(self.sophistication),
            'density': float(self.density),
            'temperature': float(self.temperature),
            'era': float(self.era),
            'dominant_colors': self.dominant_colors
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """
        Create StyleVector from dictionary
        """
        return cls(
            energy=data.get('energy', 0.5),
            sophistication=data.get('sophistication', 0.5),
            density=data.get('density', 0.5),
            temperature=data.get('temperature', 0.5),
            era=data.get('era', 0.5),
            dominant_colors=data.get('dominant_colors', [])
        )
    
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
        Dictionary with style vector data
    """
    try:
        vector = StyleVector.from_image(image_path)
        return {
            'style_vector': vector.to_dict(),
            'brand_tokens': vector.to_brand_tokens()
        }
    except Exception as e:
        print(f"Error analyzing style vector for {image_path}: {e}")
        return None


def batch_analyze_styles(image_directory: str = "content/images") -> Dict:
    """
    Analyze all images in a directory and return style vectors
    
    Args:
        image_directory: Path to directory containing images
        
    Returns:
        Dictionary mapping filenames to style vectors
    """
    results = {}
    image_dir = Path(image_directory)
    
    if not image_dir.exists():
        print(f"Directory {image_directory} not found")
        return results
    
    # Process all image files
    for image_file in image_dir.glob("*"):
        if image_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            print(f"Analyzing {image_file.name}...")
            style_data = analyze_style_vector(image_file)
            if style_data:
                results[image_file.name] = style_data
    
    return results


def create_mood_board(image_paths: List[str], weights: Optional[List[float]] = None) -> Dict:
    """
    Create a mood board by mixing style vectors from multiple images
    
    Args:
        image_paths: List of paths to images
        weights: Optional weights for each image
        
    Returns:
        Combined style vector and brand tokens
    """
    if not image_paths:
        return None
    
    # Extract style vectors
    vectors = []
    for path in image_paths:
        vector = StyleVector.from_image(path)
        vectors.append(vector)
    
    # Mix vectors
    if vectors:
        mixed = vectors[0].mix(vectors[1:], weights[1:] if weights else None)
        return {
            'style_vector': mixed.to_dict(),
            'brand_tokens': mixed.to_brand_tokens(),
            'source_images': image_paths
        }
    
    return None


# Example usage and testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Analyze a specific image
        image_path = sys.argv[1]
        print(f"\nAnalyzing {image_path}...")
        
        vector = StyleVector.from_image(image_path)
        print(f"\nStyle Vector: {vector}")
        
        tokens = vector.to_brand_tokens()
        print(f"\nBrand Tokens:")
        print(json.dumps(tokens, indent=2))
        
        # Save to JSON
        output = {
            'image': image_path,
            'style_vector': vector.to_dict(),
            'brand_tokens': tokens
        }
        
        with open('style_analysis.json', 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\nResults saved to style_analysis.json")
    else:
        print("Usage: python style_vector.py <image_path>")
        print("\nOr import and use in your code:")
        print("  from style_vector import analyze_style_vector")
        print("  style_data = analyze_style_vector('path/to/image.jpg')")