#!/usr/bin/env python3
"""
Deep Source Material Analysis Engine
Extracts brand-relevant patterns, typography styles, layout principles, 
texture qualities, spatial relationships, and cultural signals from source images
"""

import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import colorsys
import json
from datetime import datetime
from semantic_analyzer import SemanticAnalyzer

try:
    from sklearn.cluster import KMeans
    from scipy import ndimage
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class DeepSourceAnalyzer:
    """
    Deep analysis of source materials to extract brand-relevant DNA
    Goes beyond basic color/composition to identify design patterns, 
    cultural signals, and brandable elements
    """
    
    def __init__(self):
        self.semantic_analyzer = SemanticAnalyzer()
        
    def analyze_source_material(self, image_path: str, description: str = "") -> Dict:
        """
        Comprehensive analysis of source material for brand DNA extraction
        
        Returns:
            - Basic semantic analysis
            - Typography/text patterns  
            - Layout and spatial principles
            - Texture and surface analysis
            - Cultural and contextual signals
            - Brand DNA fingerprint
        """
        try:
            # Get basic semantic analysis first
            base_analysis = self.semantic_analyzer.analyze_image(image_path, description)
            
            if 'error' in base_analysis:
                return base_analysis
            
            # Load image for deep analysis
            img = Image.open(image_path).convert('RGB')
            img_array = np.array(img)
            
            # Deep brand analysis
            analysis = {
                **base_analysis,
                'brand_dna': self._extract_brand_dna(img, img_array),
                'layout_principles': self._analyze_layout_principles(img, img_array),
                'texture_analysis': self._analyze_textures(img, img_array),
                'typography_signals': self._detect_typography_patterns(img, img_array),
                'cultural_signals': self._identify_cultural_signals(img, description),
                'brandable_elements': self._extract_brandable_elements(img, img_array),
                'analysis_type': 'deep_source_v1'
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error in deep source analysis: {e}")
            return {
                'error': str(e),
                'analyzed_at': datetime.now().isoformat()
            }
    
    def _extract_brand_dna(self, img: Image, img_array: np.ndarray) -> Dict:
        """Extract core brand DNA patterns from the image"""
        
        # Color sophistication analysis
        color_sophistication = self._analyze_color_sophistication(img_array)
        
        # Visual weight distribution
        weight_distribution = self._analyze_visual_weight(img_array)
        
        # Rhythm and repetition patterns
        rhythm_patterns = self._detect_rhythm_patterns(img_array)
        
        # Luxury vs accessible indicators
        luxury_signals = self._detect_luxury_signals(img, img_array)
        
        # Energy and dynamism
        energy_analysis = self._analyze_energy_levels(img_array)
        
        return {
            'color_sophistication': color_sophistication,
            'visual_weight': weight_distribution,
            'rhythm_patterns': rhythm_patterns,
            'luxury_indicators': luxury_signals,
            'energy_profile': energy_analysis,
            'brand_archetype_signals': self._detect_archetype_signals(img, img_array)
        }
    
    def _analyze_color_sophistication(self, img_array: np.ndarray) -> Dict:
        """Analyze color sophistication and harmony"""
        
        # Sample pixels for analysis
        h, w = img_array.shape[:2]
        sample_size = min(2000, h * w)
        
        # Get color harmony patterns
        harmonies = []
        saturations = []
        hue_distances = []
        
        for _ in range(sample_size):
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            pixel = img_array[y, x]
            r, g, b = pixel[0]/255, pixel[1]/255, pixel[2]/255
            hue, sat, val = colorsys.rgb_to_hsv(r, g, b)
            
            saturations.append(sat)
            harmonies.append(hue)
        
        # Analyze color relationships
        hue_variance = np.var(harmonies)
        sat_consistency = 1 - np.var(saturations)  # Higher = more consistent
        
        # Detect monochromatic, analogous, or complementary schemes
        scheme_type = self._classify_color_scheme(harmonies)
        
        return {
            'sophistication_level': min(1.0, sat_consistency + (0.3 if hue_variance < 0.1 else 0)),
            'color_scheme_type': scheme_type,
            'saturation_consistency': float(sat_consistency),
            'hue_variance': float(hue_variance),
            'palette_complexity': 'simple' if hue_variance < 0.1 else 'complex'
        }
    
    def _classify_color_scheme(self, hues: List[float]) -> str:
        """Classify the type of color scheme"""
        if not hues:
            return 'unknown'
        
        hue_range = max(hues) - min(hues)
        
        if hue_range < 0.1:
            return 'monochromatic'
        elif hue_range < 0.25:
            return 'analogous'
        elif hue_range > 0.7:
            return 'complementary'
        else:
            return 'triadic'
    
    def _analyze_visual_weight(self, img_array: np.ndarray) -> Dict:
        """Analyze how visual weight is distributed"""
        
        # Convert to grayscale for weight analysis
        gray = np.mean(img_array, axis=2)
        h, w = gray.shape
        
        # Divide into quadrants
        mid_h, mid_w = h // 2, w // 2
        
        quadrants = {
            'top_left': gray[:mid_h, :mid_w],
            'top_right': gray[:mid_h, mid_w:],
            'bottom_left': gray[mid_h:, :mid_w], 
            'bottom_right': gray[mid_h:, mid_w:]
        }
        
        # Calculate weight (darker = heavier)
        weights = {}
        for quad, section in quadrants.items():
            # Weight = inverse brightness + contrast
            brightness = np.mean(section) / 255
            contrast = np.std(section) / 128
            weights[quad] = (1 - brightness) + contrast
        
        # Analyze balance
        horizontal_balance = abs(
            (weights['top_left'] + weights['bottom_left']) - 
            (weights['top_right'] + weights['bottom_right'])
        )
        
        vertical_balance = abs(
            (weights['top_left'] + weights['top_right']) - 
            (weights['bottom_left'] + weights['bottom_right'])
        )
        
        return {
            'quadrant_weights': {k: float(v) for k, v in weights.items()},
            'horizontal_balance': float(horizontal_balance),
            'vertical_balance': float(vertical_balance),
            'balance_type': self._classify_balance(horizontal_balance, vertical_balance),
            'dominant_quadrant': max(weights, key=weights.get)
        }
    
    def _classify_balance(self, h_balance: float, v_balance: float) -> str:
        """Classify the type of visual balance"""
        threshold = 0.3
        
        if h_balance < threshold and v_balance < threshold:
            return 'symmetric'
        elif h_balance > threshold and v_balance > threshold:
            return 'asymmetric'
        elif h_balance < threshold:
            return 'horizontally_balanced'
        else:
            return 'vertically_balanced'
    
    def _detect_rhythm_patterns(self, img_array: np.ndarray) -> Dict:
        """Detect repetition and rhythm in the composition"""
        
        # Convert to grayscale for pattern detection
        gray = np.mean(img_array, axis=2)
        
        # Apply edge detection
        edges = self._simple_edge_detection(gray)
        
        # Analyze horizontal and vertical patterns
        h_pattern_strength = self._measure_pattern_strength(edges, axis='horizontal')
        v_pattern_strength = self._measure_pattern_strength(edges, axis='vertical')
        
        # Detect grid-like structures
        grid_score = min(h_pattern_strength, v_pattern_strength)
        
        return {
            'horizontal_rhythm': float(h_pattern_strength),
            'vertical_rhythm': float(v_pattern_strength),
            'grid_structure': float(grid_score),
            'pattern_type': self._classify_pattern_type(h_pattern_strength, v_pattern_strength),
            'repetition_strength': float((h_pattern_strength + v_pattern_strength) / 2)
        }
    
    def _simple_edge_detection(self, gray: np.ndarray) -> np.ndarray:
        """Simple edge detection without external dependencies"""
        # Sobel-like edge detection
        kernel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        kernel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        
        # Manual convolution for edge detection
        edges = np.zeros_like(gray)
        h, w = gray.shape
        
        for y in range(1, h-1):
            for x in range(1, w-1):
                region = gray[y-1:y+2, x-1:x+2]
                gx = np.sum(region * kernel_x)
                gy = np.sum(region * kernel_y)
                edges[y, x] = np.sqrt(gx**2 + gy**2)
        
        return edges
    
    def _measure_pattern_strength(self, edges: np.ndarray, axis: str) -> float:
        """Measure pattern strength along an axis"""
        if axis == 'horizontal':
            # Sum edges along rows, look for consistent patterns
            row_sums = np.sum(edges, axis=1)
        else:
            # Sum edges along columns
            row_sums = np.sum(edges, axis=0)
        
        # Look for regularity in the sums
        if len(row_sums) < 10:
            return 0.0
        
        # Simple autocorrelation-like measure
        mean_val = np.mean(row_sums)
        variance = np.var(row_sums)
        
        if variance == 0:
            return 0.0
        
        # Measure how regular the pattern is
        regularity = 1 / (1 + variance / (mean_val + 1))
        return min(1.0, regularity)
    
    def _classify_pattern_type(self, h_strength: float, v_strength: float) -> str:
        """Classify the type of pattern"""
        threshold = 0.3
        
        if h_strength > threshold and v_strength > threshold:
            return 'grid'
        elif h_strength > threshold:
            return 'horizontal_lines'
        elif v_strength > threshold:
            return 'vertical_lines'
        else:
            return 'organic'
    
    def _analyze_layout_principles(self, img: Image, img_array: np.ndarray) -> Dict:
        """Analyze layout and spatial design principles"""
        
        width, height = img.size
        
        # Golden ratio analysis
        golden_ratio_score = self._analyze_golden_ratio(width, height, img_array)
        
        # Rule of thirds
        thirds_score = self._analyze_rule_of_thirds(img_array)
        
        # Margin and whitespace analysis
        whitespace = self._analyze_whitespace(img_array)
        
        # Focal point detection
        focal_points = self._detect_focal_points(img_array)
        
        return {
            'golden_ratio_alignment': golden_ratio_score,
            'rule_of_thirds_score': thirds_score,
            'whitespace_usage': whitespace,
            'focal_points': focal_points,
            'layout_style': self._classify_layout_style(golden_ratio_score, thirds_score, whitespace)
        }
    
    def _analyze_golden_ratio(self, width: int, height: int, img_array: np.ndarray) -> float:
        """Analyze alignment with golden ratio principles"""
        golden_ratio = 1.618
        aspect_ratio = width / height
        
        # How close is the aspect ratio to golden ratio?
        ratio_score = 1 / (1 + abs(aspect_ratio - golden_ratio))
        
        # Check if key elements align with golden ratio divisions
        golden_lines_h = [height / golden_ratio, height * (1 - 1/golden_ratio)]
        golden_lines_v = [width / golden_ratio, width * (1 - 1/golden_ratio)]
        
        # Simple content analysis along golden lines
        content_score = self._measure_content_along_lines(img_array, golden_lines_h, golden_lines_v)
        
        return float((ratio_score + content_score) / 2)
    
    def _analyze_rule_of_thirds(self, img_array: np.ndarray) -> float:
        """Analyze alignment with rule of thirds"""
        h, w = img_array.shape[:2]
        
        # Third lines
        third_lines_h = [h // 3, 2 * h // 3]
        third_lines_v = [w // 3, 2 * w // 3]
        
        return self._measure_content_along_lines(img_array, third_lines_h, third_lines_v)
    
    def _measure_content_along_lines(self, img_array: np.ndarray, h_lines: List[float], v_lines: List[float]) -> float:
        """Measure how much content aligns with compositional lines"""
        gray = np.mean(img_array, axis=2)
        edges = self._simple_edge_detection(gray)
        
        total_score = 0.0
        line_count = 0
        
        # Check horizontal lines
        for line_y in h_lines:
            if 0 < line_y < gray.shape[0]:
                line_content = edges[int(line_y), :]
                score = np.mean(line_content)
                total_score += score
                line_count += 1
        
        # Check vertical lines  
        for line_x in v_lines:
            if 0 < line_x < gray.shape[1]:
                line_content = edges[:, int(line_x)]
                score = np.mean(line_content)
                total_score += score
                line_count += 1
        
        return float(total_score / line_count if line_count > 0 else 0.0)
    
    def _analyze_whitespace(self, img_array: np.ndarray) -> Dict:
        """Analyze whitespace and breathing room"""
        gray = np.mean(img_array, axis=2)
        
        # Consider bright areas as potential whitespace
        brightness_threshold = 200
        whitespace_mask = gray > brightness_threshold
        
        whitespace_percentage = np.sum(whitespace_mask) / gray.size
        
        # Analyze distribution of whitespace
        h, w = gray.shape
        
        # Check margins
        margin_size = min(h, w) // 10
        top_margin = np.mean(whitespace_mask[:margin_size, :])
        bottom_margin = np.mean(whitespace_mask[-margin_size:, :])
        left_margin = np.mean(whitespace_mask[:, :margin_size])
        right_margin = np.mean(whitespace_mask[:, -margin_size:])
        
        return {
            'total_whitespace': float(whitespace_percentage),
            'margin_usage': {
                'top': float(top_margin),
                'bottom': float(bottom_margin),
                'left': float(left_margin),
                'right': float(right_margin)
            },
            'breathing_room': self._classify_whitespace_style(whitespace_percentage)
        }
    
    def _classify_whitespace_style(self, whitespace_percentage: float) -> str:
        """Classify whitespace usage style"""
        if whitespace_percentage > 0.4:
            return 'minimalist'
        elif whitespace_percentage > 0.25:
            return 'balanced'
        elif whitespace_percentage > 0.1:
            return 'compact'
        else:
            return 'dense'
    
    def _detect_focal_points(self, img_array: np.ndarray) -> Dict:
        """Detect visual focal points in the image"""
        gray = np.mean(img_array, axis=2)
        
        # Use contrast and edge density to find focal points
        edges = self._simple_edge_detection(gray)
        
        # Divide image into regions and find high-activity areas
        h, w = gray.shape
        regions = []
        
        for y in range(0, h, h//8):
            for x in range(0, w, w//8):
                region = edges[y:min(y+h//8, h), x:min(x+w//8, w)]
                activity = np.mean(region)
                regions.append({
                    'position': (x + w//16, y + h//16),  # Center of region
                    'activity': float(activity),
                    'relative_position': (
                        (x + w//16) / w,  # Normalized x
                        (y + h//16) / h   # Normalized y
                    )
                })
        
        # Sort by activity level
        regions.sort(key=lambda r: r['activity'], reverse=True)
        
        return {
            'primary_focal_point': regions[0]['relative_position'] if regions else (0.5, 0.5),
            'focal_strength': regions[0]['activity'] if regions else 0.0,
            'focal_point_count': len([r for r in regions if r['activity'] > np.mean([r['activity'] for r in regions])])
        }
    
    def _classify_layout_style(self, golden_score: float, thirds_score: float, whitespace: Dict) -> str:
        """Classify the overall layout style"""
        if golden_score > 0.7:
            return 'classical'
        elif thirds_score > 0.6:
            return 'photographic'
        elif whitespace['total_whitespace'] > 0.4:
            return 'minimalist'
        elif whitespace['total_whitespace'] < 0.15:
            return 'maximalist'
        else:
            return 'balanced'
    
    def _analyze_textures(self, img: Image, img_array: np.ndarray) -> Dict:
        """Analyze texture patterns and surface qualities"""
        
        # Convert to grayscale for texture analysis
        gray = np.mean(img_array, axis=2)
        
        # Texture roughness (using local standard deviation)
        roughness = self._calculate_roughness(gray)
        
        # Pattern regularity
        regularity = self._calculate_texture_regularity(gray)
        
        # Surface smoothness indicators
        smoothness = self._calculate_smoothness(gray)
        
        return {
            'roughness_level': roughness,
            'pattern_regularity': regularity,
            'surface_smoothness': smoothness,
            'texture_type': self._classify_texture_type(roughness, regularity, smoothness),
            'brand_texture_signals': self._interpret_texture_for_brand(roughness, regularity, smoothness)
        }
    
    def _calculate_roughness(self, gray: np.ndarray) -> float:
        """Calculate texture roughness"""
        # Use local standard deviation as roughness measure
        h, w = gray.shape
        roughness_values = []
        
        window_size = min(h, w) // 20
        if window_size < 3:
            window_size = 3
        
        for y in range(0, h-window_size, window_size//2):
            for x in range(0, w-window_size, window_size//2):
                window = gray[y:y+window_size, x:x+window_size]
                roughness_values.append(np.std(window))
        
        return float(np.mean(roughness_values) / 128)  # Normalized
    
    def _calculate_texture_regularity(self, gray: np.ndarray) -> float:
        """Calculate how regular/repeating the texture is"""
        # Simple autocorrelation-like measure
        h, w = gray.shape
        
        # Sample different offsets and measure similarity
        similarities = []
        max_offset = min(h, w) // 10
        
        if max_offset < 2:
            return 0.5
        
        for offset in range(1, max_offset):
            # Compare image with itself shifted
            original = gray[:-offset, :-offset]
            shifted = gray[offset:, offset:]
            
            if original.size > 0:
                correlation = np.corrcoef(original.flat, shifted.flat)[0, 1]
                if not np.isnan(correlation):
                    similarities.append(abs(correlation))
        
        return float(np.mean(similarities) if similarities else 0.5)
    
    def _calculate_smoothness(self, gray: np.ndarray) -> float:
        """Calculate surface smoothness"""
        # Use gradient magnitude as smoothness inverse
        grad_x = np.diff(gray, axis=1)
        grad_y = np.diff(gray, axis=0)
        
        # Calculate mean gradient magnitude
        if grad_x.size > 0 and grad_y.size > 0:
            grad_magnitude = np.sqrt(
                grad_x[:grad_y.shape[0], :]**2 + grad_y[:, :grad_x.shape[1]]**2
            )
            smoothness = 1 / (1 + np.mean(grad_magnitude) / 128)
        else:
            smoothness = 0.5
        
        return float(smoothness)
    
    def _classify_texture_type(self, roughness: float, regularity: float, smoothness: float) -> str:
        """Classify the type of texture"""
        if smoothness > 0.7:
            return 'smooth'
        elif regularity > 0.6:
            return 'patterned'
        elif roughness > 0.6:
            return 'rough'
        else:
            return 'organic'
    
    def _interpret_texture_for_brand(self, roughness: float, regularity: float, smoothness: float) -> Dict:
        """Interpret texture qualities for brand implications"""
        
        brand_signals = {}
        
        if smoothness > 0.7:
            brand_signals['luxury_indicator'] = 0.8
            brand_signals['sophistication'] = 0.9
        elif roughness > 0.6:
            brand_signals['authenticity'] = 0.8
            brand_signals['craftsmanship'] = 0.7
        
        if regularity > 0.7:
            brand_signals['precision'] = 0.9
            brand_signals['reliability'] = 0.8
        
        return brand_signals
    
    def _detect_typography_patterns(self, img: Image, img_array: np.ndarray) -> Dict:
        """Detect typography and text-related patterns"""
        
        # This is a simplified text detection
        # In production, would use OCR or text detection models
        
        gray = np.mean(img_array, axis=2)
        
        # Look for text-like patterns (high contrast, linear elements)
        edges = self._simple_edge_detection(gray)
        
        # Detect horizontal line patterns (potential text)
        h_lines = self._detect_horizontal_lines(edges)
        
        # Detect character-like patterns
        char_patterns = self._detect_character_patterns(edges)
        
        return {
            'text_likelihood': float(h_lines * char_patterns),
            'horizontal_text_patterns': h_lines,
            'character_density': char_patterns,
            'typography_style_hints': self._infer_typography_style(h_lines, char_patterns)
        }
    
    def _detect_horizontal_lines(self, edges: np.ndarray) -> float:
        """Detect horizontal line patterns typical of text"""
        h, w = edges.shape
        
        # Sum edges along rows
        row_sums = np.sum(edges, axis=1)
        
        # Look for regular spacing between lines
        if len(row_sums) < 10:
            return 0.0
        
        # Find peaks (potential text lines)
        peaks = []
        for i in range(1, len(row_sums)-1):
            if row_sums[i] > row_sums[i-1] and row_sums[i] > row_sums[i+1]:
                peaks.append(i)
        
        if len(peaks) < 2:
            return 0.0
        
        # Check for regular spacing
        spacings = np.diff(peaks)
        spacing_regularity = 1 / (1 + np.var(spacings) / (np.mean(spacings) + 1))
        
        return min(1.0, spacing_regularity)
    
    def _detect_character_patterns(self, edges: np.ndarray) -> float:
        """Detect character-like patterns"""
        # Look for small rectangular regions with edges
        # This is very simplified - real implementation would be more sophisticated
        
        h, w = edges.shape
        char_score = 0.0
        
        # Sample small regions and check for character-like properties
        samples = min(100, (h // 10) * (w // 10))
        
        for _ in range(samples):
            y = np.random.randint(0, max(1, h-10))
            x = np.random.randint(0, max(1, w-10))
            
            region = edges[y:y+10, x:x+10]
            if region.size > 0:
                # Character-like: some edges, not too dense, somewhat rectangular
                edge_density = np.mean(region)
                if 0.1 < edge_density < 0.7:
                    char_score += 1
        
        return min(1.0, char_score / samples if samples > 0 else 0.0)
    
    def _infer_typography_style(self, h_lines: float, char_density: float) -> Dict:
        """Infer typography style characteristics"""
        
        if h_lines > 0.7 and char_density > 0.5:
            return {
                'text_present': True,
                'style_hints': ['serif', 'readable', 'structured'],
                'formality_level': 'high' if h_lines > 0.8 else 'medium'
            }
        elif h_lines > 0.5:
            return {
                'text_present': True, 
                'style_hints': ['simple', 'clean'],
                'formality_level': 'medium'
            }
        else:
            return {
                'text_present': False,
                'style_hints': [],
                'formality_level': 'unknown'
            }
    
    def _identify_cultural_signals(self, img: Image, description: str) -> Dict:
        """Identify cultural and contextual signals"""
        
        # Parse description for cultural keywords
        cultural_keywords = self._extract_cultural_keywords(description)
        
        # Analyze color for cultural associations
        color_culture = self._analyze_color_culture(img)
        
        return {
            'cultural_keywords': cultural_keywords,
            'color_cultural_signals': color_culture,
            'context_category': self._classify_cultural_context(cultural_keywords, color_culture)
        }
    
    def _extract_cultural_keywords(self, description: str) -> List[str]:
        """Extract culturally significant keywords"""
        if not description:
            return []
        
        cultural_terms = {
            'luxury': ['luxury', 'premium', 'expensive', 'exclusive', 'high-end', 'designer'],
            'natural': ['natural', 'organic', 'eco', 'sustainable', 'green', 'earth'],
            'modern': ['modern', 'contemporary', 'sleek', 'minimalist', 'clean'],
            'traditional': ['traditional', 'classic', 'vintage', 'antique', 'heritage'],
            'industrial': ['industrial', 'urban', 'concrete', 'steel', 'metal'],
            'artisanal': ['handmade', 'craft', 'artisan', 'bespoke', 'custom']
        }
        
        found_signals = {}
        description_lower = description.lower()
        
        for category, terms in cultural_terms.items():
            matches = [term for term in terms if term in description_lower]
            if matches:
                found_signals[category] = matches
        
        return found_signals
    
    def _analyze_color_culture(self, img: Image) -> Dict:
        """Analyze color for cultural associations"""
        img_array = np.array(img)
        
        # Get dominant colors
        colors = self.semantic_analyzer._extract_colors(img_array)
        
        cultural_signals = {}
        
        if 'most_common' in colors:
            for color in colors['most_common'][:3]:
                rgb = color['rgb']
                cultural_signals.update(self._color_cultural_associations(rgb))
        
        return cultural_signals
    
    def _color_cultural_associations(self, rgb: List[int]) -> Dict:
        """Map RGB colors to cultural associations"""
        r, g, b = rgb
        
        associations = {}
        
        # Gold/Yellow associations
        if r > 200 and g > 180 and b < 100:
            associations['luxury'] = 0.8
            associations['premium'] = 0.7
        
        # Deep blues
        if b > 150 and r < 100 and g < 100:
            associations['trust'] = 0.8
            associations['corporate'] = 0.7
        
        # Earth tones
        if 100 < r < 160 and 80 < g < 120 and 50 < b < 90:
            associations['natural'] = 0.8
            associations['organic'] = 0.7
        
        # High saturation
        if max(rgb) - min(rgb) > 100:
            associations['energetic'] = 0.7
            associations['youthful'] = 0.6
        
        return associations
    
    def _classify_cultural_context(self, keywords: Dict, color_signals: Dict) -> str:
        """Classify the overall cultural context"""
        
        # Count signals by category
        signal_weights = {}
        
        # Add keyword signals
        for category, terms in keywords.items():
            signal_weights[category] = len(terms) * 0.5
        
        # Add color signals
        for signal, weight in color_signals.items():
            signal_weights[signal] = signal_weights.get(signal, 0) + weight
        
        if not signal_weights:
            return 'neutral'
        
        return max(signal_weights, key=signal_weights.get)
    
    def _detect_luxury_signals(self, img: Image, img_array: np.ndarray) -> Dict:
        """Detect visual indicators of luxury positioning"""
        
        # Color sophistication (muted, harmonious colors)
        colors = self.semantic_analyzer._extract_colors(img_array)
        
        luxury_score = 0.0
        
        # Check for gold/metallic colors
        if 'most_common' in colors:
            for color in colors['most_common'][:5]:
                rgb = color['rgb']
                r, g, b = rgb
                
                # Gold/metallic detection
                if r > 180 and g > 150 and b < 120:
                    luxury_score += 0.3
                
                # Deep, rich colors
                if color['saturation'] > 0.6 and color['brightness'] < 0.7:
                    luxury_score += 0.2
        
        # Analyze whitespace (luxury often has generous whitespace)
        whitespace = self._analyze_whitespace(img_array)['total_whitespace']
        if whitespace > 0.4:
            luxury_score += 0.3
        
        # Check for minimal, clean composition
        edges = self._simple_edge_detection(np.mean(img_array, axis=2))
        edge_density = np.mean(edges)
        
        if edge_density < 0.3:  # Clean, minimal
            luxury_score += 0.2
        
        return {
            'luxury_score': min(1.0, luxury_score),
            'luxury_indicators': {
                'metallic_colors': any(r > 180 and g > 150 and b < 120 
                                     for color in colors.get('most_common', [])
                                     for r, g, b in [color['rgb']]),
                'generous_whitespace': whitespace > 0.4,
                'minimal_composition': edge_density < 0.3,
                'sophisticated_colors': len([c for c in colors.get('most_common', []) 
                                           if c['saturation'] > 0.6 and c['brightness'] < 0.7]) > 0
            }
        }
    
    def _analyze_energy_levels(self, img_array: np.ndarray) -> Dict:
        """Analyze visual energy and dynamism"""
        
        gray = np.mean(img_array, axis=2)
        
        # Motion blur detection (simplified)
        motion_score = self._detect_motion_blur(gray)
        
        # Color vibrancy
        vibrancy = self._calculate_color_vibrancy(img_array)
        
        # Contrast energy
        contrast_energy = np.std(gray) / 128
        
        # Composition dynamism (diagonal lines, asymmetry)
        dynamism = self._calculate_dynamism(gray)
        
        total_energy = (motion_score + vibrancy + contrast_energy + dynamism) / 4
        
        return {
            'total_energy': float(total_energy),
            'motion_indicators': float(motion_score),
            'color_vibrancy': float(vibrancy),
            'contrast_energy': float(contrast_energy),
            'compositional_dynamism': float(dynamism),
            'energy_level': self._classify_energy_level(total_energy)
        }
    
    def _detect_motion_blur(self, gray: np.ndarray) -> float:
        """Detect motion blur indicators"""
        # Look for directional streaking
        h, w = gray.shape
        
        # Check for horizontal streaking
        h_blur = 0
        for y in range(1, h-1):
            row_diff = np.diff(gray[y, :])
            if np.std(row_diff) < np.mean(np.abs(row_diff)) * 0.5:
                h_blur += 1
        
        # Check for vertical streaking
        v_blur = 0
        for x in range(1, w-1):
            col_diff = np.diff(gray[:, x])
            if np.std(col_diff) < np.mean(np.abs(col_diff)) * 0.5:
                v_blur += 1
        
        blur_score = max(h_blur / h, v_blur / w)
        return min(1.0, blur_score)
    
    def _calculate_color_vibrancy(self, img_array: np.ndarray) -> float:
        """Calculate color vibrancy"""
        # Sample pixels and calculate average saturation
        h, w = img_array.shape[:2]
        sample_size = min(1000, h * w)
        
        saturations = []
        for _ in range(sample_size):
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            pixel = img_array[y, x]
            r, g, b = pixel[0]/255, pixel[1]/255, pixel[2]/255
            _, s, _ = colorsys.rgb_to_hsv(r, g, b)
            saturations.append(s)
        
        return float(np.mean(saturations))
    
    def _calculate_dynamism(self, gray: np.ndarray) -> float:
        """Calculate compositional dynamism"""
        # Detect diagonal patterns
        edges = self._simple_edge_detection(gray)
        
        # Create diagonal kernels
        diag1 = np.array([[1, 0, -1], [0, 0, 0], [-1, 0, 1]])  # / diagonal
        diag2 = np.array([[-1, 0, 1], [0, 0, 0], [1, 0, -1]])  # \ diagonal
        
        h, w = edges.shape
        diag_strength = 0
        
        for y in range(1, h-1):
            for x in range(1, w-1):
                region = edges[y-1:y+2, x-1:x+2]
                d1 = np.sum(region * diag1)
                d2 = np.sum(region * diag2)
                diag_strength += max(abs(d1), abs(d2))
        
        return min(1.0, diag_strength / (h * w * 255))
    
    def _classify_energy_level(self, energy: float) -> str:
        """Classify energy level"""
        if energy > 0.7:
            return 'high'
        elif energy > 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _detect_archetype_signals(self, img: Image, img_array: np.ndarray) -> Dict:
        """Detect brand archetype signals in the image"""
        
        # Analyze various visual elements for archetype indicators
        
        # Get color and composition analysis
        colors = self.semantic_analyzer._extract_colors(img_array)
        composition = self.semantic_analyzer._analyze_composition(img)
        visual_props = self.semantic_analyzer._calculate_visual_properties(img_array)
        
        archetype_signals = {}
        
        # The Innocent (clean, simple, bright)
        if (visual_props['brightness'] > 0.6 and 
            visual_props['saturation'] < 0.5 and 
            composition['orientation'] == 'square'):
            archetype_signals['innocent'] = 0.7
        
        # The Explorer (dynamic, varied colors, movement)
        if (visual_props['saturation'] > 0.6 and 
            len(colors.get('most_common', [])) > 5):
            archetype_signals['explorer'] = 0.6
        
        # The Sage (muted, balanced, sophisticated)
        if (visual_props['brightness'] > 0.4 and 
            visual_props['brightness'] < 0.8 and
            visual_props['saturation'] < 0.4):
            archetype_signals['sage'] = 0.7
        
        # The Hero (bold, strong contrast)
        if visual_props['contrast'] > 0.6:
            archetype_signals['hero'] = 0.6
        
        # The Outlaw (dark, high contrast, asymmetric)
        if (visual_props['brightness'] < 0.4 and 
            visual_props['contrast'] > 0.7):
            archetype_signals['outlaw'] = 0.7
        
        # The Magician (mysterious, complex colors)
        if (visual_props['saturation'] > 0.7 and 
            visual_props['brightness'] < 0.6):
            archetype_signals['magician'] = 0.6
        
        # The Regular Guy/Gal (balanced, moderate everything)
        if (0.4 < visual_props['brightness'] < 0.7 and
            0.3 < visual_props['saturation'] < 0.6 and
            0.3 < visual_props['contrast'] < 0.6):
            archetype_signals['everyman'] = 0.8
        
        # The Lover (warm colors, soft, romantic)
        warm_colors = self._count_warm_colors(colors)
        if warm_colors > 0.6 and visual_props['contrast'] < 0.5:
            archetype_signals['lover'] = 0.7
        
        # The Jester (bright, varied, playful)
        if (visual_props['saturation'] > 0.7 and 
            visual_props['brightness'] > 0.6):
            archetype_signals['jester'] = 0.6
        
        # The Caregiver (soft, nurturing colors)
        if (0.5 < visual_props['brightness'] < 0.8 and
            visual_props['saturation'] < 0.5):
            archetype_signals['caregiver'] = 0.6
        
        # The Creator (complex, detailed, textured)
        texture_complexity = self._assess_texture_complexity(img_array)
        if texture_complexity > 0.6:
            archetype_signals['creator'] = 0.7
        
        # The Ruler (sophisticated, luxury indicators)
        luxury = self._detect_luxury_signals(img, img_array)
        if luxury['luxury_score'] > 0.6:
            archetype_signals['ruler'] = luxury['luxury_score']
        
        return archetype_signals
    
    def _count_warm_colors(self, colors: Dict) -> float:
        """Count proportion of warm colors"""
        if 'most_common' not in colors:
            return 0.0
        
        warm_count = 0
        total_count = len(colors['most_common'])
        
        for color in colors['most_common']:
            hue = color.get('hue', 0)
            # Warm colors: red to yellow (0-60 and 300-360 degrees)
            if (0 <= hue <= 60) or (300 <= hue <= 360):
                warm_count += 1
        
        return warm_count / max(1, total_count)
    
    def _assess_texture_complexity(self, img_array: np.ndarray) -> float:
        """Assess texture complexity"""
        gray = np.mean(img_array, axis=2)
        edges = self._simple_edge_detection(gray)
        
        # Complex textures have high edge density and variation
        edge_density = np.mean(edges)
        edge_variation = np.std(edges)
        
        complexity = (edge_density + edge_variation / 128) / 2
        return min(1.0, complexity)
    
    def _extract_brandable_elements(self, img: Image, img_array: np.ndarray) -> Dict:
        """Extract elements that can be used for brand generation"""
        
        # Get all the analyses
        colors = self.semantic_analyzer._extract_colors(img_array)
        composition = self.semantic_analyzer._analyze_composition(img)
        visual_props = self.semantic_analyzer._calculate_visual_properties(img_array)
        
        # Extract key brandable elements
        brandable = {}
        
        # Color palette for brand
        if 'most_common' in colors:
            brand_colors = colors['most_common'][:5]
            brandable['color_palette'] = {
                'primary': brand_colors[0]['hex'] if brand_colors else '#000000',
                'secondary': brand_colors[1]['hex'] if len(brand_colors) > 1 else '#666666',
                'accents': [c['hex'] for c in brand_colors[2:5]],
                'palette_mood': self._classify_palette_mood(brand_colors)
            }
        
        # Layout principles
        brandable['layout_DNA'] = {
            'preferred_aspect_ratio': composition['aspect_ratio'],
            'visual_balance': self._analyze_visual_weight(img_array)['balance_type'],
            'whitespace_style': self._analyze_whitespace(img_array)['breathing_room']
        }
        
        # Visual style characteristics
        brandable['visual_style'] = {
            'energy_level': self._analyze_energy_levels(img_array)['energy_level'],
            'sophistication_level': 'high' if visual_props['contrast'] < 0.5 and visual_props['saturation'] < 0.6 else 'medium',
            'approach': 'minimalist' if visual_props['brightness'] > 0.6 and visual_props['saturation'] < 0.4 else 'bold'
        }
        
        # Typography hints
        typography_analysis = self._detect_typography_patterns(img, img_array)
        if typography_analysis['text_likelihood'] > 0.5:
            brandable['typography_hints'] = typography_analysis['typography_style_hints']
        
        return brandable

    def _classify_palette_mood(self, colors: List[Dict]) -> str:
        """Classify the mood of a color palette"""
        if not colors:
            return 'neutral'
        
        # Analyze brightness and saturation
        avg_brightness = np.mean([c['brightness'] for c in colors])
        avg_saturation = np.mean([c['saturation'] for c in colors])
        
        # Analyze hue distribution
        hues = [c['hue'] for c in colors]
        warm_colors = len([h for h in hues if (0 <= h <= 60) or (300 <= h <= 360)])
        cool_colors = len([h for h in hues if 180 <= h <= 300])
        
        # Classify mood based on characteristics
        if avg_brightness > 0.7 and avg_saturation < 0.5:
            return 'calm'
        elif avg_brightness < 0.3:
            return 'dramatic'
        elif avg_saturation > 0.7:
            if warm_colors > cool_colors:
                return 'energetic'
            else:
                return 'vibrant'
        elif warm_colors > cool_colors:
            return 'warm'
        elif cool_colors > warm_colors:
            return 'cool'
        else:
            return 'balanced'


def analyze_deep_source(image_path: str, description: str = "") -> Dict:
    """
    Simple integration function for deep source analysis
    
    Returns comprehensive brand DNA extracted from source material
    """
    analyzer = DeepSourceAnalyzer()
    return analyzer.analyze_source_material(image_path, description)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        description = sys.argv[2] if len(sys.argv) > 2 else ""
        
        print(f"Deep analyzing: {image_path}")
        result = analyze_deep_source(image_path, description)
        
        if result and 'error' not in result:
            print("\n=== DEEP SOURCE ANALYSIS ===")
            
            # Brand DNA
            if 'brand_dna' in result:
                dna = result['brand_dna']
                print("\n🧬 Brand DNA:")
                if 'color_sophistication' in dna:
                    print(f"  Color Sophistication: {dna['color_sophistication']['sophistication_level']:.2f}")
                    print(f"  Color Scheme: {dna['color_sophistication']['color_scheme_type']}")
                
                if 'luxury_indicators' in dna:
                    print(f"  Luxury Score: {dna['luxury_indicators']['luxury_score']:.2f}")
                
                if 'energy_profile' in dna:
                    print(f"  Energy Level: {dna['energy_profile']['energy_level']}")
            
            # Layout Principles
            if 'layout_principles' in result:
                layout = result['layout_principles']
                print(f"\n📐 Layout Style: {layout.get('layout_style', 'unknown')}")
                print(f"  Golden Ratio Alignment: {layout.get('golden_ratio_alignment', 0):.2f}")
                print(f"  Rule of Thirds: {layout.get('rule_of_thirds_score', 0):.2f}")
            
            # Brandable Elements
            if 'brandable_elements' in result:
                brandable = result['brandable_elements']
                print(f"\n🎨 Brandable Elements:")
                if 'color_palette' in brandable:
                    palette = brandable['color_palette']
                    print(f"  Primary Color: {palette.get('primary', 'N/A')}")
                    print(f"  Palette Mood: {palette.get('palette_mood', 'neutral')}")
                
                if 'visual_style' in brandable:
                    style = brandable['visual_style']
                    print(f"  Energy: {style.get('energy_level', 'unknown')}")
                    print(f"  Approach: {style.get('approach', 'unknown')}")
        else:
            print(f"Analysis failed: {result.get('error', 'Unknown error')}")
    else:
        print("Usage: python deep_source_analyzer.py <image_path> [description]")