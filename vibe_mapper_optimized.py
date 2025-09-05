#!/usr/bin/env python3
"""
Optimized Vibe Intensity Mapping System
Fast emotional intensity quantification with simplified calculations
"""

import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import colorsys
from datetime import datetime
from deep_source_analyzer_optimized import DeepSourceAnalyzerOptimized

class VibeMapperOptimized:
    """
    Fast vibe mapping focusing on essential emotional characteristics
    Uses sampling and simplified calculations for speed
    """
    
    def __init__(self):
        self.deep_analyzer = DeepSourceAnalyzerOptimized()
        self._cache = {}
        
    def map_vibe_intensity(self, image_path: str, description: str = "") -> Dict:
        """
        Fast vibe intensity mapping with essential characteristics
        """
        try:
            # Check cache
            cache_key = f"{image_path}_{description}"
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            # Get optimized deep analysis
            deep_analysis = self.deep_analyzer.analyze_source_material(image_path, description)
            
            if 'error' in deep_analysis:
                return deep_analysis
            
            # Load and downsample image
            img = Image.open(image_path).convert('RGB')
            if img.width > 256 or img.height > 256:
                img.thumbnail((256, 256), Image.Resampling.LANCZOS)
            
            img_array = np.array(img)
            
            # Fast vibe mapping
            vibe_map = {
                'analyzed_at': datetime.now().isoformat(),
                'source_path': str(image_path),
                'vibe_spectrum': self._analyze_vibe_spectrum_fast(img_array, description),
                'emotional_intensity': self._calculate_emotional_intensity_fast(img_array),
                'brand_personality_mapping': self._map_to_brand_personality_fast(img_array, description),
                'vibe_transferability': self._assess_transferability_fast(img_array),
                'analysis_type': 'vibe_intensity_optimized_v1'
            }
            
            # Cache result
            self._cache[cache_key] = vibe_map
            
            return vibe_map
            
        except Exception as e:
            return {
                'error': str(e),
                'analyzed_at': datetime.now().isoformat()
            }
    
    def _analyze_vibe_spectrum_fast(self, img_array: np.ndarray, description: str) -> Dict:
        """Fast analysis of essential vibe dimensions"""
        
        # Calculate once, use multiple times
        brightness = np.mean(img_array) / 255
        gray = np.mean(img_array, axis=2)
        contrast = np.std(gray) / 128
        
        # Sample colors efficiently
        h, w = img_array.shape[:2]
        color_samples = []
        for _ in range(50):  # Small sample
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            pixel = img_array[y, x]
            r, g, b = pixel[0]/255, pixel[1]/255, pixel[2]/255
            _, s, v = colorsys.rgb_to_hsv(r, g, b)
            color_samples.append((s, v))
        
        avg_saturation = np.mean([s for s, v in color_samples])
        
        # Fast vibe calculations
        spectrum = {
            'energy': self._calculate_energy_fast(contrast, avg_saturation),
            'sophistication': self._calculate_sophistication_fast(brightness, avg_saturation),
            'warmth': self._calculate_warmth_fast(img_array, color_samples),
            'playfulness': self._calculate_playfulness_fast(avg_saturation, contrast),
            'authenticity': self._calculate_authenticity_fast(brightness, description),
            'innovation': self._calculate_innovation_fast(description, contrast)
        }
        
        # Create vibe signature
        strong_traits = [k for k, v in spectrum.items() 
                        if isinstance(v, dict) and v.get('intensity', 0) > 0.6]
        spectrum['vibe_signature'] = "_".join(strong_traits[:3]) if strong_traits else "balanced"
        
        return spectrum
    
    def _calculate_energy_fast(self, contrast: float, saturation: float) -> Dict:
        """Fast energy calculation"""
        energy_score = (contrast + saturation) / 2
        
        if energy_score > 0.6:
            level = 'high'
        elif energy_score > 0.3:
            level = 'medium'
        else:
            level = 'low'
        
        return {
            'level': level,
            'intensity': energy_score,
            'components': {'contrast': contrast, 'saturation': saturation}
        }
    
    def _calculate_sophistication_fast(self, brightness: float, saturation: float) -> Dict:
        """Fast sophistication calculation"""
        # Sophisticated = moderate brightness + low-medium saturation
        soph_score = 0.5
        
        if 0.4 < brightness < 0.8 and saturation < 0.5:
            soph_score = 0.8
        elif saturation < 0.3:
            soph_score = 0.9  # Very sophisticated
        elif saturation > 0.7:
            soph_score = 0.3  # Less sophisticated
        
        if soph_score > 0.7:
            level = 'luxury'
        elif soph_score > 0.5:
            level = 'refined'
        else:
            level = 'minimal'
        
        return {
            'level': level,
            'intensity': soph_score,
            'components': {'brightness_balance': abs(brightness - 0.6), 'saturation_restraint': 1 - saturation}
        }
    
    def _calculate_warmth_fast(self, img_array: np.ndarray, color_samples: List[Tuple]) -> Dict:
        """Fast warmth calculation"""
        # Count warm vs cool hues in samples
        warm_count = 0
        for _ in range(20):  # Small sample
            h, w = img_array.shape[:2]
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            pixel = img_array[y, x]
            r, g, b = pixel
            
            # Simple warm detection: more red/yellow than blue
            if r + g > b * 1.5:
                warm_count += 1
        
        warmth_ratio = warm_count / 20
        
        if warmth_ratio > 0.6:
            level = 'warm'
        elif warmth_ratio < 0.4:
            level = 'cool'
        else:
            level = 'neutral'
        
        return {
            'level': level,
            'intensity': warmth_ratio if warmth_ratio > 0.5 else 1 - warmth_ratio,
            'components': {'warm_color_ratio': warmth_ratio}
        }
    
    def _calculate_playfulness_fast(self, saturation: float, contrast: float) -> Dict:
        """Fast playfulness calculation"""
        # High saturation + high contrast = playful
        play_score = (saturation * 0.6 + contrast * 0.4)
        
        if play_score > 0.6:
            level = 'playful'
        elif play_score > 0.3:
            level = 'balanced'
        else:
            level = 'serious'
        
        return {
            'level': level,
            'intensity': play_score,
            'components': {'color_vibrancy': saturation, 'visual_contrast': contrast}
        }
    
    def _calculate_authenticity_fast(self, brightness: float, description: str) -> Dict:
        """Fast authenticity calculation"""
        # Avoid extreme brightness = more authentic
        extreme_penalty = abs(brightness - 0.5) * 2
        auth_score = 1 - extreme_penalty
        
        # Check description for authenticity keywords
        if description:
            desc_lower = description.lower()
            if any(word in desc_lower for word in ['raw', 'authentic', 'real', 'unfiltered']):
                auth_score += 0.3
            elif any(word in desc_lower for word in ['polished', 'perfect', 'refined']):
                auth_score -= 0.2
        
        auth_score = max(0, min(1, auth_score))
        
        if auth_score > 0.7:
            level = 'raw'
        elif auth_score > 0.4:
            level = 'balanced'
        else:
            level = 'polished'
        
        return {
            'level': level,
            'intensity': auth_score,
            'components': {'natural_balance': 1 - extreme_penalty}
        }
    
    def _calculate_innovation_fast(self, description: str, contrast: float) -> Dict:
        """Fast innovation calculation"""
        innov_score = 0.5  # Default
        
        if description:
            desc_lower = description.lower()
            if any(word in desc_lower for word in ['innovative', 'cutting-edge', 'modern', 'futuristic']):
                innov_score += 0.4
            elif any(word in desc_lower for word in ['traditional', 'classic', 'vintage']):
                innov_score -= 0.3
        
        # High contrast can indicate innovation
        if contrast > 0.6:
            innov_score += 0.2
        
        innov_score = max(0, min(1, innov_score))
        
        if innov_score > 0.7:
            level = 'cutting_edge'
        elif innov_score > 0.4:
            level = 'progressive'
        else:
            level = 'traditional'
        
        return {
            'level': level,
            'intensity': innov_score,
            'components': {'conceptual_signals': innov_score, 'visual_boldness': contrast}
        }
    
    def _calculate_emotional_intensity_fast(self, img_array: np.ndarray) -> Dict:
        """Fast emotional intensity calculation"""
        gray = np.mean(img_array, axis=2)
        contrast = np.std(gray) / 128
        
        # Sample saturation quickly
        h, w = img_array.shape[:2]
        saturations = []
        for _ in range(30):  # Small sample
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            pixel = img_array[y, x]
            r, g, b = pixel[0]/255, pixel[1]/255, pixel[2]/255
            _, s, _ = colorsys.rgb_to_hsv(r, g, b)
            saturations.append(s)
        
        avg_saturation = np.mean(saturations)
        total_intensity = (contrast + avg_saturation) / 2
        
        if total_intensity > 0.7:
            level = 'high'
        elif total_intensity > 0.4:
            level = 'medium'
        else:
            level = 'low'
        
        return {
            'total_intensity': total_intensity,
            'intensity_level': level,
            'components': {'visual_contrast': contrast, 'color_intensity': avg_saturation}
        }
    
    def _map_to_brand_personality_fast(self, img_array: np.ndarray, description: str) -> Dict:
        """Fast brand personality mapping"""
        brightness = np.mean(img_array) / 255
        gray = np.mean(img_array, axis=2)
        contrast = np.std(gray) / 128
        
        personality = {
            'sincerity': 0.5,
            'excitement': 0.5,
            'competence': 0.5,
            'sophistication': 0.5,
            'ruggedness': 0.5
        }
        
        # Quick personality mapping
        if brightness > 0.6:
            personality['sincerity'] += 0.3
        if contrast > 0.5:
            personality['excitement'] += 0.3
        if 0.4 < brightness < 0.7 and contrast < 0.5:
            personality['competence'] += 0.3
        if brightness > 0.5 and contrast < 0.4:
            personality['sophistication'] += 0.3
        if brightness < 0.4:
            personality['ruggedness'] += 0.3
        
        # Normalize
        for key in personality:
            personality[key] = min(1.0, personality[key])
        
        return personality
    
    def _assess_transferability_fast(self, img_array: np.ndarray) -> Dict:
        """Fast transferability assessment"""
        # Simple metrics for transferability
        brightness = np.mean(img_array) / 255
        gray = np.mean(img_array, axis=2)
        contrast = np.std(gray) / 128
        
        # Good transferability = balanced properties
        balance_score = 1 - abs(brightness - 0.5) - abs(contrast - 0.5)
        balance_score = max(0, balance_score)
        
        if balance_score > 0.7:
            level = 'high'
        elif balance_score > 0.4:
            level = 'medium'
        else:
            level = 'low'
        
        applications = []
        if balance_score > 0.6:
            applications.extend(['logo_design', 'brand_identity'])
        if contrast > 0.3:
            applications.append('marketing_materials')
        if brightness > 0.4:
            applications.append('web_design')
        
        return {
            'transferability_level': level,
            'total_transferability': balance_score,
            'brand_applications': applications
        }


def map_vibe_intensity_optimized(image_path: str, description: str = "") -> Dict:
    """
    Optimized vibe intensity mapping - fast and efficient
    """
    mapper = VibeMapperOptimized()
    return mapper.map_vibe_intensity(image_path, description)


if __name__ == "__main__":
    import sys
    import time
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        description = sys.argv[2] if len(sys.argv) > 2 else ""
        
        print(f"Mapping vibe intensity (optimized): {image_path}")
        
        start_time = time.time()
        result = map_vibe_intensity_optimized(image_path, description)
        elapsed = time.time() - start_time
        
        if result and 'error' not in result:
            print(f"\n=== OPTIMIZED VIBE MAPPING ({elapsed:.2f}s) ===")
            
            # Vibe Spectrum
            if 'vibe_spectrum' in result:
                spectrum = result['vibe_spectrum']
                print(f"\n🌈 Vibe Spectrum:")
                
                for dimension, analysis in spectrum.items():
                    if isinstance(analysis, dict) and 'level' in analysis:
                        print(f"  {dimension.title()}: {analysis['level']} (intensity: {analysis['intensity']:.2f})")
                
                if 'vibe_signature' in spectrum:
                    print(f"\n🎯 Vibe Signature: {spectrum['vibe_signature']}")
            
            # Emotional Intensity
            if 'emotional_intensity' in result:
                intensity = result['emotional_intensity']
                print(f"\n⚡ Emotional Intensity: {intensity['intensity_level']} ({intensity['total_intensity']:.2f})")
            
            # Brand Personality (top traits only)
            if 'brand_personality_mapping' in result:
                personality = result['brand_personality_mapping']
                top_traits = [(k, v) for k, v in personality.items() if v > 0.6]
                if top_traits:
                    print(f"\n👤 Top Brand Traits:")
                    for trait, score in sorted(top_traits, key=lambda x: x[1], reverse=True):
                        print(f"  {trait.title()}: {score:.2f}")
            
            # Transferability
            if 'vibe_transferability' in result:
                transfer = result['vibe_transferability']
                print(f"\n🔄 Transferability: {transfer['transferability_level']}")
            
            print(f"\n⚡ Processing Time: {elapsed:.2f}s")
        else:
            print(f"Vibe mapping failed: {result.get('error', 'Unknown error')}")
    else:
        print("Usage: python vibe_mapper_optimized.py <image_path> [description]")