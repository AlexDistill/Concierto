#!/usr/bin/env python3
"""
Optimized Deep Source Material Analysis Engine
Fast, efficient brand DNA extraction with caching and simplified algorithms
"""

import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import colorsys
from datetime import datetime
from semantic_analyzer import SemanticAnalyzer

class DeepSourceAnalyzerOptimized:
    """
    Optimized deep analysis focusing on speed and essential brand elements
    Uses sampling, caching, and simplified algorithms
    """
    
    def __init__(self):
        self.semantic_analyzer = SemanticAnalyzer()
        self._cache = {}  # Cache for repeated calculations
        
    def analyze_source_material(self, image_path: str, description: str = "") -> Dict:
        """
        Fast analysis of source material for brand DNA extraction
        Optimized for speed while maintaining quality
        """
        try:
            # Check cache first
            cache_key = f"{image_path}_{description}"
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            # Get basic semantic analysis (already fast)
            base_analysis = self.semantic_analyzer.analyze_image(image_path, description)
            
            if 'error' in base_analysis:
                return base_analysis
            
            # Load and downsample image for faster processing
            img = Image.open(image_path).convert('RGB')
            
            # Downsample if image is large
            max_dimension = 512  # Process at lower resolution
            if img.width > max_dimension or img.height > max_dimension:
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            
            img_array = np.array(img)
            
            # Fast brand analysis with essential elements only
            analysis = {
                **base_analysis,
                'brand_dna': self._extract_brand_dna_fast(img_array),
                'layout_principles': self._analyze_layout_fast(img, img_array),
                'brandable_elements': self._extract_brandable_fast(img_array, base_analysis),
                'analysis_type': 'deep_source_optimized_v1'
            }
            
            # Cache result
            self._cache[cache_key] = analysis
            
            return analysis
            
        except Exception as e:
            return {
                'error': str(e),
                'analyzed_at': datetime.now().isoformat()
            }
    
    def _extract_brand_dna_fast(self, img_array: np.ndarray) -> Dict:
        """Fast extraction of essential brand DNA"""
        
        # Use smaller sample size
        h, w = img_array.shape[:2]
        sample_size = min(500, h * w // 10)  # Much smaller sample
        
        # Fast color sophistication check
        color_sophistication = self._fast_color_sophistication(img_array, sample_size)
        
        # Quick energy analysis
        energy_level = self._fast_energy_analysis(img_array)
        
        # Simple luxury detection
        luxury_indicators = self._fast_luxury_detection(img_array, sample_size)
        
        # Quick archetype signals
        archetype_signals = self._fast_archetype_detection(img_array)
        
        return {
            'color_sophistication': color_sophistication,
            'energy_level': energy_level,
            'luxury_score': luxury_indicators,
            'dominant_archetype': archetype_signals,
            'processing_time': 'optimized'
        }
    
    def _fast_color_sophistication(self, img_array: np.ndarray, sample_size: int) -> float:
        """Fast color sophistication analysis"""
        h, w = img_array.shape[:2]
        
        # Random sampling for speed
        saturations = []
        for _ in range(min(sample_size, 200)):  # Cap at 200 samples
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            pixel = img_array[y, x]
            r, g, b = pixel[0]/255, pixel[1]/255, pixel[2]/255
            _, s, _ = colorsys.rgb_to_hsv(r, g, b)
            saturations.append(s)
        
        # Simple sophistication: moderate saturation = sophisticated
        avg_sat = np.mean(saturations)
        if 0.2 < avg_sat < 0.6:
            return 0.8  # Sophisticated
        elif avg_sat < 0.2:
            return 0.9  # Very sophisticated (muted)
        else:
            return 0.4  # Less sophisticated (too vibrant)
    
    def _fast_energy_analysis(self, img_array: np.ndarray) -> str:
        """Fast energy level detection"""
        # Use standard deviation as quick energy metric
        gray = np.mean(img_array, axis=2)
        
        # Downsample for speed
        if gray.shape[0] > 100:
            gray = gray[::4, ::4]  # Take every 4th pixel
        
        contrast = np.std(gray) / 128
        
        if contrast > 0.5:
            return 'high'
        elif contrast > 0.3:
            return 'medium'
        else:
            return 'low'
    
    def _fast_luxury_detection(self, img_array: np.ndarray, sample_size: int) -> float:
        """Fast luxury indicator detection"""
        luxury_score = 0.0
        
        # Check for dark/muted palette (often luxury)
        mean_brightness = np.mean(img_array) / 255
        if mean_brightness < 0.5:
            luxury_score += 0.3
        
        # Check for low saturation (sophisticated)
        h, w = img_array.shape[:2]
        sat_samples = []
        for _ in range(min(100, sample_size)):
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            pixel = img_array[y, x]
            r, g, b = pixel[0]/255, pixel[1]/255, pixel[2]/255
            _, s, _ = colorsys.rgb_to_hsv(r, g, b)
            sat_samples.append(s)
        
        if np.mean(sat_samples) < 0.4:
            luxury_score += 0.4
        
        return min(1.0, luxury_score)
    
    def _fast_archetype_detection(self, img_array: np.ndarray) -> str:
        """Fast brand archetype detection"""
        # Simplified archetype detection based on visual properties
        
        brightness = np.mean(img_array) / 255
        gray = np.mean(img_array, axis=2)
        contrast = np.std(gray) / 128
        
        # Simple rules for archetype
        if brightness > 0.7 and contrast < 0.3:
            return 'innocent'  # Bright and soft
        elif brightness < 0.3 and contrast > 0.5:
            return 'outlaw'  # Dark and high contrast
        elif brightness > 0.5 and contrast > 0.5:
            return 'hero'  # Bright and bold
        elif 0.4 < brightness < 0.6 and contrast < 0.4:
            return 'sage'  # Balanced and calm
        else:
            return 'everyman'  # Default balanced
    
    def _analyze_layout_fast(self, img: Image, img_array: np.ndarray) -> Dict:
        """Fast layout analysis"""
        width, height = img.size
        
        # Quick aspect ratio analysis
        aspect_ratio = width / height
        
        # Simple layout classification
        if 0.9 < aspect_ratio < 1.1:
            layout_style = 'balanced'
        elif aspect_ratio > 1.5:
            layout_style = 'horizontal'
        elif aspect_ratio < 0.67:
            layout_style = 'vertical'
        else:
            layout_style = 'standard'
        
        # Quick focal point detection (center vs edges)
        h, w = img_array.shape[:2]
        center_region = img_array[h//3:2*h//3, w//3:2*w//3]
        center_activity = np.std(center_region)
        
        edge_samples = [
            img_array[:h//3, :],  # top
            img_array[2*h//3:, :],  # bottom
        ]
        edge_activity = np.mean([np.std(region) for region in edge_samples])
        
        if center_activity > edge_activity * 1.2:
            focal_strategy = 'centered'
        else:
            focal_strategy = 'distributed'
        
        return {
            'aspect_ratio': aspect_ratio,
            'layout_style': layout_style,
            'focal_strategy': focal_strategy
        }
    
    def _extract_brandable_fast(self, img_array: np.ndarray, base_analysis: Dict) -> Dict:
        """Fast extraction of brandable elements"""
        
        brandable = {}
        
        # Use existing color analysis
        if 'colors' in base_analysis and 'most_common' in base_analysis['colors']:
            colors = base_analysis['colors']['most_common'][:5]
            if colors:
                brandable['primary_color'] = colors[0]['hex']
                brandable['secondary_color'] = colors[1]['hex'] if len(colors) > 1 else None
                
                # Quick palette mood
                avg_brightness = np.mean([c.get('brightness', 0.5) for c in colors[:3]])
                if avg_brightness > 0.7:
                    brandable['palette_mood'] = 'bright'
                elif avg_brightness < 0.3:
                    brandable['palette_mood'] = 'dark'
                else:
                    brandable['palette_mood'] = 'balanced'
        
        # Quick visual style
        brightness = base_analysis.get('visual_properties', {}).get('brightness', 0.5)
        contrast = base_analysis.get('visual_properties', {}).get('contrast', 0.5)
        
        if contrast > 0.6:
            brandable['visual_approach'] = 'bold'
        elif brightness > 0.7:
            brandable['visual_approach'] = 'light'
        elif brightness < 0.3:
            brandable['visual_approach'] = 'dramatic'
        else:
            brandable['visual_approach'] = 'balanced'
        
        return brandable


def analyze_deep_source_optimized(image_path: str, description: str = "") -> Dict:
    """
    Optimized deep source analysis - fast and efficient
    """
    analyzer = DeepSourceAnalyzerOptimized()
    return analyzer.analyze_source_material(image_path, description)


if __name__ == "__main__":
    import sys
    import time
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        description = sys.argv[2] if len(sys.argv) > 2 else ""
        
        print(f"Analyzing (optimized): {image_path}")
        
        start_time = time.time()
        result = analyze_deep_source_optimized(image_path, description)
        elapsed = time.time() - start_time
        
        if result and 'error' not in result:
            print(f"\n=== OPTIMIZED DEEP ANALYSIS ({elapsed:.2f}s) ===")
            
            # Brand DNA
            if 'brand_dna' in result:
                dna = result['brand_dna']
                print(f"\n🧬 Brand DNA:")
                print(f"  Color Sophistication: {dna.get('color_sophistication', 0):.2f}")
                print(f"  Energy Level: {dna.get('energy_level', 'unknown')}")
                print(f"  Luxury Score: {dna.get('luxury_score', 0):.2f}")
                print(f"  Archetype: {dna.get('dominant_archetype', 'unknown')}")
            
            # Layout
            if 'layout_principles' in result:
                layout = result['layout_principles']
                print(f"\n📐 Layout:")
                print(f"  Style: {layout.get('layout_style', 'unknown')}")
                print(f"  Focus: {layout.get('focal_strategy', 'unknown')}")
            
            # Brandable Elements
            if 'brandable_elements' in result:
                brandable = result['brandable_elements']
                print(f"\n🎨 Brandable Elements:")
                print(f"  Primary Color: {brandable.get('primary_color', 'N/A')}")
                print(f"  Palette Mood: {brandable.get('palette_mood', 'N/A')}")
                print(f"  Visual Approach: {brandable.get('visual_approach', 'N/A')}")
            
            print(f"\n⚡ Processing Time: {elapsed:.2f}s")
        else:
            print(f"Analysis failed: {result.get('error', 'Unknown error')}")
    else:
        print("Usage: python deep_source_analyzer_optimized.py <image_path> [description]")