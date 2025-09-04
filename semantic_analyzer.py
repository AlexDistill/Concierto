#!/usr/bin/env python3
"""
Semantic Image Analyzer - HONEST VERSION
Only analyzes what can actually be extracted from images
No hallucinated brand strategies or fake specifications
"""

import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, List, Optional
import colorsys
from datetime import datetime

try:
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class SemanticAnalyzer:
    """
    Honest semantic analysis of images
    Only returns what can actually be determined from the image
    """
    
    def analyze_image(self, image_path: str, description: str = "") -> Dict:
        """
        Analyze an image and return ONLY what we can actually determine
        
        Returns:
            - colors: Actual extracted colors with weights
            - composition: Basic composition analysis (aspect ratio, dimensions)
            - visual_properties: Brightness, contrast, saturation (measurable)
            - description_keywords: Keywords from provided description (if any)
        """
        try:
            # Load image
            img = Image.open(image_path).convert('RGB')
            img_array = np.array(img)
            
            # Extract real colors
            colors = self._extract_colors(img_array)
            
            # Analyze basic composition
            composition = self._analyze_composition(img)
            
            # Calculate visual properties we can actually measure
            visual_properties = self._calculate_visual_properties(img_array)
            
            # Parse description if provided
            description_keywords = self._parse_description(description) if description else []
            
            return {
                'analyzed_at': datetime.now().isoformat(),
                'file_path': str(image_path),
                'colors': colors,
                'composition': composition,
                'visual_properties': visual_properties,
                'description_keywords': description_keywords,
                'analysis_type': 'semantic_honest_v1'
            }
            
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return {
                'error': str(e),
                'analyzed_at': datetime.now().isoformat()
            }
    
    def _extract_colors(self, img_array: np.ndarray) -> Dict:
        """Extract actual colors from the image"""
        h, w = img_array.shape[:2]
        pixels = img_array.reshape(-1, 3)
        
        # Get unique colors and their counts
        from collections import Counter
        pixel_tuples = [tuple(p) for p in pixels]
        color_counts = Counter(pixel_tuples)
        total_pixels = len(pixels)
        
        # Get most common colors
        most_common = color_counts.most_common(10)
        
        colors = []
        for color_tuple, count in most_common[:8]:
            hex_color = '#{:02x}{:02x}{:02x}'.format(
                color_tuple[0], color_tuple[1], color_tuple[2]
            )
            
            # Calculate HSV for color properties
            r, g, b = color_tuple[0]/255, color_tuple[1]/255, color_tuple[2]/255
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            
            colors.append({
                'hex': hex_color,
                'rgb': [int(c) for c in color_tuple],  # Convert to regular int
                'percentage': round((count / total_pixels) * 100, 2),
                'saturation': round(s, 2),
                'brightness': round(v, 2),
                'hue': round(h * 360, 1)  # Convert to degrees
            })
        
        # Use clustering for dominant color groups if sklearn available
        dominant_groups = []
        if SKLEARN_AVAILABLE and len(pixels) > 100:
            # Sample for speed
            sample_size = min(5000, len(pixels))
            if len(pixels) > sample_size:
                indices = np.random.choice(len(pixels), sample_size, replace=False)
                sample_pixels = pixels[indices]
            else:
                sample_pixels = pixels
            
            # Cluster into color groups
            n_clusters = min(5, len(np.unique(sample_pixels, axis=0)))
            if n_clusters > 1:
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                kmeans.fit(sample_pixels)
                
                for center in kmeans.cluster_centers_:
                    hex_color = '#{:02x}{:02x}{:02x}'.format(
                        int(center[0]), int(center[1]), int(center[2])
                    )
                    dominant_groups.append(hex_color)
        
        return {
            'most_common': colors,
            'dominant_groups': dominant_groups,
            'total_unique_colors': min(len(color_counts), 10000)  # Cap for sanity
        }
    
    def _analyze_composition(self, img: Image) -> Dict:
        """Analyze basic composition - things we can actually measure"""
        width, height = img.size
        
        return {
            'width': width,
            'height': height,
            'aspect_ratio': round(width / height, 2),
            'orientation': 'landscape' if width > height else 'portrait' if height > width else 'square',
            'size_category': self._categorize_size(width, height)
        }
    
    def _categorize_size(self, width: int, height: int) -> str:
        """Categorize image size"""
        pixels = width * height
        if pixels < 100000:
            return 'small'
        elif pixels < 1000000:
            return 'medium'
        elif pixels < 4000000:
            return 'large'
        else:
            return 'very_large'
    
    def _calculate_visual_properties(self, img_array: np.ndarray) -> Dict:
        """Calculate measurable visual properties"""
        # Convert to grayscale for some calculations
        gray = np.mean(img_array, axis=2)
        
        # Calculate actual measurable properties
        brightness = round(np.mean(gray) / 255, 2)
        contrast = round(np.std(gray) / 128, 2)  # Normalized
        
        # Color saturation (average)
        saturations = []
        # Sample pixels for saturation calculation
        sample_size = min(1000, img_array.shape[0] * img_array.shape[1])
        h, w = img_array.shape[:2]
        for _ in range(sample_size):
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            pixel = img_array[y, x]
            r, g, b = pixel[0]/255, pixel[1]/255, pixel[2]/255
            _, s, _ = colorsys.rgb_to_hsv(r, g, b)
            saturations.append(s)
        
        avg_saturation = round(np.mean(saturations), 2)
        
        # Detect if likely black and white
        is_grayscale = self._is_grayscale(img_array)
        
        return {
            'brightness': float(brightness),  # Convert numpy float
            'contrast': float(contrast),  # Convert numpy float 
            'saturation': float(avg_saturation),  # Convert numpy float
            'is_grayscale': bool(is_grayscale),  # Convert numpy bool
            'darkness': 'dark' if brightness < 0.3 else 'light' if brightness > 0.7 else 'medium'
        }
    
    def _is_grayscale(self, img_array: np.ndarray) -> bool:
        """Check if image is grayscale"""
        # Sample some pixels
        sample_size = min(100, img_array.shape[0] * img_array.shape[1])
        h, w = img_array.shape[:2]
        
        color_differences = []
        for _ in range(sample_size):
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            pixel = img_array[y, x]
            # Check if R, G, B are similar
            diff = np.max(pixel) - np.min(pixel)
            color_differences.append(diff)
        
        # If most pixels have similar RGB values, it's grayscale
        avg_diff = np.mean(color_differences)
        return avg_diff < 20  # Threshold for considering grayscale
    
    def _parse_description(self, description: str) -> List[str]:
        """Extract keywords from description"""
        if not description:
            return []
        
        # Simple keyword extraction
        # Remove common words and extract meaningful terms
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        # Split and clean
        words = description.lower().split()
        keywords = []
        
        for word in words:
            # Remove punctuation
            cleaned = ''.join(c for c in word if c.isalnum() or c == '-')
            if cleaned and len(cleaned) > 2 and cleaned not in common_words:
                keywords.append(cleaned)
        
        # Return unique keywords
        return list(set(keywords))[:20]  # Limit to 20 keywords


def analyze_semantic(image_path: str, description: str = "") -> Dict:
    """
    Simple integration function for semantic analysis
    
    Returns only what can actually be determined from the image
    """
    analyzer = SemanticAnalyzer()
    return analyzer.analyze_image(image_path, description)


# Integration with existing system
def enhance_with_semantic_analysis(item: Dict, image_path: str) -> Dict:
    """
    Add semantic analysis to an existing item
    Only adds real, measurable data
    """
    semantic = analyze_semantic(image_path, item.get('description', ''))
    
    if semantic and 'error' not in semantic:
        item['semantic_analysis'] = semantic
        
        # Extract primary colors for use
        if 'colors' in semantic and 'most_common' in semantic['colors']:
            colors = semantic['colors']['most_common']
            if colors:
                # Use the most prominent colors
                item['primary_color'] = colors[0]['hex']
                if len(colors) > 1:
                    item['secondary_color'] = colors[1]['hex']
                if len(colors) > 2:
                    item['accent_colors'] = [c['hex'] for c in colors[2:5]]
    
    return item


if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        description = sys.argv[2] if len(sys.argv) > 2 else ""
        
        print(f"Analyzing: {image_path}")
        result = analyze_semantic(image_path, description)
        
        if result:
            print("\n=== SEMANTIC ANALYSIS (HONEST) ===")
            
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                # Colors
                if 'colors' in result:
                    colors = result['colors']
                    print("\n📊 Color Analysis:")
                    if 'most_common' in colors:
                        for i, color in enumerate(colors['most_common'][:5], 1):
                            print(f"  {i}. {color['hex']} - {color['percentage']:.1f}% " +
                                  f"(Sat: {color['saturation']}, Bright: {color['brightness']})")
                    
                    if 'dominant_groups' in colors and colors['dominant_groups']:
                        print(f"  Dominant Groups: {', '.join(colors['dominant_groups'])}")
                
                # Composition
                if 'composition' in result:
                    comp = result['composition']
                    print(f"\n📐 Composition:")
                    print(f"  Dimensions: {comp['width']}x{comp['height']} ({comp['orientation']})")
                    print(f"  Aspect Ratio: {comp['aspect_ratio']}")
                    print(f"  Size: {comp['size_category']}")
                
                # Visual Properties
                if 'visual_properties' in result:
                    props = result['visual_properties']
                    print(f"\n✨ Visual Properties:")
                    print(f"  Brightness: {props['brightness']} ({props['darkness']})")
                    print(f"  Contrast: {props['contrast']}")
                    print(f"  Saturation: {props['saturation']}")
                    print(f"  Grayscale: {props['is_grayscale']}")
                
                # Keywords
                if 'description_keywords' in result and result['description_keywords']:
                    print(f"\n🔤 Description Keywords:")
                    print(f"  {', '.join(result['description_keywords'][:10])}")
        else:
            print("Analysis failed")
    else:
        print("Usage: python semantic_analyzer.py <image_path> [description]")