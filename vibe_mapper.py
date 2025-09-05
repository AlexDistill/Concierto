#!/usr/bin/env python3
"""
Vibe Intensity Mapping System
Quantifies and maps emotional intensity of source materials to create
a "vibe spectrum" that captures the feeling, mood, and emotional resonance
of inspiration sources for brand generation
"""

import numpy as np
from PIL import Image, ImageEnhance
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import colorsys
import json
from datetime import datetime
from deep_source_analyzer import DeepSourceAnalyzer

class VibeMapper:
    """
    Maps and quantifies emotional intensity and vibe characteristics
    from source materials to create a comprehensive vibe profile
    """
    
    def __init__(self):
        self.deep_analyzer = DeepSourceAnalyzer()
        
        # Define vibe dimensions and their characteristics
        self.vibe_dimensions = {
            'energy': {
                'low': ['calm', 'peaceful', 'serene', 'relaxed', 'quiet'],
                'medium': ['balanced', 'moderate', 'steady', 'comfortable'],
                'high': ['dynamic', 'exciting', 'vibrant', 'intense', 'electric']
            },
            'sophistication': {
                'minimal': ['simple', 'clean', 'basic', 'straightforward'],
                'refined': ['polished', 'elegant', 'sophisticated', 'tasteful'],
                'luxury': ['premium', 'exclusive', 'luxurious', 'opulent', 'lavish']
            },
            'warmth': {
                'cool': ['cold', 'distant', 'clinical', 'detached', 'sterile'],
                'neutral': ['balanced', 'moderate', 'even', 'stable'],
                'warm': ['inviting', 'friendly', 'cozy', 'welcoming', 'intimate']
            },
            'playfulness': {
                'serious': ['formal', 'professional', 'stern', 'rigid', 'conservative'],
                'balanced': ['approachable', 'friendly', 'open', 'moderate'],
                'playful': ['fun', 'whimsical', 'creative', 'experimental', 'bold']
            },
            'authenticity': {
                'polished': ['perfect', 'flawless', 'ideal', 'pristine', 'refined'],
                'balanced': ['realistic', 'natural', 'genuine', 'honest'],
                'raw': ['unfiltered', 'gritty', 'authentic', 'rough', 'real']
            },
            'innovation': {
                'traditional': ['classic', 'timeless', 'conventional', 'established'],
                'progressive': ['modern', 'contemporary', 'current', 'updated'],
                'cutting_edge': ['innovative', 'revolutionary', 'futuristic', 'groundbreaking']
            }
        }
    
    def map_vibe_intensity(self, image_path: str, description: str = "") -> Dict:
        """
        Create comprehensive vibe intensity mapping from source material
        
        Returns vibe spectrum with intensity scores across multiple dimensions
        """
        try:
            # Get deep source analysis first
            deep_analysis = self.deep_analyzer.analyze_source_material(image_path, description)
            
            if 'error' in deep_analysis:
                return deep_analysis
            
            # Load image for vibe analysis
            img = Image.open(image_path).convert('RGB')
            img_array = np.array(img)
            
            # Create comprehensive vibe mapping
            vibe_map = {
                'analyzed_at': datetime.now().isoformat(),
                'source_path': str(image_path),
                'vibe_spectrum': self._analyze_vibe_spectrum(img, img_array, description),
                'emotional_intensity': self._calculate_emotional_intensity(img, img_array),
                'mood_indicators': self._detect_mood_indicators(img, img_array, deep_analysis),
                'vibe_keywords': self._extract_vibe_keywords(description),
                'vibe_coherence': self._assess_vibe_coherence(img, img_array, description),
                'brand_personality_mapping': self._map_to_brand_personality(img, img_array, description),
                'vibe_transferability': self._assess_transferability(img, img_array),
                'analysis_type': 'vibe_intensity_v1'
            }
            
            return vibe_map
            
        except Exception as e:
            print(f"Error in vibe intensity mapping: {e}")
            return {
                'error': str(e),
                'analyzed_at': datetime.now().isoformat()
            }
    
    def _analyze_vibe_spectrum(self, img: Image, img_array: np.ndarray, description: str) -> Dict:
        """Analyze the full vibe spectrum across multiple dimensions"""
        
        spectrum = {}
        
        # Energy dimension
        spectrum['energy'] = self._calculate_energy_vibe(img, img_array)
        
        # Sophistication dimension
        spectrum['sophistication'] = self._calculate_sophistication_vibe(img, img_array)
        
        # Warmth dimension
        spectrum['warmth'] = self._calculate_warmth_vibe(img, img_array)
        
        # Playfulness dimension
        spectrum['playfulness'] = self._calculate_playfulness_vibe(img, img_array)
        
        # Authenticity dimension
        spectrum['authenticity'] = self._calculate_authenticity_vibe(img, img_array)
        
        # Innovation dimension
        spectrum['innovation'] = self._calculate_innovation_vibe(img, img_array, description)
        
        # Calculate overall vibe signature
        spectrum['vibe_signature'] = self._create_vibe_signature(spectrum)
        
        return spectrum
    
    def _calculate_energy_vibe(self, img: Image, img_array: np.ndarray) -> Dict:
        """Calculate energy vibe intensity"""
        
        # Visual energy indicators
        gray = np.mean(img_array, axis=2)
        
        # Contrast energy (high contrast = high energy)
        contrast = np.std(gray) / 128
        
        # Color saturation energy
        saturations = []
        h, w = img_array.shape[:2]
        sample_size = min(1000, h * w)
        
        for _ in range(sample_size):
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            pixel = img_array[y, x]
            r, g, b = pixel[0]/255, pixel[1]/255, pixel[2]/255
            _, s, _ = colorsys.rgb_to_hsv(r, g, b)
            saturations.append(s)
        
        color_energy = np.mean(saturations)
        
        # Motion/dynamism indicators
        edges = self._simple_edge_detection(gray)
        motion_energy = self._detect_directional_energy(edges)
        
        # Composition energy (asymmetry, diagonal lines)
        comp_energy = self._calculate_compositional_energy(gray)
        
        # Combine energy factors
        total_energy = (contrast + color_energy + motion_energy + comp_energy) / 4
        
        # Map to energy levels
        if total_energy < 0.3:
            level = 'low'
            intensity = total_energy / 0.3
        elif total_energy < 0.7:
            level = 'medium'
            intensity = (total_energy - 0.3) / 0.4
        else:
            level = 'high'
            intensity = min(1.0, (total_energy - 0.7) / 0.3)
        
        return {
            'level': level,
            'intensity': float(intensity),
            'raw_score': float(total_energy),
            'components': {
                'contrast': float(contrast),
                'color_saturation': float(color_energy),
                'motion_indicators': float(motion_energy),
                'compositional_dynamism': float(comp_energy)
            },
            'descriptors': self.vibe_dimensions['energy'][level]
        }
    
    def _simple_edge_detection(self, gray: np.ndarray) -> np.ndarray:
        """Simple edge detection for analysis"""
        kernel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        kernel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        
        edges = np.zeros_like(gray)
        h, w = gray.shape
        
        for y in range(1, h-1):
            for x in range(1, w-1):
                region = gray[y-1:y+2, x-1:x+2]
                gx = np.sum(region * kernel_x)
                gy = np.sum(region * kernel_y)
                edges[y, x] = np.sqrt(gx**2 + gy**2)
        
        return edges
    
    def _detect_directional_energy(self, edges: np.ndarray) -> float:
        """Detect directional motion energy"""
        h, w = edges.shape
        
        # Check for diagonal patterns (high energy)
        diag_energy = 0
        for y in range(1, h-1):
            for x in range(1, w-1):
                # Sample diagonal gradients
                diag1 = abs(edges[y-1, x-1] - edges[y+1, x+1])
                diag2 = abs(edges[y-1, x+1] - edges[y+1, x-1])
                diag_energy += max(diag1, diag2)
        
        # Normalize
        if h * w > 0:
            return min(1.0, diag_energy / (h * w * 255))
        return 0.0
    
    def _calculate_compositional_energy(self, gray: np.ndarray) -> float:
        """Calculate energy from composition"""
        h, w = gray.shape
        
        # Check center vs edges (centered = low energy, off-center = high)
        center_region = gray[h//3:2*h//3, w//3:2*w//3]
        edge_regions = [
            gray[:h//3, :],  # top
            gray[2*h//3:, :],  # bottom
            gray[:, :w//3],  # left
            gray[:, 2*w//3:]   # right
        ]
        
        if center_region.size > 0:
            center_activity = np.std(center_region)
            edge_activity = np.mean([np.std(region) for region in edge_regions if region.size > 0])
            
            # Higher edge activity = more energy
            if center_activity > 0:
                energy_ratio = edge_activity / center_activity
                return min(1.0, energy_ratio / 2)  # Normalize
        
        return 0.5
    
    def _calculate_sophistication_vibe(self, img: Image, img_array: np.ndarray) -> Dict:
        """Calculate sophistication vibe intensity"""
        
        # Color sophistication indicators
        colors_analysis = self._analyze_color_sophistication(img_array)
        
        # Composition sophistication
        comp_sophistication = self._analyze_composition_sophistication(img, img_array)
        
        # Texture sophistication
        texture_sophistication = self._analyze_texture_sophistication(img_array)
        
        # Typography sophistication (if text detected)
        typo_sophistication = self._analyze_typography_sophistication(img_array)
        
        # Combine sophistication factors
        total_sophistication = np.mean([
            colors_analysis,
            comp_sophistication,
            texture_sophistication,
            typo_sophistication
        ])
        
        # Map to sophistication levels
        if total_sophistication < 0.4:
            level = 'minimal'
            intensity = total_sophistication / 0.4
        elif total_sophistication < 0.7:
            level = 'refined'
            intensity = (total_sophistication - 0.4) / 0.3
        else:
            level = 'luxury'
            intensity = min(1.0, (total_sophistication - 0.7) / 0.3)
        
        return {
            'level': level,
            'intensity': float(intensity),
            'raw_score': float(total_sophistication),
            'components': {
                'color_sophistication': float(colors_analysis),
                'composition_sophistication': float(comp_sophistication),
                'texture_sophistication': float(texture_sophistication),
                'typography_sophistication': float(typo_sophistication)
            },
            'descriptors': self.vibe_dimensions['sophistication'][level]
        }
    
    def _analyze_color_sophistication(self, img_array: np.ndarray) -> float:
        """Analyze color sophistication"""
        h, w = img_array.shape[:2]
        sample_size = min(1000, h * w)
        
        hues = []
        saturations = []
        values = []
        
        for _ in range(sample_size):
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            pixel = img_array[y, x]
            r, g, b = pixel[0]/255, pixel[1]/255, pixel[2]/255
            hue, sat, val = colorsys.rgb_to_hsv(r, g, b)
            hues.append(hue)
            saturations.append(sat)
            values.append(val)
        
        # Sophisticated colors: consistent saturation, harmonious hues, balanced values
        sat_consistency = 1 - np.var(saturations)  # Lower variance = more sophisticated
        hue_harmony = self._calculate_hue_harmony(hues)
        value_balance = 1 - abs(np.mean(values) - 0.5)  # Closer to middle = more balanced
        
        return np.mean([sat_consistency, hue_harmony, value_balance])
    
    def _calculate_hue_harmony(self, hues: List[float]) -> float:
        """Calculate hue harmony score"""
        if len(hues) < 2:
            return 0.5
        
        hue_pairs = []
        for i in range(len(hues)):
            for j in range(i+1, len(hues)):
                diff = min(abs(hues[i] - hues[j]), 1 - abs(hues[i] - hues[j]))
                hue_pairs.append(diff)
        
        # Harmonious relationships: similar, complementary, or triadic
        harmony_score = 0
        for diff in hue_pairs:
            if diff < 0.1 or abs(diff - 0.33) < 0.1 or abs(diff - 0.5) < 0.1:
                harmony_score += 1
        
        return min(1.0, harmony_score / len(hue_pairs))
    
    def _analyze_composition_sophistication(self, img: Image, img_array: np.ndarray) -> float:
        """Analyze composition sophistication"""
        width, height = img.size
        
        # Golden ratio alignment (sophisticated)
        golden_ratio = 1.618
        aspect_ratio = width / height
        golden_score = 1 / (1 + abs(aspect_ratio - golden_ratio))
        
        # Whitespace usage (sophisticated designs use whitespace well)
        whitespace_score = self._calculate_whitespace_sophistication(img_array)
        
        # Balance and symmetry
        balance_score = self._calculate_visual_balance_sophistication(img_array)
        
        return np.mean([golden_score, whitespace_score, balance_score])
    
    def _calculate_whitespace_sophistication(self, img_array: np.ndarray) -> float:
        """Calculate whitespace sophistication"""
        gray = np.mean(img_array, axis=2)
        
        # Consider bright areas as potential whitespace
        brightness_threshold = 200
        whitespace_mask = gray > brightness_threshold
        whitespace_percentage = np.sum(whitespace_mask) / gray.size
        
        # Sophisticated designs often have 20-40% whitespace
        if 0.2 <= whitespace_percentage <= 0.4:
            return 1.0
        elif whitespace_percentage < 0.2:
            return whitespace_percentage / 0.2
        else:
            return max(0, 1 - (whitespace_percentage - 0.4) / 0.4)
    
    def _calculate_visual_balance_sophistication(self, img_array: np.ndarray) -> float:
        """Calculate visual balance sophistication"""
        gray = np.mean(img_array, axis=2)
        h, w = gray.shape
        
        # Check quadrant balance
        mid_h, mid_w = h // 2, w // 2
        
        quadrants = [
            gray[:mid_h, :mid_w],      # top-left
            gray[:mid_h, mid_w:],      # top-right
            gray[mid_h:, :mid_w],      # bottom-left
            gray[mid_h:, mid_w:]       # bottom-right
        ]
        
        # Calculate visual weight of each quadrant
        weights = [np.mean(1 - (quad / 255)) for quad in quadrants]  # Darker = heavier
        
        # Perfect balance = all weights equal (sophisticated)
        weight_variance = np.var(weights)
        balance_score = 1 / (1 + weight_variance * 10)
        
        return balance_score
    
    def _analyze_texture_sophistication(self, img_array: np.ndarray) -> float:
        """Analyze texture sophistication"""
        gray = np.mean(img_array, axis=2)
        
        # Smooth textures = high sophistication
        # Calculate local standard deviation (roughness)
        h, w = gray.shape
        roughness_values = []
        
        window_size = min(h, w) // 20
        if window_size < 3:
            window_size = 3
        
        for y in range(0, h-window_size, window_size):
            for x in range(0, w-window_size, window_size):
                window = gray[y:y+window_size, x:x+window_size]
                roughness_values.append(np.std(window))
        
        if roughness_values:
            avg_roughness = np.mean(roughness_values)
            # Lower roughness = higher sophistication
            return 1 - min(1.0, avg_roughness / 64)
        
        return 0.5
    
    def _analyze_typography_sophistication(self, img_array: np.ndarray) -> float:
        """Analyze typography sophistication (simplified)"""
        # This is a placeholder - would need OCR for full analysis
        
        gray = np.mean(img_array, axis=2)
        edges = self._simple_edge_detection(gray)
        
        # Look for text-like patterns
        h, w = edges.shape
        text_likelihood = 0
        
        # Check for horizontal line patterns (text)
        for y in range(h):
            row = edges[y, :]
            if np.sum(row > np.mean(row)) > w * 0.1:  # Significant edges in row
                text_likelihood += 1
        
        text_score = text_likelihood / h if h > 0 else 0
        
        # Assume moderate sophistication if text detected
        return 0.6 if text_score > 0.1 else 0.5
    
    def _calculate_warmth_vibe(self, img: Image, img_array: np.ndarray) -> Dict:
        """Calculate warmth vibe intensity"""
        
        # Color temperature analysis
        color_warmth = self._analyze_color_temperature(img_array)
        
        # Lighting warmth
        lighting_warmth = self._analyze_lighting_warmth(img_array)
        
        # Composition warmth (centered, inviting vs. distant)
        comp_warmth = self._analyze_compositional_warmth(img_array)
        
        # Texture warmth (soft vs. hard surfaces)
        texture_warmth = self._analyze_texture_warmth(img_array)
        
        total_warmth = np.mean([color_warmth, lighting_warmth, comp_warmth, texture_warmth])
        
        # Map to warmth levels
        if total_warmth < 0.35:
            level = 'cool'
            intensity = total_warmth / 0.35
        elif total_warmth < 0.65:
            level = 'neutral'
            intensity = (total_warmth - 0.35) / 0.3
        else:
            level = 'warm'
            intensity = min(1.0, (total_warmth - 0.65) / 0.35)
        
        return {
            'level': level,
            'intensity': float(intensity),
            'raw_score': float(total_warmth),
            'components': {
                'color_temperature': float(color_warmth),
                'lighting_warmth': float(lighting_warmth),
                'compositional_warmth': float(comp_warmth),
                'texture_warmth': float(texture_warmth)
            },
            'descriptors': self.vibe_dimensions['warmth'][level]
        }
    
    def _analyze_color_temperature(self, img_array: np.ndarray) -> float:
        """Analyze color temperature warmth"""
        h, w = img_array.shape[:2]
        sample_size = min(1000, h * w)
        
        warm_count = 0
        for _ in range(sample_size):
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            pixel = img_array[y, x]
            r, g, b = pixel
            
            # Warm colors: reds, oranges, yellows
            if r > g and r > b:  # Red dominant
                warm_count += 1
            elif r > b and g > b:  # Yellow/orange
                warm_count += 1
        
        return warm_count / sample_size
    
    def _analyze_lighting_warmth(self, img_array: np.ndarray) -> float:
        """Analyze lighting warmth"""
        # Warm lighting tends to have more red/yellow channel activity
        r_channel = img_array[:, :, 0].astype(float)
        g_channel = img_array[:, :, 1].astype(float)
        b_channel = img_array[:, :, 2].astype(float)
        
        # Calculate relative warmth
        warm_intensity = (np.mean(r_channel) + np.mean(g_channel)) / 2
        cool_intensity = np.mean(b_channel)
        
        if warm_intensity + cool_intensity > 0:
            warmth_ratio = warm_intensity / (warm_intensity + cool_intensity)
        else:
            warmth_ratio = 0.5
        
        return warmth_ratio
    
    def _analyze_compositional_warmth(self, img_array: np.ndarray) -> float:
        """Analyze compositional warmth"""
        gray = np.mean(img_array, axis=2)
        h, w = gray.shape
        
        # Warm compositions often have subjects closer to center
        center_region = gray[h//3:2*h//3, w//3:2*w//3]
        edge_regions = [
            gray[:h//4, :], gray[3*h//4:, :],  # top/bottom
            gray[:, :w//4], gray[:, 3*w//4:]   # left/right
        ]
        
        if center_region.size > 0:
            center_activity = np.std(center_region)
            edge_activity = np.mean([np.std(region) for region in edge_regions if region.size > 0])
            
            # More activity in center = warmer
            if center_activity + edge_activity > 0:
                return center_activity / (center_activity + edge_activity)
        
        return 0.5
    
    def _analyze_texture_warmth(self, img_array: np.ndarray) -> float:
        """Analyze texture warmth"""
        gray = np.mean(img_array, axis=2)
        
        # Smooth textures feel warmer than rough ones
        edges = self._simple_edge_detection(gray)
        edge_density = np.mean(edges)
        
        # Lower edge density = smoother = warmer
        smoothness = 1 - min(1.0, edge_density / 100)
        return smoothness
    
    def _calculate_playfulness_vibe(self, img: Image, img_array: np.ndarray) -> Dict:
        """Calculate playfulness vibe intensity"""
        
        # Color playfulness (bright, saturated colors)
        color_play = self._analyze_color_playfulness(img_array)
        
        # Composition playfulness (asymmetry, unexpected elements)
        comp_play = self._analyze_compositional_playfulness(img_array)
        
        # Movement playfulness (dynamic, flowing elements)
        movement_play = self._analyze_movement_playfulness(img_array)
        
        # Contrast playfulness (bold contrasts, unexpected combinations)
        contrast_play = self._analyze_contrast_playfulness(img_array)
        
        total_playfulness = np.mean([color_play, comp_play, movement_play, contrast_play])
        
        # Map to playfulness levels
        if total_playfulness < 0.35:
            level = 'serious'
            intensity = total_playfulness / 0.35
        elif total_playfulness < 0.65:
            level = 'balanced'
            intensity = (total_playfulness - 0.35) / 0.3
        else:
            level = 'playful'
            intensity = min(1.0, (total_playfulness - 0.65) / 0.35)
        
        return {
            'level': level,
            'intensity': float(intensity),
            'raw_score': float(total_playfulness),
            'components': {
                'color_playfulness': float(color_play),
                'compositional_playfulness': float(comp_play),
                'movement_playfulness': float(movement_play),
                'contrast_playfulness': float(contrast_play)
            },
            'descriptors': self.vibe_dimensions['playfulness'][level]
        }
    
    def _analyze_color_playfulness(self, img_array: np.ndarray) -> float:
        """Analyze color playfulness"""
        h, w = img_array.shape[:2]
        sample_size = min(1000, h * w)
        
        saturations = []
        brightnesses = []
        
        for _ in range(sample_size):
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            pixel = img_array[y, x]
            r, g, b = pixel[0]/255, pixel[1]/255, pixel[2]/255
            _, s, v = colorsys.rgb_to_hsv(r, g, b)
            saturations.append(s)
            brightnesses.append(v)
        
        # High saturation + high brightness = playful
        avg_saturation = np.mean(saturations)
        avg_brightness = np.mean(brightnesses)
        
        return (avg_saturation + avg_brightness) / 2
    
    def _analyze_compositional_playfulness(self, img_array: np.ndarray) -> float:
        """Analyze compositional playfulness"""
        gray = np.mean(img_array, axis=2)
        h, w = gray.shape
        
        # Asymmetry = more playful
        mid_h, mid_w = h // 2, w // 2
        left_half = gray[:, :mid_w]
        right_half = gray[:, mid_w:]
        top_half = gray[:mid_h, :]
        bottom_half = gray[mid_h:, :]
        
        # Calculate asymmetry
        lr_asymmetry = abs(np.mean(left_half) - np.mean(right_half)) / 255
        tb_asymmetry = abs(np.mean(top_half) - np.mean(bottom_half)) / 255
        
        return (lr_asymmetry + tb_asymmetry) / 2
    
    def _analyze_movement_playfulness(self, img_array: np.ndarray) -> float:
        """Analyze movement playfulness"""
        gray = np.mean(img_array, axis=2)
        edges = self._simple_edge_detection(gray)
        
        # Curved, flowing edges = more playful than straight lines
        # This is simplified - would need more sophisticated curve detection
        edge_variance = np.var(edges)
        edge_density = np.mean(edges)
        
        # High variance in edge directions = more dynamic/playful
        if edge_density > 0:
            return min(1.0, edge_variance / (edge_density * 100))
        return 0.5
    
    def _analyze_contrast_playfulness(self, img_array: np.ndarray) -> float:
        """Analyze contrast playfulness"""
        gray = np.mean(img_array, axis=2)
        
        # High contrast can be playful
        contrast = np.std(gray) / 128
        
        # But extreme contrast might be more dramatic than playful
        if contrast > 0.8:
            return 1 - (contrast - 0.8) * 2  # Reduce for extreme contrast
        else:
            return contrast / 0.8
    
    def _calculate_authenticity_vibe(self, img: Image, img_array: np.ndarray) -> Dict:
        """Calculate authenticity vibe intensity"""
        
        # Image processing authenticity (natural vs. heavily processed)
        processing_authenticity = self._analyze_processing_authenticity(img_array)
        
        # Composition authenticity (natural vs. staged)
        comp_authenticity = self._analyze_compositional_authenticity(img_array)
        
        # Lighting authenticity (natural vs. artificial)
        lighting_authenticity = self._analyze_lighting_authenticity(img_array)
        
        # Texture authenticity (natural textures vs. synthetic)
        texture_authenticity = self._analyze_texture_authenticity(img_array)
        
        total_authenticity = np.mean([
            processing_authenticity, comp_authenticity, 
            lighting_authenticity, texture_authenticity
        ])
        
        # Map to authenticity levels (inverted - raw is high authenticity)
        if total_authenticity > 0.65:
            level = 'raw'
            intensity = min(1.0, (total_authenticity - 0.65) / 0.35)
        elif total_authenticity > 0.35:
            level = 'balanced'
            intensity = (total_authenticity - 0.35) / 0.3
        else:
            level = 'polished'
            intensity = 1 - (total_authenticity / 0.35)
        
        return {
            'level': level,
            'intensity': float(intensity),
            'raw_score': float(total_authenticity),
            'components': {
                'processing_authenticity': float(processing_authenticity),
                'compositional_authenticity': float(comp_authenticity),
                'lighting_authenticity': float(lighting_authenticity),
                'texture_authenticity': float(texture_authenticity)
            },
            'descriptors': self.vibe_dimensions['authenticity'][level]
        }
    
    def _analyze_processing_authenticity(self, img_array: np.ndarray) -> float:
        """Analyze image processing authenticity"""
        # Look for signs of heavy processing: over-saturation, unnatural colors
        
        h, w = img_array.shape[:2]
        sample_size = min(1000, h * w)
        
        unnatural_count = 0
        for _ in range(sample_size):
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            pixel = img_array[y, x]
            r, g, b = pixel[0]/255, pixel[1]/255, pixel[2]/255
            _, s, v = colorsys.rgb_to_hsv(r, g, b)
            
            # Very high saturation or very extreme values might indicate processing
            if s > 0.9 or v > 0.95 or v < 0.05:
                unnatural_count += 1
        
        # More natural colors = higher authenticity
        return 1 - (unnatural_count / sample_size)
    
    def _analyze_compositional_authenticity(self, img_array: np.ndarray) -> float:
        """Analyze compositional authenticity"""
        gray = np.mean(img_array, axis=2)
        
        # Perfect center composition might be less authentic
        h, w = gray.shape
        center_region = gray[2*h//5:3*h//5, 2*w//5:3*w//5]
        
        if center_region.size > 0:
            center_activity = np.mean(center_region)
            total_activity = np.mean(gray)
            
            if total_activity > 0:
                center_dominance = center_activity / total_activity
                # Moderate center dominance = more authentic
                if 0.8 < center_dominance < 1.2:
                    return 1.0
                else:
                    return 1 - abs(center_dominance - 1.0) / 2
        
        return 0.5
    
    def _analyze_lighting_authenticity(self, img_array: np.ndarray) -> float:
        """Analyze lighting authenticity"""
        # Natural lighting has more variation than artificial
        gray = np.mean(img_array, axis=2)
        
        # Calculate lighting variation across the image
        lighting_variance = np.var(gray) / (255**2)
        
        # Moderate variance suggests natural lighting
        if 0.01 < lighting_variance < 0.1:
            return 1.0
        elif lighting_variance <= 0.01:
            return lighting_variance / 0.01  # Too uniform = artificial
        else:
            return max(0, 1 - (lighting_variance - 0.1) / 0.1)  # Too chaotic
    
    def _analyze_texture_authenticity(self, img_array: np.ndarray) -> float:
        """Analyze texture authenticity"""
        gray = np.mean(img_array, axis=2)
        
        # Natural textures have irregular, organic patterns
        # Calculate local pattern regularity
        h, w = gray.shape
        irregularity_score = 0
        
        # Sample small regions and check for pattern regularity
        for _ in range(min(100, h * w // 100)):
            y = np.random.randint(0, max(1, h-10))
            x = np.random.randint(0, max(1, w-10))
            
            region = gray[y:y+10, x:x+10]
            if region.size >= 100:  # Ensure we have enough pixels
                # Check for repeating patterns (less authentic)
                pattern_regularity = self._detect_pattern_regularity(region)
                irregularity_score += 1 - pattern_regularity
        
        return irregularity_score / 100 if irregularity_score > 0 else 0.5
    
    def _detect_pattern_regularity(self, region: np.ndarray) -> float:
        """Detect pattern regularity in a small region"""
        if region.size < 4:
            return 0.5
        
        # Simple autocorrelation-like measure
        region_flat = region.flatten()
        
        # Check similarity with shifted versions
        similarities = []
        for shift in range(1, min(len(region_flat) // 2, 10)):
            if shift < len(region_flat):
                original = region_flat[:-shift]
                shifted = region_flat[shift:]
                
                if len(original) > 0 and len(shifted) > 0:
                    corr = np.corrcoef(original, shifted)[0, 1]
                    if not np.isnan(corr):
                        similarities.append(abs(corr))
        
        return np.mean(similarities) if similarities else 0.5
    
    def _calculate_innovation_vibe(self, img: Image, img_array: np.ndarray, description: str) -> Dict:
        """Calculate innovation vibe intensity"""
        
        # Visual innovation (unusual compositions, techniques)
        visual_innovation = self._analyze_visual_innovation(img, img_array)
        
        # Color innovation (unexpected color combinations)
        color_innovation = self._analyze_color_innovation(img_array)
        
        # Conceptual innovation (from description)
        conceptual_innovation = self._analyze_conceptual_innovation(description)
        
        # Technical innovation (processing, effects)
        technical_innovation = self._analyze_technical_innovation(img_array)
        
        total_innovation = np.mean([
            visual_innovation, color_innovation, 
            conceptual_innovation, technical_innovation
        ])
        
        # Map to innovation levels
        if total_innovation < 0.35:
            level = 'traditional'
            intensity = total_innovation / 0.35
        elif total_innovation < 0.65:
            level = 'progressive'
            intensity = (total_innovation - 0.35) / 0.3
        else:
            level = 'cutting_edge'
            intensity = min(1.0, (total_innovation - 0.65) / 0.35)
        
        return {
            'level': level,
            'intensity': float(intensity),
            'raw_score': float(total_innovation),
            'components': {
                'visual_innovation': float(visual_innovation),
                'color_innovation': float(color_innovation),
                'conceptual_innovation': float(conceptual_innovation),
                'technical_innovation': float(technical_innovation)
            },
            'descriptors': self.vibe_dimensions['innovation'][level]
        }
    
    def _analyze_visual_innovation(self, img: Image, img_array: np.ndarray) -> float:
        """Analyze visual innovation"""
        width, height = img.size
        
        # Unusual aspect ratios can be innovative
        aspect_ratio = width / height
        unusual_ratio_score = 0
        if aspect_ratio < 0.5 or aspect_ratio > 2.5:
            unusual_ratio_score = 0.3
        
        # Composition innovation (breaking conventional rules)
        gray = np.mean(img_array, axis=2)
        
        # Check for rule-breaking compositions
        edges = self._simple_edge_detection(gray)
        edge_distribution = self._analyze_edge_distribution(edges)
        
        # Innovative compositions might have unusual edge distributions
        innovation_score = unusual_ratio_score + edge_distribution
        
        return min(1.0, innovation_score)
    
    def _analyze_edge_distribution(self, edges: np.ndarray) -> float:
        """Analyze edge distribution for innovation"""
        h, w = edges.shape
        
        # Divide into regions and check edge distribution
        regions = []
        for i in range(3):
            for j in range(3):
                region = edges[i*h//3:(i+1)*h//3, j*w//3:(j+1)*w//3]
                if region.size > 0:
                    regions.append(np.sum(region))
        
        if not regions:
            return 0.0
        
        # Calculate variance in edge distribution
        variance = np.var(regions)
        mean_edges = np.mean(regions)
        
        # High variance = unconventional distribution = innovative
        if mean_edges > 0:
            return min(1.0, variance / (mean_edges**2))
        return 0.0
    
    def _analyze_color_innovation(self, img_array: np.ndarray) -> float:
        """Analyze color innovation"""
        h, w = img_array.shape[:2]
        sample_size = min(1000, h * w)
        
        colors = []
        for _ in range(sample_size):
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            pixel = img_array[y, x]
            r, g, b = pixel[0]/255, pixel[1]/255, pixel[2]/255
            hue, sat, val = colorsys.rgb_to_hsv(r, g, b)
            colors.append((hue, sat, val))
        
        # Look for unusual color combinations
        innovation_score = 0
        
        # Very high saturation can be innovative
        high_sat_count = len([c for c in colors if c[1] > 0.8])
        innovation_score += min(0.5, high_sat_count / len(colors))
        
        # Unusual hue combinations
        hues = [c[0] for c in colors]
        hue_spread = max(hues) - min(hues) if hues else 0
        if hue_spread > 0.8:  # Very wide hue range
            innovation_score += 0.3
        
        # Extreme values (very dark or very bright)
        values = [c[2] for c in colors]
        extreme_values = len([v for v in values if v < 0.1 or v > 0.9])
        innovation_score += min(0.2, extreme_values / len(values))
        
        return min(1.0, innovation_score)
    
    def _analyze_conceptual_innovation(self, description: str) -> float:
        """Analyze conceptual innovation from description"""
        if not description:
            return 0.5
        
        # Look for innovation-related keywords
        innovation_keywords = [
            'innovative', 'cutting-edge', 'revolutionary', 'breakthrough',
            'futuristic', 'experimental', 'avant-garde', 'pioneering',
            'disruptive', 'unconventional', 'radical', 'groundbreaking'
        ]
        
        traditional_keywords = [
            'traditional', 'classic', 'vintage', 'timeless', 'conventional',
            'established', 'standard', 'orthodox', 'conservative'
        ]
        
        desc_lower = description.lower()
        
        innovation_count = sum(1 for keyword in innovation_keywords if keyword in desc_lower)
        traditional_count = sum(1 for keyword in traditional_keywords if keyword in desc_lower)
        
        # Score based on keyword presence
        if innovation_count > traditional_count:
            return min(1.0, 0.5 + (innovation_count - traditional_count) * 0.2)
        elif traditional_count > innovation_count:
            return max(0.0, 0.5 - (traditional_count - innovation_count) * 0.2)
        else:
            return 0.5
    
    def _analyze_technical_innovation(self, img_array: np.ndarray) -> float:
        """Analyze technical innovation"""
        # Look for signs of advanced image processing or effects
        
        # High dynamic range indicators
        pixel_range = np.max(img_array) - np.min(img_array)
        hdr_score = min(1.0, pixel_range / 255)
        
        # Color channel relationships (unusual processing)
        r_channel = img_array[:, :, 0].flatten()
        g_channel = img_array[:, :, 1].flatten()
        b_channel = img_array[:, :, 2].flatten()
        
        # Check for unusual channel correlations
        rg_corr = np.corrcoef(r_channel, g_channel)[0, 1]
        rb_corr = np.corrcoef(r_channel, b_channel)[0, 1]
        gb_corr = np.corrcoef(g_channel, b_channel)[0, 1]
        
        # Very low correlations might indicate special processing
        unusual_processing = 0
        for corr in [rg_corr, rb_corr, gb_corr]:
            if not np.isnan(corr) and abs(corr) < 0.3:
                unusual_processing += 0.2
        
        return min(1.0, (hdr_score * 0.5) + unusual_processing)
    
    def _create_vibe_signature(self, spectrum: Dict) -> str:
        """Create a unique vibe signature from the spectrum"""
        
        # Extract dominant characteristics
        dominant_traits = []
        
        for dimension, analysis in spectrum.items():
            if dimension == 'vibe_signature':
                continue
                
            if isinstance(analysis, dict) and 'level' in analysis and 'intensity' in analysis:
                if analysis['intensity'] > 0.6:  # Strong intensity
                    dominant_traits.append(f"{analysis['level']}_{dimension}")
        
        # Create signature
        if dominant_traits:
            return "_".join(sorted(dominant_traits)[:3])  # Top 3 traits
        else:
            return "balanced_neutral"
    
    def _calculate_emotional_intensity(self, img: Image, img_array: np.ndarray) -> Dict:
        """Calculate overall emotional intensity"""
        
        # Combine various intensity indicators
        visual_intensity = self._calculate_visual_intensity(img_array)
        color_intensity = self._calculate_color_intensity(img_array)
        composition_intensity = self._calculate_composition_intensity(img_array)
        
        total_intensity = np.mean([visual_intensity, color_intensity, composition_intensity])
        
        return {
            'total_intensity': float(total_intensity),
            'visual_intensity': float(visual_intensity),
            'color_intensity': float(color_intensity),
            'composition_intensity': float(composition_intensity),
            'intensity_level': self._classify_intensity_level(total_intensity)
        }
    
    def _calculate_visual_intensity(self, img_array: np.ndarray) -> float:
        """Calculate visual intensity"""
        gray = np.mean(img_array, axis=2)
        
        # High contrast = high intensity
        contrast = np.std(gray) / 128
        
        # Edge density = visual complexity/intensity
        edges = self._simple_edge_detection(gray)
        edge_density = np.mean(edges) / 255
        
        return (contrast + edge_density) / 2
    
    def _calculate_color_intensity(self, img_array: np.ndarray) -> float:
        """Calculate color intensity"""
        h, w = img_array.shape[:2]
        sample_size = min(1000, h * w)
        
        saturations = []
        for _ in range(sample_size):
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            pixel = img_array[y, x]
            r, g, b = pixel[0]/255, pixel[1]/255, pixel[2]/255
            _, s, _ = colorsys.rgb_to_hsv(r, g, b)
            saturations.append(s)
        
        return np.mean(saturations)
    
    def _calculate_composition_intensity(self, img_array: np.ndarray) -> float:
        """Calculate composition intensity"""
        gray = np.mean(img_array, axis=2)
        h, w = gray.shape
        
        # Asymmetry creates intensity
        mid_h, mid_w = h // 2, w // 2
        
        # Calculate quadrant imbalance
        quadrants = [
            gray[:mid_h, :mid_w],     # top-left
            gray[:mid_h, mid_w:],     # top-right
            gray[mid_h:, :mid_w],     # bottom-left
            gray[mid_h:, mid_w:]      # bottom-right
        ]
        
        means = [np.mean(quad) for quad in quadrants]
        imbalance = np.std(means) / 128
        
        return min(1.0, imbalance)
    
    def _classify_intensity_level(self, intensity: float) -> str:
        """Classify intensity level"""
        if intensity > 0.7:
            return 'high'
        elif intensity > 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _detect_mood_indicators(self, img: Image, img_array: np.ndarray, deep_analysis: Dict) -> Dict:
        """Detect specific mood indicators"""
        
        mood_indicators = {
            'dominant_mood': 'neutral',
            'mood_confidence': 0.5,
            'mood_elements': {}
        }
        
        # Extract relevant elements from deep analysis
        if 'brand_dna' in deep_analysis:
            brand_dna = deep_analysis['brand_dna']
            
            if 'energy_profile' in brand_dna:
                energy = brand_dna['energy_profile']
                mood_indicators['mood_elements']['energy'] = energy.get('energy_level', 'medium')
            
            if 'luxury_indicators' in brand_dna:
                luxury = brand_dna['luxury_indicators']
                if luxury.get('luxury_score', 0) > 0.6:
                    mood_indicators['mood_elements']['luxury'] = 'high'
        
        # Add color mood analysis
        gray = np.mean(img_array, axis=2)
        brightness = np.mean(gray) / 255
        
        if brightness > 0.7:
            mood_indicators['mood_elements']['brightness'] = 'bright'
        elif brightness < 0.3:
            mood_indicators['mood_elements']['darkness'] = 'dark'
        
        # Determine dominant mood
        mood_elements = mood_indicators['mood_elements']
        
        if 'luxury' in mood_elements:
            mood_indicators['dominant_mood'] = 'sophisticated'
            mood_indicators['mood_confidence'] = 0.8
        elif 'bright' in mood_elements:
            mood_indicators['dominant_mood'] = 'optimistic'
            mood_indicators['mood_confidence'] = 0.7
        elif 'dark' in mood_elements:
            mood_indicators['dominant_mood'] = 'dramatic'
            mood_indicators['mood_confidence'] = 0.7
        
        return mood_indicators
    
    def _extract_vibe_keywords(self, description: str) -> List[str]:
        """Extract vibe-related keywords from description"""
        if not description:
            return []
        
        vibe_keywords = {
            'energy': ['energetic', 'dynamic', 'vibrant', 'lively', 'intense', 'calm', 'peaceful', 'serene'],
            'mood': ['happy', 'sad', 'dramatic', 'playful', 'serious', 'mysterious', 'romantic', 'edgy'],
            'style': ['minimal', 'maximalist', 'elegant', 'rustic', 'modern', 'vintage', 'industrial', 'organic'],
            'feeling': ['warm', 'cool', 'cozy', 'stark', 'inviting', 'distant', 'intimate', 'grand']
        }
        
        found_keywords = []
        desc_lower = description.lower()
        
        for category, keywords in vibe_keywords.items():
            for keyword in keywords:
                if keyword in desc_lower:
                    found_keywords.append(f"{category}:{keyword}")
        
        return found_keywords[:10]  # Limit to top 10
    
    def _assess_vibe_coherence(self, img: Image, img_array: np.ndarray, description: str) -> Dict:
        """Assess how coherent the vibe is across different elements"""
        
        # Analyze coherence between visual elements and description
        visual_coherence = self._calculate_visual_coherence(img_array)
        desc_coherence = self._calculate_description_coherence(img_array, description)
        
        total_coherence = (visual_coherence + desc_coherence) / 2
        
        return {
            'total_coherence': float(total_coherence),
            'visual_coherence': float(visual_coherence),
            'description_coherence': float(desc_coherence),
            'coherence_level': 'high' if total_coherence > 0.7 else 'medium' if total_coherence > 0.4 else 'low'
        }
    
    def _calculate_visual_coherence(self, img_array: np.ndarray) -> float:
        """Calculate visual coherence within the image"""
        # Check if color palette is coherent
        h, w = img_array.shape[:2]
        sample_size = min(500, h * w)
        
        hues = []
        saturations = []
        values = []
        
        for _ in range(sample_size):
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            pixel = img_array[y, x]
            r, g, b = pixel[0]/255, pixel[1]/255, pixel[2]/255
            hue, sat, val = colorsys.rgb_to_hsv(r, g, b)
            hues.append(hue)
            saturations.append(sat)
            values.append(val)
        
        # Coherent palettes have consistent characteristics
        hue_consistency = 1 - min(1.0, np.std(hues) * 2)
        sat_consistency = 1 - min(1.0, np.std(saturations))
        val_consistency = 1 - min(1.0, np.std(values))
        
        return (hue_consistency + sat_consistency + val_consistency) / 3
    
    def _calculate_description_coherence(self, img_array: np.ndarray, description: str) -> float:
        """Calculate coherence between image and description"""
        if not description:
            return 0.5
        
        # This is simplified - would need more sophisticated NLP
        # For now, check basic consistency
        
        desc_lower = description.lower()
        
        # Analyze image characteristics
        gray = np.mean(img_array, axis=2)
        brightness = np.mean(gray) / 255
        contrast = np.std(gray) / 128
        
        coherence_score = 0.5  # Start with neutral
        
        # Check brightness consistency
        if 'bright' in desc_lower or 'light' in desc_lower:
            if brightness > 0.6:
                coherence_score += 0.2
        elif 'dark' in desc_lower or 'moody' in desc_lower:
            if brightness < 0.4:
                coherence_score += 0.2
        
        # Check energy consistency
        if 'dynamic' in desc_lower or 'energetic' in desc_lower:
            if contrast > 0.5:
                coherence_score += 0.2
        elif 'calm' in desc_lower or 'peaceful' in desc_lower:
            if contrast < 0.4:
                coherence_score += 0.2
        
        return min(1.0, coherence_score)
    
    def _map_to_brand_personality(self, img: Image, img_array: np.ndarray, description: str) -> Dict:
        """Map vibe characteristics to brand personality dimensions"""
        
        # Analyze image for brand personality indicators
        brand_personality = {
            'sincerity': 0.5,
            'excitement': 0.5,
            'competence': 0.5,
            'sophistication': 0.5,
            'ruggedness': 0.5
        }
        
        # Get visual characteristics
        gray = np.mean(img_array, axis=2)
        brightness = np.mean(gray) / 255
        contrast = np.std(gray) / 128
        
        # Calculate color characteristics
        h, w = img_array.shape[:2]
        sample_size = min(500, h * w)
        
        warm_colors = 0
        saturations = []
        
        for _ in range(sample_size):
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            pixel = img_array[y, x]
            r, g, b = pixel[0]/255, pixel[1]/255, pixel[2]/255
            hue, sat, val = colorsys.rgb_to_hsv(r, g, b)
            saturations.append(sat)
            
            # Warm colors (red, orange, yellow)
            if (0 <= hue <= 0.17) or (0.92 <= hue <= 1.0):
                warm_colors += 1
        
        warm_ratio = warm_colors / sample_size
        avg_saturation = np.mean(saturations)
        
        # Map visual characteristics to personality
        
        # Sincerity (honest, wholesome, cheerful)
        if brightness > 0.6 and warm_ratio > 0.4:
            brand_personality['sincerity'] = 0.8
        elif brightness < 0.4 or avg_saturation > 0.8:
            brand_personality['sincerity'] = 0.3
        
        # Excitement (daring, spirited, imaginative)
        if avg_saturation > 0.6 and contrast > 0.5:
            brand_personality['excitement'] = 0.8
        elif avg_saturation < 0.3 and contrast < 0.3:
            brand_personality['excitement'] = 0.2
        
        # Competence (reliable, intelligent, successful)
        if 0.4 < brightness < 0.7 and 0.3 < contrast < 0.6:
            brand_personality['competence'] = 0.8
        elif brightness > 0.8 or contrast > 0.8:
            brand_personality['competence'] = 0.4
        
        # Sophistication (upper class, charming)
        if avg_saturation < 0.5 and contrast < 0.5 and brightness > 0.5:
            brand_personality['sophistication'] = 0.8
        elif avg_saturation > 0.7:
            brand_personality['sophistication'] = 0.3
        
        # Ruggedness (outdoorsy, tough)
        if brightness < 0.5 and contrast > 0.4:
            brand_personality['ruggedness'] = 0.7
        elif brightness > 0.7 and avg_saturation < 0.4:
            brand_personality['ruggedness'] = 0.2
        
        # Adjust based on description if available
        if description:
            desc_lower = description.lower()
            
            if any(word in desc_lower for word in ['natural', 'honest', 'wholesome']):
                brand_personality['sincerity'] = min(1.0, brand_personality['sincerity'] + 0.2)
            
            if any(word in desc_lower for word in ['bold', 'exciting', 'dynamic']):
                brand_personality['excitement'] = min(1.0, brand_personality['excitement'] + 0.2)
            
            if any(word in desc_lower for word in ['professional', 'reliable', 'quality']):
                brand_personality['competence'] = min(1.0, brand_personality['competence'] + 0.2)
            
            if any(word in desc_lower for word in ['luxury', 'elegant', 'refined']):
                brand_personality['sophistication'] = min(1.0, brand_personality['sophistication'] + 0.2)
            
            if any(word in desc_lower for word in ['rugged', 'tough', 'outdoor']):
                brand_personality['ruggedness'] = min(1.0, brand_personality['ruggedness'] + 0.2)
        
        return {k: float(v) for k, v in brand_personality.items()}
    
    def _assess_transferability(self, img: Image, img_array: np.ndarray) -> Dict:
        """Assess how transferable the vibe is to brand applications"""
        
        # Analyze elements that transfer well to branding
        
        # Color transferability (distinct, memorable colors)
        color_transfer = self._assess_color_transferability(img_array)
        
        # Composition transferability (clear principles)
        comp_transfer = self._assess_composition_transferability(img, img_array)
        
        # Style transferability (coherent aesthetic)
        style_transfer = self._assess_style_transferability(img_array)
        
        total_transferability = (color_transfer + comp_transfer + style_transfer) / 3
        
        return {
            'total_transferability': float(total_transferability),
            'color_transferability': float(color_transfer),
            'composition_transferability': float(comp_transfer),
            'style_transferability': float(style_transfer),
            'transferability_level': 'high' if total_transferability > 0.7 else 'medium' if total_transferability > 0.4 else 'low',
            'brand_applications': self._suggest_brand_applications(total_transferability, color_transfer, comp_transfer)
        }
    
    def _assess_color_transferability(self, img_array: np.ndarray) -> float:
        """Assess color transferability"""
        # Get color analysis from semantic analyzer
        colors_analysis = self.deep_analyzer.semantic_analyzer._extract_colors(img_array)
        
        if 'most_common' not in colors_analysis:
            return 0.5
        
        colors = colors_analysis['most_common']
        
        if not colors:
            return 0.5
        
        # Transferable colors: distinct, memorable, not too many
        transferability = 0.5
        
        # Good number of colors (2-5 is ideal for branding)
        if 2 <= len(colors) <= 5:
            transferability += 0.2
        
        # Colors should be distinct
        if len(colors) >= 2:
            color_distances = []
            for i in range(len(colors)):
                for j in range(i+1, len(colors)):
                    # Calculate color distance in HSV space
                    h1, s1, v1 = colors[i]['hue']/360, colors[i]['saturation'], colors[i]['brightness']
                    h2, s2, v2 = colors[j]['hue']/360, colors[j]['saturation'], colors[j]['brightness']
                    
                    distance = np.sqrt((h1-h2)**2 + (s1-s2)**2 + (v1-v2)**2)
                    color_distances.append(distance)
            
            if color_distances and np.mean(color_distances) > 0.3:
                transferability += 0.2
        
        # Avoid extreme values (too bright, too dark, too saturated)
        extreme_count = 0
        for color in colors[:5]:
            if color['brightness'] > 0.95 or color['brightness'] < 0.05:
                extreme_count += 1
            if color['saturation'] > 0.95:
                extreme_count += 1
        
        if extreme_count == 0:
            transferability += 0.1
        
        return min(1.0, transferability)
    
    def _assess_composition_transferability(self, img: Image, img_array: np.ndarray) -> float:
        """Assess composition transferability"""
        width, height = img.size
        
        transferability = 0.5
        
        # Standard aspect ratios transfer better
        aspect_ratio = width / height
        if 0.5 <= aspect_ratio <= 2.0:
            transferability += 0.2
        
        # Balanced compositions transfer better
        gray = np.mean(img_array, axis=2)
        h, w = gray.shape
        
        # Check visual balance
        mid_h, mid_w = h // 2, w // 2
        quadrants = [
            gray[:mid_h, :mid_w],     # top-left
            gray[:mid_h, mid_w:],     # top-right
            gray[mid_h:, :mid_w],     # bottom-left
            gray[mid_h:, mid_w:]      # bottom-right
        ]
        
        weights = [np.mean(1 - (quad / 255)) for quad in quadrants]
        weight_balance = 1 - min(1.0, np.var(weights))
        
        if weight_balance > 0.7:
            transferability += 0.2
        
        # Clear focal points transfer better
        focal_strength = self._calculate_focal_strength(gray)
        if 0.3 < focal_strength < 0.8:
            transferability += 0.1
        
        return min(1.0, transferability)
    
    def _calculate_focal_strength(self, gray: np.ndarray) -> float:
        """Calculate focal point strength"""
        edges = self._simple_edge_detection(gray)
        h, w = edges.shape
        
        # Find the region with highest edge density
        max_density = 0
        for y in range(0, h, h//8):
            for x in range(0, w, w//8):
                region = edges[y:min(y+h//8, h), x:min(x+w//8, w)]
                if region.size > 0:
                    density = np.mean(region)
                    max_density = max(max_density, density)
        
        # Normalize and return
        return min(1.0, max_density / 100)
    
    def _assess_style_transferability(self, img_array: np.ndarray) -> float:
        """Assess style transferability"""
        
        # Consistent styles transfer better
        transferability = 0.5
        
        # Texture consistency
        gray = np.mean(img_array, axis=2)
        texture_variance = self._calculate_texture_variance(gray)
        
        if texture_variance < 0.5:  # Consistent texture
            transferability += 0.2
        
        # Color harmony
        h, w = img_array.shape[:2]
        sample_size = min(500, h * w)
        
        hues = []
        for _ in range(sample_size):
            y, x = np.random.randint(0, h), np.random.randint(0, w)
            pixel = img_array[y, x]
            r, g, b = pixel[0]/255, pixel[1]/255, pixel[2]/255
            hue, _, _ = colorsys.rgb_to_hsv(r, g, b)
            hues.append(hue)
        
        if hues:
            hue_consistency = 1 - min(1.0, np.std(hues))
            if hue_consistency > 0.7:
                transferability += 0.2
        
        # Avoid chaos (too much visual noise)
        edges = self._simple_edge_detection(gray)
        noise_level = np.std(edges) / 100
        
        if noise_level < 0.5:
            transferability += 0.1
        
        return min(1.0, transferability)
    
    def _calculate_texture_variance(self, gray: np.ndarray) -> float:
        """Calculate texture variance"""
        h, w = gray.shape
        
        # Sample texture in different regions
        texture_scores = []
        
        for i in range(4):
            for j in range(4):
                y_start, y_end = i * h // 4, (i + 1) * h // 4
                x_start, x_end = j * w // 4, (j + 1) * w // 4
                
                region = gray[y_start:y_end, x_start:x_end]
                if region.size > 10:
                    texture_score = np.std(region)
                    texture_scores.append(texture_score)
        
        if texture_scores:
            return np.var(texture_scores) / (np.mean(texture_scores) + 1)
        return 0.5
    
    def _suggest_brand_applications(self, total_transfer: float, color_transfer: float, comp_transfer: float) -> List[str]:
        """Suggest suitable brand applications"""
        applications = []
        
        if total_transfer > 0.7:
            applications.extend(['logo_design', 'brand_identity', 'marketing_materials'])
        
        if color_transfer > 0.7:
            applications.extend(['color_palette', 'packaging_design'])
        
        if comp_transfer > 0.7:
            applications.extend(['layout_systems', 'web_design'])
        
        if total_transfer > 0.5:
            applications.extend(['mood_boards', 'style_guides'])
        
        return list(set(applications))  # Remove duplicates


def map_vibe_intensity(image_path: str, description: str = "") -> Dict:
    """
    Simple integration function for vibe intensity mapping
    
    Returns comprehensive vibe spectrum and intensity mapping
    """
    mapper = VibeMapper()
    return mapper.map_vibe_intensity(image_path, description)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        description = sys.argv[2] if len(sys.argv) > 2 else ""
        
        print(f"Mapping vibe intensity: {image_path}")
        result = map_vibe_intensity(image_path, description)
        
        if result and 'error' not in result:
            print("\n=== VIBE INTENSITY MAPPING ===")
            
            # Vibe Spectrum
            if 'vibe_spectrum' in result:
                spectrum = result['vibe_spectrum']
                print("\n🌈 Vibe Spectrum:")
                
                for dimension, analysis in spectrum.items():
                    if isinstance(analysis, dict) and 'level' in analysis:
                        print(f"  {dimension.title()}: {analysis['level']} (intensity: {analysis['intensity']:.2f})")
                
                if 'vibe_signature' in spectrum:
                    print(f"\n🎯 Vibe Signature: {spectrum['vibe_signature']}")
            
            # Emotional Intensity
            if 'emotional_intensity' in result:
                intensity = result['emotional_intensity']
                print(f"\n⚡ Emotional Intensity: {intensity['intensity_level']} ({intensity['total_intensity']:.2f})")
            
            # Brand Personality
            if 'brand_personality_mapping' in result:
                personality = result['brand_personality_mapping']
                print(f"\n👤 Brand Personality Mapping:")
                for trait, score in personality.items():
                    if score > 0.6:
                        print(f"  {trait.title()}: {score:.2f} ✨")
            
            # Transferability
            if 'vibe_transferability' in result:
                transfer = result['vibe_transferability']
                print(f"\n🔄 Vibe Transferability: {transfer['transferability_level']}")
                if 'brand_applications' in transfer:
                    print(f"  Recommended Applications: {', '.join(transfer['brand_applications'])}")
            
        else:
            print(f"Vibe mapping failed: {result.get('error', 'Unknown error')}")
    else:
        print("Usage: python vibe_mapper.py <image_path> [description]")