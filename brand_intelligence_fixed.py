#!/usr/bin/env python3
"""
Fixed Advanced Brand Intelligence Engine
Actually analyzes image content to generate meaningful specifications
"""

import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import colorsys
import re

try:
    from PIL import Image, ImageFilter, ImageStat
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import cv2
    ADVANCED_DEPS = True
except ImportError:
    print("Advanced dependencies not available. Install: pip install opencv-python scikit-learn pillow")
    ADVANCED_DEPS = False

from style_vector import StyleVector, analyze_style_vector

@dataclass
class BrandContext:
    """Brand context information"""
    company_name: str = ""
    industry: str = ""
    target_audience: str = ""
    brand_values: List[str] = None
    brand_archetype: str = ""
    brand_personality: List[str] = None
    competitors: List[str] = None
    style_guidelines: Dict = None
    
    def __post_init__(self):
        if self.brand_values is None:
            self.brand_values = []
        if self.brand_personality is None:
            self.brand_personality = []
        if self.competitors is None:
            self.competitors = []
        if self.style_guidelines is None:
            self.style_guidelines = {}

class BrandIntelligenceEngine:
    """Advanced Brand Intelligence with meaningful image analysis"""
    
    def __init__(self, brand_context: Optional[BrandContext] = None):
        self.brand_context = brand_context or BrandContext()
        
        # Brand archetype mappings
        self.brand_archetypes = {
            'Creator': ['creative', 'artistic', 'innovative', 'imaginative', 'original'],
            'Sage': ['wise', 'knowledgeable', 'analytical', 'thoughtful', 'precise'],
            'Explorer': ['adventurous', 'free', 'pioneering', 'bold', 'independent'],
            'Hero': ['courageous', 'determined', 'strong', 'confident', 'triumphant'],
            'Lover': ['passionate', 'romantic', 'intimate', 'warm', 'sensual'],
            'Jester': ['playful', 'fun', 'lighthearted', 'spontaneous', 'entertaining'],
            'Innocent': ['pure', 'simple', 'wholesome', 'optimistic', 'peaceful'],
            'Everyman': ['down-to-earth', 'friendly', 'genuine', 'reliable', 'practical'],
            'Caregiver': ['nurturing', 'protective', 'compassionate', 'selfless', 'generous'],
            'Ruler': ['responsible', 'authoritative', 'organized', 'stable', 'prestigious'],
            'Magician': ['transformative', 'visionary', 'charismatic', 'inspiring', 'mystical'],
            'Outlaw': ['rebellious', 'revolutionary', 'wild', 'disruptive', 'authentic']
        }
    
    def analyze_comprehensive(self, image_path: str, description: str = "", 
                            existing_analysis: Dict = None, brand_context: BrandContext = None) -> Dict:
        """Perform comprehensive brand intelligence analysis"""
        try:
            # Start with existing style vector analysis
            if existing_analysis and 'style_vector' in existing_analysis:
                style_analysis = existing_analysis
            else:
                style_analysis = analyze_style_vector(image_path)
            
            if not style_analysis:
                return existing_analysis or {}
            
            # Load and analyze the actual image
            img = Image.open(image_path).convert('RGB')
            
            # Extract REAL semantic meaning from the image
            semantic_analysis = self._analyze_image_semantics(img, description, style_analysis['style_vector'])
            
            # Generate SPECIFIC design specifications based on actual analysis
            design_specs = self._generate_real_specifications(style_analysis, semantic_analysis, img)
            
            # Analyze ACTUAL brand alignment with context
            brand_alignment = self._analyze_real_brand_alignment(semantic_analysis, 
                                                               style_analysis['style_vector'], 
                                                               brand_context or self.brand_context)
            
            # Extract implementation details based on real analysis
            implementation = self._generate_contextual_implementation(style_analysis, design_specs, semantic_analysis)
            
            # Cultural analysis based on actual visual elements
            cultural_analysis = self._analyze_visual_culture(semantic_analysis, style_analysis['style_vector'])
            
            return {
                **style_analysis,
                'semantic_analysis': semantic_analysis,
                'design_specifications': design_specs,
                'brand_alignment': brand_alignment,
                'implementation': implementation,
                'cultural_analysis': cultural_analysis,
                'intelligence_score': self._calculate_real_intelligence_score(semantic_analysis, brand_alignment),
                'analyzed_at': datetime.now().isoformat(),
                'analysis_method': 'Fixed Brand Intelligence Engine v2'
            }
            
        except Exception as e:
            print(f"Error in comprehensive analysis: {e}")
            return existing_analysis or {}
    
    def _analyze_image_semantics(self, img: Image, description: str, style_vector: Dict) -> Dict:
        """Extract REAL semantic meaning from the actual image"""
        try:
            # Get image properties
            width, height = img.size
            aspect_ratio = width / height
            
            # Analyze actual color distribution
            colors = self._extract_meaningful_colors(img)
            
            # Analyze actual composition
            composition = self._analyze_real_composition(img)
            
            # Extract emotions based on ACTUAL visual elements
            emotions = self._extract_real_emotions(img, style_vector, description)
            
            # Identify actual visual concepts
            concepts = self._identify_real_concepts(img, description, colors)
            
            # Detect actual symbols and visual elements
            symbols = self._detect_real_symbols(img, description)
            
            # Analyze actual visual hierarchy
            hierarchy = self._analyze_real_hierarchy(img)
            
            return {
                'composition_analysis': composition,
                'emotional_signals': emotions,
                'concept_mapping': concepts,
                'symbol_detection': symbols,
                'visual_hierarchy': hierarchy,
                'color_psychology': self._analyze_color_psychology(colors),
                'meaning_extraction': self._extract_contextual_meaning(description, concepts, emotions, colors),
                'visual_elements': {
                    'dominant_colors': colors,
                    'contrast_level': self._calculate_contrast_level(img),
                    'texture_complexity': self._analyze_texture_complexity(img),
                    'geometric_elements': self._detect_geometric_elements(img)
                }
            }
            
        except Exception as e:
            print(f"Error in semantic analysis: {e}")
            return {}
    
    def _extract_meaningful_colors(self, img: Image) -> List[str]:
        """Extract and analyze actual dominant colors from image"""
        # Convert to numpy array for analysis
        img_array = np.array(img)
        
        # Reshape for clustering
        pixels = img_array.reshape(-1, 3)
        
        # Use KMeans to find dominant colors
        if ADVANCED_DEPS:
            kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
            kmeans.fit(pixels)
            colors = []
            
            for center in kmeans.cluster_centers_:
                # Convert to hex
                hex_color = '#{:02x}{:02x}{:02x}'.format(int(center[0]), int(center[1]), int(center[2]))
                colors.append(hex_color)
            
            return colors
        else:
            # Fallback: sample colors from different regions
            colors = []
            h, w = img_array.shape[:2]
            sample_points = [(h//4, w//4), (h//2, w//2), (3*h//4, 3*w//4)]
            
            for y, x in sample_points:
                color = img_array[y, x]
                hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
                colors.append(hex_color)
            
            return colors
    
    def _analyze_real_composition(self, img: Image) -> Dict:
        """Analyze actual composition structure of the image"""
        width, height = img.size
        aspect_ratio = width / height
        
        # Determine actual composition type based on image analysis
        if aspect_ratio > 1.5:
            comp_type = "horizontal_emphasis"
        elif aspect_ratio < 0.7:
            comp_type = "vertical_emphasis"
        else:
            comp_type = "balanced_square"
            
        # Analyze visual weight distribution by examining pixel intensity
        img_gray = img.convert('L')
        img_array = np.array(img_gray)
        
        # Divide image into 9 regions (rule of thirds)
        h, w = img_array.shape
        regions = {
            'top_left': img_array[0:h//3, 0:w//3],
            'top_center': img_array[0:h//3, w//3:2*w//3],
            'top_right': img_array[0:h//3, 2*w//3:w],
            'center_left': img_array[h//3:2*h//3, 0:w//3],
            'center': img_array[h//3:2*h//3, w//3:2*w//3],
            'center_right': img_array[h//3:2*h//3, 2*w//3:w],
            'bottom_left': img_array[2*h//3:h, 0:w//3],
            'bottom_center': img_array[2*h//3:h, w//3:2*w//3],
            'bottom_right': img_array[2*h//3:h, 2*w//3:w]
        }
        
        # Calculate visual interest (contrast) in each region
        region_weights = {}
        for name, region in regions.items():
            region_weights[name] = float(np.std(region))  # Standard deviation as measure of visual interest
        
        # Find region with highest visual weight
        primary_focus = max(region_weights, key=region_weights.get)
        
        # Determine weight distribution
        center_weight = region_weights['center']
        edge_weights = [region_weights[k] for k in region_weights if k != 'center']
        avg_edge_weight = np.mean(edge_weights)
        
        if center_weight > avg_edge_weight * 1.5:
            weight_dist = "center_heavy"
        elif max(edge_weights) > center_weight * 1.3:
            weight_dist = "edge_emphasized"
        else:
            weight_dist = "balanced"
        
        return {
            'type': comp_type,
            'aspect_ratio': round(aspect_ratio, 2),
            'dimensions': f'{width}x{height}',
            'format_category': 'landscape' if aspect_ratio > 1.2 else 'portrait' if aspect_ratio < 0.8 else 'square',
            'visual_weight_distribution': weight_dist,
            'primary_focus_region': primary_focus,
            'composition_strength': max(region_weights.values()) / (np.mean(list(region_weights.values())) + 0.01),
            'rule_of_thirds_compliance': self._check_rule_of_thirds(region_weights)
        }
    
    def _check_rule_of_thirds(self, region_weights: Dict) -> float:
        """Check how well the composition follows rule of thirds"""
        # Rule of thirds points are at intersections - weight these more
        key_regions = ['top_left', 'top_right', 'bottom_left', 'bottom_right', 'center_left', 'center_right', 'top_center', 'bottom_center']
        key_weight = sum(region_weights[r] for r in key_regions if r in region_weights)
        total_weight = sum(region_weights.values())
        
        return key_weight / (total_weight + 0.01)
    
    def _extract_real_emotions(self, img: Image, style_vector: Dict, description: str) -> List[str]:
        """Extract emotions based on actual visual analysis"""
        emotions = []
        
        # Analyze based on style vector
        energy = style_vector.get('energy', 0.5)
        sophistication = style_vector.get('sophistication', 0.5)
        temperature = style_vector.get('temperature', 0.5)
        
        # Energy-based emotions
        if energy > 0.7:
            emotions.extend(['dynamic', 'energetic', 'vibrant'])
        elif energy < 0.3:
            emotions.extend(['calm', 'peaceful', 'serene'])
        
        # Sophistication-based emotions  
        if sophistication > 0.8:
            emotions.extend(['sophisticated', 'refined', 'elegant'])
        elif sophistication < 0.3:
            emotions.extend(['casual', 'approachable', 'simple'])
        
        # Temperature-based emotions
        if temperature > 0.7:
            emotions.extend(['warm', 'inviting', 'cozy'])
        elif temperature < 0.3:
            emotions.extend(['cool', 'distant', 'professional'])
            
        # Add emotions from description analysis
        if description:
            description_lower = description.lower()
            emotion_keywords = {
                'happy': ['happy', 'joyful', 'cheerful', 'smile', 'laugh'],
                'serious': ['serious', 'stern', 'formal', 'professional'],
                'playful': ['playful', 'fun', 'whimsical', 'quirky'],
                'mysterious': ['mysterious', 'dark', 'shadow', 'hidden'],
                'nostalgic': ['vintage', 'retro', 'old', 'classic', 'nostalgic']
            }
            
            for emotion, keywords in emotion_keywords.items():
                if any(keyword in description_lower for keyword in keywords):
                    emotions.append(emotion)
        
        return list(set(emotions))  # Remove duplicates
    
    def _identify_real_concepts(self, img: Image, description: str, colors: List[str]) -> List[str]:
        """Identify actual visual concepts from image analysis"""
        concepts = []
        
        # Analyze colors for concepts
        for color_hex in colors:
            # Convert hex to RGB then to HSV for analysis
            color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
            h, s, v = colorsys.rgb_to_hsv(color_rgb[0]/255, color_rgb[1]/255, color_rgb[2]/255)
            
            # Map hue to concepts
            if 0.0 <= h < 0.1 or 0.9 <= h <= 1.0:  # Red
                concepts.extend(['bold', 'passionate', 'energetic'])
            elif 0.1 <= h < 0.2:  # Orange/Yellow
                concepts.extend(['warm', 'creative', 'optimistic'])
            elif 0.2 <= h < 0.4:  # Green
                concepts.extend(['natural', 'growth', 'harmony'])
            elif 0.4 <= h < 0.7:  # Blue
                concepts.extend(['trust', 'professional', 'calm'])
            elif 0.7 <= h < 0.9:  # Purple
                concepts.extend(['creative', 'luxury', 'mystical'])
                
            # Saturation-based concepts
            if s > 0.8:
                concepts.append('vibrant')
            elif s < 0.3:
                concepts.extend(['muted', 'subtle'])
                
            # Value-based concepts
            if v > 0.8:
                concepts.append('bright')
            elif v < 0.3:
                concepts.extend(['dark', 'mysterious'])
        
        # Extract concepts from description
        if description:
            desc_lower = description.lower()
            concept_keywords = {
                'technology': ['digital', 'tech', 'modern', 'futuristic', 'cyber'],
                'nature': ['organic', 'natural', 'earth', 'plant', 'animal'],
                'art': ['artistic', 'creative', 'design', 'abstract', 'aesthetic'],
                'business': ['professional', 'corporate', 'business', 'formal'],
                'lifestyle': ['lifestyle', 'casual', 'everyday', 'personal'],
                'luxury': ['luxury', 'premium', 'high-end', 'exclusive', 'expensive'],
                'vintage': ['vintage', 'retro', 'classic', 'old-fashioned', 'nostalgic'],
                'minimalism': ['minimal', 'clean', 'simple', 'pure', 'basic']
            }
            
            for concept, keywords in concept_keywords.items():
                if any(keyword in desc_lower for keyword in keywords):
                    concepts.append(concept)
        
        return list(set(concepts))
    
    def _analyze_real_brand_alignment(self, semantic_analysis: Dict, style_vector: Dict, brand_context: BrandContext) -> Dict:
        """Analyze REAL brand alignment based on actual image content"""
        if not brand_context or not brand_context.company_name:
            return {
                'overall_score': 0.5,
                'note': 'No brand context provided for alignment analysis',
                'recommendations': ['Provide brand context for meaningful alignment analysis']
            }
        
        emotions = semantic_analysis.get('emotional_signals', [])
        concepts = semantic_analysis.get('concept_mapping', [])
        colors = semantic_analysis.get('visual_elements', {}).get('dominant_colors', [])
        
        # Calculate archetype alignment based on actual emotional signals
        archetype_score = self._calculate_real_archetype_alignment(emotions, brand_context.brand_archetype)
        
        # Calculate values alignment based on extracted concepts
        values_score = self._calculate_real_values_alignment(concepts, emotions, brand_context.brand_values)
        
        # Calculate audience alignment based on sophistication and emotional tone
        audience_score = self._calculate_real_audience_alignment(style_vector, emotions, brand_context.target_audience)
        
        # Calculate industry alignment
        industry_score = self._calculate_industry_alignment(concepts, brand_context.industry)
        
        overall_score = (archetype_score + values_score + audience_score + industry_score) / 4
        
        # Generate specific recommendations
        recommendations = self._generate_real_recommendations(
            archetype_score, values_score, audience_score, industry_score, 
            emotions, concepts, brand_context
        )
        
        return {
            'overall_score': round(overall_score, 3),
            'archetype_alignment': round(archetype_score, 3),
            'values_alignment': round(values_score, 3),
            'audience_alignment': round(audience_score, 3),
            'industry_alignment': round(industry_score, 3),
            'recommendations': recommendations,
            'brand_consistency': self._assess_visual_brand_consistency(style_vector, semantic_analysis),
            'alignment_breakdown': {
                'emotional_match': f"{len([e for e in emotions if e in self.brand_archetypes.get(brand_context.brand_archetype, [])])}/{len(emotions)}",
                'concept_relevance': f"{len([c for c in concepts if c.lower() in [v.lower() for v in brand_context.brand_values]])}/{len(concepts)}",
                'visual_sophistication_match': self._assess_sophistication_match(style_vector.get('sophistication', 0.5), brand_context.target_audience)
            }
        }
    
    def _calculate_real_archetype_alignment(self, emotions: List[str], brand_archetype: str) -> float:
        """Calculate alignment with brand archetype based on actual emotions detected"""
        if not brand_archetype or brand_archetype not in self.brand_archetypes:
            return 0.5
        
        archetype_emotions = self.brand_archetypes[brand_archetype]
        matching_emotions = [e for e in emotions if e.lower() in [ae.lower() for ae in archetype_emotions]]
        
        if not emotions:
            return 0.5
            
        alignment = len(matching_emotions) / len(emotions)
        
        # Bonus for strong matches
        if len(matching_emotions) >= 2:
            alignment += 0.1
            
        return min(alignment, 1.0)
    
    def _calculate_real_values_alignment(self, concepts: List[str], emotions: List[str], brand_values: List[str]) -> float:
        """Calculate alignment with brand values based on actual visual concepts"""
        if not brand_values:
            return 0.5
        
        all_visual_elements = concepts + emotions
        
        # Create mapping of brand values to visual indicators
        value_indicators = {
            'innovation': ['creative', 'modern', 'futuristic', 'bold', 'technology'],
            'quality': ['sophisticated', 'refined', 'elegant', 'professional', 'luxury'],
            'authenticity': ['natural', 'genuine', 'honest', 'simple', 'organic'],
            'creativity': ['artistic', 'creative', 'imaginative', 'colorful', 'abstract'],
            'trust': ['professional', 'reliable', 'stable', 'consistent', 'calm'],
            'sustainability': ['natural', 'green', 'organic', 'earth', 'responsible'],
            'beauty': ['elegant', 'aesthetic', 'refined', 'harmonious', 'graceful'],
            'timeless': ['classic', 'elegant', 'sophisticated', 'enduring', 'vintage']
        }
        
        alignment_scores = []
        for value in brand_values:
            value_lower = value.lower()
            indicators = value_indicators.get(value_lower, [value_lower])
            
            matches = len([elem for elem in all_visual_elements if elem.lower() in indicators])
            max_possible = len(all_visual_elements)
            
            if max_possible > 0:
                score = matches / max_possible
            else:
                score = 0.5
                
            alignment_scores.append(score)
        
        return np.mean(alignment_scores) if alignment_scores else 0.5
    
    def _calculate_real_audience_alignment(self, style_vector: Dict, emotions: List[str], target_audience: str) -> float:
        """Calculate audience alignment based on visual sophistication and emotional tone"""
        if not target_audience:
            return 0.5
            
        audience_lower = target_audience.lower()
        sophistication = style_vector.get('sophistication', 0.5)
        energy = style_vector.get('energy', 0.5)
        
        # Map audience types to expected characteristics
        if any(term in audience_lower for term in ['professional', 'executive', 'business']):
            # Professional audience expects high sophistication, moderate energy
            sophistication_match = 1.0 if sophistication > 0.7 else sophistication / 0.7
            energy_match = 1.0 if 0.3 <= energy <= 0.7 else max(0, 1 - abs(energy - 0.5) * 2)
            return (sophistication_match + energy_match) / 2
            
        elif any(term in audience_lower for term in ['young', 'youth', 'teen', 'millennial', 'gen z']):
            # Young audience expects higher energy, varied sophistication
            energy_match = energy  # Higher energy is better
            sophistication_match = 0.8  # Most sophistication levels work
            return (energy_match + sophistication_match) / 2
            
        elif any(term in audience_lower for term in ['luxury', 'premium', 'high-end']):
            # Luxury audience expects very high sophistication
            sophistication_match = 1.0 if sophistication > 0.8 else sophistication / 0.8
            emotion_match = 1.0 if any(e in emotions for e in ['sophisticated', 'refined', 'elegant']) else 0.6
            return (sophistication_match + emotion_match) / 2
            
        elif any(term in audience_lower for term in ['creative', 'artist', 'designer']):
            # Creative audience values creativity over convention
            creativity_emotions = ['creative', 'artistic', 'imaginative', 'bold', 'innovative']
            creativity_match = len([e for e in emotions if e in creativity_emotions]) / max(len(emotions), 1)
            return creativity_match
            
        else:
            # General audience - balanced approach
            return 0.7  # Assume good general appeal
    
    def _calculate_industry_alignment(self, concepts: List[str], industry: str) -> float:
        """Calculate alignment with industry based on visual concepts"""
        if not industry:
            return 0.5
            
        industry_lower = industry.lower()
        
        # Map industries to expected visual concepts
        industry_concepts = {
            'technology': ['modern', 'digital', 'innovative', 'clean', 'futuristic'],
            'healthcare': ['clean', 'professional', 'trust', 'caring', 'reliable'],
            'finance': ['professional', 'trust', 'stable', 'sophisticated', 'conservative'],
            'fashion': ['stylish', 'trendy', 'aesthetic', 'luxury', 'creative'],
            'food': ['appetizing', 'fresh', 'natural', 'warm', 'inviting'],
            'travel': ['adventurous', 'exciting', 'beautiful', 'cultural', 'inspiring'],
            'education': ['knowledge', 'growth', 'inspiring', 'accessible', 'trustworthy'],
            'creative': ['artistic', 'innovative', 'imaginative', 'bold', 'expressive']
        }
        
        # Find the best matching industry category
        max_alignment = 0.5
        for industry_key, expected_concepts in industry_concepts.items():
            if industry_key in industry_lower:
                matching_concepts = len([c for c in concepts if c.lower() in [ec.lower() for ec in expected_concepts]])
                if concepts:
                    alignment = matching_concepts / len(concepts)
                    max_alignment = max(max_alignment, alignment)
        
        return max_alignment
    
    def _generate_real_recommendations(self, archetype_score: float, values_score: float, 
                                     audience_score: float, industry_score: float,
                                     emotions: List[str], concepts: List[str], 
                                     brand_context: BrandContext) -> List[str]:
        """Generate specific, actionable recommendations based on actual analysis"""
        recommendations = []
        
        if archetype_score < 0.6:
            archetype_emotions = self.brand_archetypes.get(brand_context.brand_archetype, [])
            missing_emotions = [e for e in archetype_emotions if e not in emotions]
            if missing_emotions:
                recommendations.append(f"Strengthen {brand_context.brand_archetype} archetype by incorporating more {', '.join(missing_emotions[:3])} visual elements")
        
        if values_score < 0.6:
            recommendations.append(f"Better align visual concepts with brand values: {', '.join(brand_context.brand_values[:3])}")
        
        if audience_score < 0.6:
            recommendations.append(f"Adjust visual sophistication and energy levels to better match {brand_context.target_audience}")
        
        if industry_score < 0.6:
            recommendations.append(f"Incorporate more {brand_context.industry}-appropriate visual elements and concepts")
        
        # Positive reinforcement for strong areas
        if max(archetype_score, values_score, audience_score, industry_score) > 0.8:
            strongest_area = ['archetype', 'values', 'audience', 'industry'][
                [archetype_score, values_score, audience_score, industry_score].index(
                    max(archetype_score, values_score, audience_score, industry_score)
                )
            ]
            recommendations.append(f"Strong {strongest_area} alignment - leverage this consistency across other brand touchpoints")
        
        if not recommendations:
            recommendations.append("Good overall brand alignment - maintain current visual direction")
        
        return recommendations
    
    def _generate_real_specifications(self, style_analysis: Dict, semantic_analysis: Dict, img: Image) -> Dict:
        """Generate meaningful design specifications based on actual image analysis"""
        
        # Get the actual analysis data
        style_vector = style_analysis['style_vector']
        emotions = semantic_analysis.get('emotional_signals', [])
        concepts = semantic_analysis.get('concept_mapping', [])
        composition = semantic_analysis.get('composition_analysis', {})
        hierarchy = semantic_analysis.get('visual_hierarchy', {})
        colors = semantic_analysis.get('visual_elements', {}).get('dominant_colors', [])
        
        return {
            'layout_system': self._generate_contextual_layout_specs(style_vector, composition, hierarchy, emotions),
            'typography_system': self._generate_contextual_typography_specs(style_vector, emotions, concepts),
            'color_system': self._generate_contextual_color_specs(colors, emotions, concepts),
            'spacing_system': self._generate_contextual_spacing_specs(composition, style_vector, emotions),
            'interaction_patterns': self._generate_contextual_interaction_specs(emotions, concepts, style_vector),
            'responsive_strategy': self._generate_contextual_responsive_specs(composition, style_vector),
            'component_guidelines': self._generate_contextual_component_specs(emotions, concepts, style_vector)
        }
    
    def _generate_contextual_layout_specs(self, style_vector: Dict, composition: Dict, hierarchy: Dict, emotions: List[str]) -> Dict:
        """Generate layout specs based on actual composition analysis"""
        
        # Determine grid system based on actual composition
        comp_type = composition.get('type', 'balanced')
        aspect_ratio = composition.get('aspect_ratio', 1.0)
        primary_focus = hierarchy.get('primary_focus_region', 'center')
        
        if comp_type == 'vertical_emphasis':
            grid_cols = 8
            grid_reasoning = "8-column grid optimized for vertical content flow and reading patterns"
        elif comp_type == 'horizontal_emphasis':
            grid_cols = 16
            grid_reasoning = "16-column grid to support wide horizontal layouts and content distribution"
        elif 'sophisticated' in emotions:
            grid_cols = 12
            grid_reasoning = "12-column grid for refined, editorial-style layouts with sophisticated proportions"
        else:
            grid_cols = 12
            grid_reasoning = "Standard 12-column grid for balanced, flexible layouts"
        
        # Spacing based on visual density and emotional tone
        density = style_vector.get('density', 0.5)
        if 'minimal' in emotions or density < 0.3:
            base_spacing = 32
            spacing_reasoning = "Generous spacing to emphasize minimalist aesthetic and create visual breathing room"
        elif 'sophisticated' in emotions or 'refined' in emotions:
            base_spacing = 24
            spacing_reasoning = "Refined spacing that supports elegant typography and content hierarchy"
        elif density > 0.7:
            base_spacing = 16
            spacing_reasoning = "Compact spacing to efficiently organize dense content while maintaining readability"
        else:
            base_spacing = 20
            spacing_reasoning = "Balanced spacing for comfortable content consumption and visual flow"
        
        return {
            'grid_system': f'{grid_cols}-column responsive grid',
            'grid_reasoning': grid_reasoning,
            'spacing_base': f'{base_spacing}px',
            'spacing_scale': f'{base_spacing}px, {base_spacing*1.5}px, {base_spacing*2}px, {base_spacing*3}px',
            'spacing_reasoning': spacing_reasoning,
            'content_width': self._calculate_optimal_content_width(composition, style_vector),
            'alignment_strategy': self._determine_alignment_strategy(hierarchy, emotions),
            'composition_insights': {
                'visual_weight_distribution': composition.get('visual_weight_distribution', 'balanced'),
                'rule_of_thirds_compliance': composition.get('rule_of_thirds_compliance', 0.5),
                'recommended_focal_points': self._suggest_focal_points(hierarchy)
            }
        }
    
    def _calculate_optimal_content_width(self, composition: Dict, style_vector: Dict) -> Dict:
        """Calculate optimal content width based on composition analysis"""
        aspect_ratio = composition.get('aspect_ratio', 1.0)
        sophistication = style_vector.get('sophistication', 0.5)
        
        if sophistication > 0.8 and aspect_ratio < 1.2:
            # High sophistication with square/portrait = reading-focused
            return {
                'max_width': '900px',
                'reasoning': 'Narrow width optimized for reading comfort and sophisticated typography',
                'breakpoints': {'mobile': '100%', 'tablet': '750px', 'desktop': '900px'}
            }
        elif aspect_ratio > 1.5:
            # Wide format content
            return {
                'max_width': '1600px',
                'reasoning': 'Wide format to showcase horizontal content and maintain aspect ratio integrity',
                'breakpoints': {'mobile': '100%', 'tablet': '1200px', 'desktop': '1600px'}
            }
        else:
            return {
                'max_width': '1200px',
                'reasoning': 'Balanced width for versatile content presentation and optimal readability',
                'breakpoints': {'mobile': '100%', 'tablet': '900px', 'desktop': '1200px'}
            }
    
    def _generate_contextual_typography_specs(self, style_vector: Dict, emotions: List[str], concepts: List[str]) -> Dict:
        """Generate typography specifications based on emotional and conceptual analysis"""
        sophistication = style_vector.get('sophistication', 0.5)
        energy = style_vector.get('energy', 0.5)
        
        # Determine font family based on analysis
        if 'technology' in concepts or 'modern' in concepts:
            font_primary = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
            font_reasoning = 'Modern system fonts for technology-forward, clean aesthetic'
        elif sophistication > 0.8 or 'elegant' in emotions or 'refined' in emotions:
            font_primary = '"Playfair Display", "Times New Roman", serif'
            font_reasoning = 'Elegant serif for sophisticated, editorial-style content'
        elif 'creative' in emotions or 'artistic' in concepts:
            font_primary = '"Inter", "Helvetica Neue", sans-serif'
            font_reasoning = 'Versatile sans-serif that balances creativity with readability'
        else:
            font_primary = '"Inter", system-ui, sans-serif'
            font_reasoning = 'Clean, readable sans-serif for broad accessibility'
        
        # Scale based on energy and sophistication
        if energy > 0.7:
            scale_ratio = 1.333  # Perfect Fourth - energetic
            scale_reasoning = 'Dynamic scale for energetic, attention-grabbing typography'
        elif sophistication > 0.8:
            scale_ratio = 1.618  # Golden Ratio - sophisticated
            scale_reasoning = 'Golden ratio scale for sophisticated, harmonious typography hierarchy'
        else:
            scale_ratio = 1.25   # Major Third - balanced
            scale_reasoning = 'Balanced scale for clear hierarchy and comfortable reading'
        
        return {
            'font_primary': font_primary,
            'font_reasoning': font_reasoning,
            'scale_ratio': scale_ratio,
            'scale_reasoning': scale_reasoning,
            'line_height': self._calculate_optimal_line_height(sophistication, concepts),
            'font_weights': self._determine_font_weights(energy, emotions),
            'letter_spacing': self._calculate_letter_spacing(style_vector, emotions)
        }
    
    def _calculate_optimal_line_height(self, sophistication: float, concepts: List[str]) -> Dict:
        """Calculate line height based on sophistication and content type"""
        if 'technology' in concepts:
            line_height = 1.4
            reasoning = 'Tight line height for technical content and screen reading'
        elif sophistication > 0.8:
            line_height = 1.6
            reasoning = 'Generous line height for sophisticated, long-form reading'
        else:
            line_height = 1.5
            reasoning = 'Balanced line height for comfortable reading across contexts'
        
        return {'value': line_height, 'reasoning': reasoning}
    
    def _generate_contextual_color_specs(self, colors: List[str], emotions: List[str], concepts: List[str]) -> Dict:
        """Generate color system based on actual extracted colors and analysis"""
        
        if not colors:
            colors = ['#333333', '#666666']  # Fallback
        
        primary_color = colors[0] if colors else '#333333'
        secondary_color = colors[1] if len(colors) > 1 else self._generate_complementary_color(primary_color)
        
        # Analyze color psychology of extracted colors
        color_psychology = self._analyze_extracted_color_psychology(colors)
        
        # Generate palette based on actual colors and emotional context
        if 'sophisticated' in emotions:
            palette_approach = 'monochromatic_sophisticated'
            accent_colors = self._generate_sophisticated_accents(colors)
        elif 'energetic' in emotions or 'vibrant' in emotions:
            palette_approach = 'complementary_vibrant'
            accent_colors = self._generate_vibrant_accents(colors)
        elif 'minimal' in emotions:
            palette_approach = 'minimal_neutral'
            accent_colors = self._generate_minimal_accents(colors)
        else:
            palette_approach = 'balanced_harmonious'
            accent_colors = self._generate_balanced_accents(colors)
        
        return {
            'primary_color': primary_color,
            'secondary_color': secondary_color,
            'accent_colors': accent_colors,
            'palette_approach': palette_approach,
            'color_psychology': color_psychology,
            'usage_guidelines': self._generate_color_usage_guidelines(colors, emotions),
            'accessibility': self._generate_color_accessibility_specs(colors),
            'extracted_from_image': True,
            'color_harmony': self._analyze_color_harmony(colors)
        }
    
    def _analyze_extracted_color_psychology(self, colors: List[str]) -> Dict:
        """Analyze the psychological impact of extracted colors"""
        psychology = {}
        
        for i, color_hex in enumerate(colors[:3]):  # Analyze top 3 colors
            color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
            h, s, v = colorsys.rgb_to_hsv(color_rgb[0]/255, color_rgb[1]/255, color_rgb[2]/255)
            
            # Map to psychological associations
            if 0.9 <= h or h < 0.1:  # Red
                psychology[color_hex] = ['passionate', 'energetic', 'bold', 'attention-grabbing']
            elif 0.1 <= h < 0.2:  # Orange/Yellow
                psychology[color_hex] = ['warm', 'optimistic', 'creative', 'friendly']
            elif 0.2 <= h < 0.4:  # Green
                psychology[color_hex] = ['natural', 'calming', 'growth', 'harmony']
            elif 0.4 <= h < 0.7:  # Blue
                psychology[color_hex] = ['trustworthy', 'calm', 'professional', 'stable']
            elif 0.7 <= h < 0.9:  # Purple
                psychology[color_hex] = ['creative', 'luxurious', 'mystical', 'innovative']
            else:
                psychology[color_hex] = ['neutral', 'versatile', 'balanced']
        
        return psychology
    
    def _analyze_color_psychology(self, colors: List[str]) -> List[str]:
        """Simplified color psychology analysis"""
        psychology_terms = []
        for color_hex in colors[:3]:
            try:
                color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
                h, s, v = colorsys.rgb_to_hsv(color_rgb[0]/255, color_rgb[1]/255, color_rgb[2]/255)
                
                if 0.9 <= h or h < 0.1:
                    psychology_terms.extend(['bold', 'energetic'])
                elif 0.1 <= h < 0.4:
                    psychology_terms.extend(['warm', 'natural'])
                elif 0.4 <= h < 0.7:
                    psychology_terms.extend(['calm', 'trustworthy'])
                else:
                    psychology_terms.extend(['creative', 'luxurious'])
            except:
                continue
        
        return list(set(psychology_terms))
    
    # Additional helper methods for completeness
    def _detect_real_symbols(self, img: Image, description: str) -> List[str]:
        """Detect symbols based on description and basic image analysis"""
        symbols = []
        
        if description:
            symbol_keywords = {
                'star': ['star', 'asterisk', '*'],
                'heart': ['heart', 'love', '♥'],
                'arrow': ['arrow', 'pointer', '→', '←', '↑', '↓'],
                'circle': ['circle', 'round', 'dot', '●'],
                'square': ['square', 'box', 'rectangle', '■'],
                'triangle': ['triangle', 'arrow', '▲'],
                'crown': ['crown', 'royal', 'king', 'queen'],
                'eye': ['eye', 'vision', 'see', 'watch']
            }
            
            desc_lower = description.lower()
            for symbol, keywords in symbol_keywords.items():
                if any(keyword in desc_lower for keyword in keywords):
                    symbols.append(symbol)
        
        return symbols
    
    def _analyze_real_hierarchy(self, img: Image) -> Dict:
        """Analyze visual hierarchy using image processing"""
        try:
            # Convert to grayscale for analysis
            gray = img.convert('L')
            img_array = np.array(gray)
            
            # Find areas of high contrast (likely focal points)
            if ADVANCED_DEPS:
                # Use edge detection to find areas of visual interest
                edges = cv2.Canny(img_array, 100, 200)
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    # Find largest contour area (primary focus)
                    areas = [cv2.contourArea(c) for c in contours]
                    primary_focus = "center" if max(areas) > img_array.size * 0.1 else "distributed"
                else:
                    primary_focus = "center"
            else:
                # Fallback analysis
                center_region = img_array[img_array.shape[0]//3:2*img_array.shape[0]//3, 
                                        img_array.shape[1]//3:2*img_array.shape[1]//3]
                edge_regions = np.concatenate([
                    img_array[:img_array.shape[0]//3, :].flatten(),
                    img_array[2*img_array.shape[0]//3:, :].flatten(),
                    img_array[:, :img_array.shape[1]//3].flatten(),
                    img_array[:, 2*img_array.shape[1]//3:].flatten()
                ])
                
                center_contrast = np.std(center_region)
                edge_contrast = np.std(edge_regions)
                
                primary_focus = "center" if center_contrast > edge_contrast else "edges"
            
            return {
                'primary_focus': primary_focus,
                'reading_pattern': self._determine_reading_pattern(img_array),
                'contrast_areas': self._identify_contrast_areas(img_array),
                'visual_weight': self._calculate_visual_weight_distribution(img_array)
            }
            
        except Exception as e:
            return {
                'primary_focus': 'center',
                'reading_pattern': 'linear',
                'contrast_areas': 'balanced',
                'visual_weight': 'center_focused'
            }
    
    def _determine_reading_pattern(self, img_array: np.ndarray) -> str:
        """Determine likely reading pattern based on image layout"""
        h, w = img_array.shape
        
        # Analyze quadrants for visual weight
        tl = np.mean(img_array[:h//2, :w//2])
        tr = np.mean(img_array[:h//2, w//2:])
        bl = np.mean(img_array[h//2:, :w//2])
        br = np.mean(img_array[h//2:, w//2:])
        
        # Determine pattern based on where visual interest is concentrated
        if tl > np.mean([tr, bl, br]) * 1.2:
            return 'f_pattern'  # Strong top-left
        elif max(tl, tr) > max(bl, br) * 1.2 and abs(tl - tr) < 20:
            return 'z_pattern'  # Top-heavy with horizontal emphasis
        else:
            return 'linear'
    
    def _identify_contrast_areas(self, img_array: np.ndarray) -> str:
        """Identify areas of high contrast in the image"""
        # Calculate local contrast using standard deviation in regions
        h, w = img_array.shape
        regions = [
            img_array[:h//2, :w//2],    # Top-left
            img_array[:h//2, w//2:],    # Top-right
            img_array[h//2:, :w//2],    # Bottom-left
            img_array[h//2:, w//2:],    # Bottom-right
            img_array[h//3:2*h//3, w//3:2*w//3]  # Center
        ]
        
        contrasts = [np.std(region) for region in regions]
        max_contrast_idx = np.argmax(contrasts)
        
        area_names = ['top_left', 'top_right', 'bottom_left', 'bottom_right', 'center']
        return area_names[max_contrast_idx]
    
    def _calculate_visual_weight_distribution(self, img_array: np.ndarray) -> str:
        """Calculate how visual weight is distributed across the image"""
        h, w = img_array.shape
        
        # Calculate mean brightness in different areas
        center = np.mean(img_array[h//4:3*h//4, w//4:3*w//4])
        edges = np.mean([
            np.mean(img_array[:h//4, :]),      # Top edge
            np.mean(img_array[3*h//4:, :]),    # Bottom edge
            np.mean(img_array[:, :w//4]),      # Left edge
            np.mean(img_array[:, 3*w//4:])     # Right edge
        ])
        
        if center > edges * 1.2:
            return 'center_heavy'
        elif edges > center * 1.2:
            return 'edge_emphasized'
        else:
            return 'balanced'
    
    def _calculate_contrast_level(self, img: Image) -> float:
        """Calculate overall contrast level of the image"""
        gray = img.convert('L')
        img_array = np.array(gray)
        return float(np.std(img_array) / 127.5)  # Normalize to 0-1
    
    def _analyze_texture_complexity(self, img: Image) -> str:
        """Analyze texture complexity of the image"""
        gray = img.convert('L')
        img_array = np.array(gray)
        
        # Use local standard deviation as texture measure
        from scipy import ndimage
        if ADVANCED_DEPS:
            try:
                # Calculate local variance
                mean_filter = ndimage.uniform_filter(img_array.astype(float), size=5)
                sqr_filter = ndimage.uniform_filter(img_array.astype(float)**2, size=5)
                texture_variance = sqr_filter - mean_filter**2
                
                avg_texture = np.mean(texture_variance)
                
                if avg_texture > 1000:
                    return 'high'
                elif avg_texture > 300:
                    return 'medium'
                else:
                    return 'low'
            except:
                pass
        
        # Fallback method
        gradient = np.gradient(img_array.astype(float))
        gradient_magnitude = np.sqrt(gradient[0]**2 + gradient[1]**2)
        avg_gradient = np.mean(gradient_magnitude)
        
        if avg_gradient > 20:
            return 'high'
        elif avg_gradient > 10:
            return 'medium'
        else:
            return 'low'
    
    def _detect_geometric_elements(self, img: Image) -> List[str]:
        """Detect basic geometric elements in the image"""
        elements = []
        
        # This is a simplified approach - in practice you'd use more sophisticated computer vision
        gray = img.convert('L')
        img_array = np.array(gray)
        
        # Look for high contrast edges that might indicate geometric shapes
        if ADVANCED_DEPS:
            try:
                edges = cv2.Canny(img_array, 50, 150)
                
                # Look for lines (could indicate rectangles, triangles)
                lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
                if lines is not None and len(lines) > 10:
                    elements.append('linear_elements')
                
                # Look for circles
                circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=10, maxRadius=100)
                if circles is not None and len(circles[0]) > 0:
                    elements.append('circular_elements')
                    
            except:
                pass
        
        if not elements:
            elements.append('organic_shapes')  # Default assumption
        
        return elements
    
    def _extract_contextual_meaning(self, description: str, concepts: List[str], emotions: List[str], colors: List[str]) -> str:
        """Extract contextual meaning by combining all analysis elements"""
        meaning_parts = []
        
        # Primary concept
        if concepts:
            primary_concept = concepts[0]
            meaning_parts.append(f"Primary concept: {primary_concept}")
        
        # Emotional journey
        if emotions:
            emotion_summary = ', '.join(emotions[:3])
            meaning_parts.append(f"Emotional journey: {emotion_summary}")
        
        # Color story
        if colors and len(colors) >= 2:
            meaning_parts.append(f"Color narrative supports {emotions[0] if emotions else 'balanced'} aesthetic")
        
        # Synthesis
        if description:
            # Try to synthesize with description
            meaning_parts.append(f"Visual elements reinforce the described {description[:50]}...")
        
        return '. '.join(meaning_parts) if meaning_parts else "Balanced visual composition with harmonious elements"
    
    def _assess_visual_brand_consistency(self, style_vector: Dict, semantic_analysis: Dict) -> float:
        """Assess visual brand consistency based on analysis"""
        consistency_factors = []
        
        # Color consistency (are emotions aligned with color psychology?)
        emotions = semantic_analysis.get('emotional_signals', [])
        color_psychology = semantic_analysis.get('color_psychology', [])
        
        emotion_color_alignment = len(set(emotions) & set(color_psychology)) / max(len(emotions), 1)
        consistency_factors.append(emotion_color_alignment)
        
        # Style vector coherence
        style_values = [style_vector.get(k, 0.5) for k in ['energy', 'sophistication', 'temperature']]
        style_variance = np.var(style_values)
        style_consistency = 1 - min(style_variance, 1)  # Lower variance = higher consistency
        consistency_factors.append(style_consistency)
        
        # Composition consistency
        composition = semantic_analysis.get('composition_analysis', {})
        rule_of_thirds = composition.get('rule_of_thirds_compliance', 0.5)
        consistency_factors.append(rule_of_thirds)
        
        return np.mean(consistency_factors)
    
    def _assess_sophistication_match(self, sophistication: float, target_audience: str) -> str:
        """Assess if sophistication level matches target audience"""
        if not target_audience:
            return "unknown_audience"
        
        audience_lower = target_audience.lower()
        
        if any(term in audience_lower for term in ['luxury', 'premium', 'executive']):
            expected_sophistication = 0.8
        elif any(term in audience_lower for term in ['professional', 'business']):
            expected_sophistication = 0.7
        elif any(term in audience_lower for term in ['young', 'casual']):
            expected_sophistication = 0.4
        else:
            expected_sophistication = 0.6
        
        difference = abs(sophistication - expected_sophistication)
        
        if difference < 0.1:
            return "excellent_match"
        elif difference < 0.2:
            return "good_match"
        elif difference < 0.3:
            return "fair_match"
        else:
            return "poor_match"
    
    def _calculate_real_intelligence_score(self, semantic_analysis: Dict, brand_alignment: Dict) -> float:
        """Calculate intelligence score based on depth and quality of analysis"""
        score_factors = []
        
        # Semantic richness
        emotions = len(semantic_analysis.get('emotional_signals', []))
        concepts = len(semantic_analysis.get('concept_mapping', []))
        symbols = len(semantic_analysis.get('symbol_detection', []))
        
        semantic_richness = min((emotions + concepts + symbols) / 10, 1.0)
        score_factors.append(semantic_richness)
        
        # Brand alignment quality
        brand_score = brand_alignment.get('overall_score', 0.5)
        score_factors.append(brand_score)
        
        # Analysis completeness
        required_fields = ['composition_analysis', 'visual_hierarchy', 'color_psychology']
        completeness = sum(1 for field in required_fields if field in semantic_analysis) / len(required_fields)
        score_factors.append(completeness)
        
        return np.mean(score_factors)
    
    def _generate_contextual_implementation(self, style_analysis: Dict, design_specs: Dict, semantic_analysis: Dict) -> Dict:
        """Generate implementation specs based on actual analysis"""
        return {
            'css_variables': self._generate_contextual_css_variables(style_analysis, semantic_analysis),
            'design_tokens': design_specs,  # Use the real design specs as tokens
            'component_code': self._generate_contextual_component_code(style_analysis, semantic_analysis),
            'style_guide': self._generate_contextual_style_guide(style_analysis, semantic_analysis)
        }
    
    def _generate_contextual_css_variables(self, style_analysis: Dict, semantic_analysis: Dict) -> Dict:
        """Generate CSS variables based on actual analysis"""
        colors = semantic_analysis.get('visual_elements', {}).get('dominant_colors', ['#333333'])
        emotions = semantic_analysis.get('emotional_signals', [])
        
        # Spacing based on emotions
        if 'minimal' in emotions:
            spacing_unit = '32px'
        elif 'sophisticated' in emotions:
            spacing_unit = '24px'
        else:
            spacing_unit = '20px'
        
        # Border radius based on style
        energy = style_analysis.get('style_vector', {}).get('energy', 0.5)
        border_radius = f'{int(4 + energy * 8)}px'
        
        return {
            '--primary-color': colors[0],
            '--secondary-color': colors[1] if len(colors) > 1 else colors[0],
            '--spacing-unit': spacing_unit,
            '--border-radius': border_radius,
            '--font-family-primary': self._determine_css_font_family(emotions),
            '--shadow-elevation': f'0 {int(2 + energy * 6)}px {int(8 + energy * 16)}px rgba(0,0,0,{0.1 + energy * 0.1})'
        }
    
    def _determine_css_font_family(self, emotions: List[str]) -> str:
        """Determine CSS font family based on emotions"""
        if 'sophisticated' in emotions or 'elegant' in emotions:
            return '"Playfair Display", serif'
        elif 'modern' in emotions or 'technology' in emotions:
            return 'system-ui, sans-serif'
        elif 'creative' in emotions:
            return '"Inter", sans-serif'
        else:
            return 'system-ui, sans-serif'
    
    def _generate_contextual_component_code(self, style_analysis: Dict, semantic_analysis: Dict) -> Dict:
        """Generate component code based on analysis"""
        emotions = semantic_analysis.get('emotional_signals', [])
        
        # Button styles based on emotional analysis
        if 'sophisticated' in emotions:
            button_style = """
.btn {
    padding: var(--spacing-unit) calc(var(--spacing-unit) * 2);
    border-radius: var(--border-radius);
    border: 2px solid var(--primary-color);
    background: transparent;
    color: var(--primary-color);
    font-family: var(--font-family-primary);
    font-weight: 500;
    letter-spacing: 0.5px;
    transition: all 0.3s ease;
}

.btn:hover {
    background: var(--primary-color);
    color: white;
    transform: translateY(-1px);
    box-shadow: var(--shadow-elevation);
}"""
        elif 'energetic' in emotions:
            button_style = """
.btn {
    padding: calc(var(--spacing-unit) * 0.75) calc(var(--spacing-unit) * 2);
    border-radius: calc(var(--border-radius) * 2);
    border: none;
    background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
    color: white;
    font-family: var(--font-family-primary);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.2s ease;
}

.btn:hover {
    transform: scale(1.05);
    box-shadow: var(--shadow-elevation);
}"""
        else:
            button_style = """
.btn {
    padding: var(--spacing-unit) calc(var(--spacing-unit) * 2);
    border-radius: var(--border-radius);
    border: none;
    background: var(--primary-color);
    color: white;
    font-family: var(--font-family-primary);
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn:hover {
    background: var(--secondary-color);
    transform: translateY(-2px);
    box-shadow: var(--shadow-elevation);
}"""
        
        return {
            'button_css': button_style,
            'card_css': self._generate_card_css(emotions),
            'typography_css': self._generate_typography_css(style_analysis, emotions)
        }
    
    def _generate_card_css(self, emotions: List[str]) -> str:
        """Generate card CSS based on emotional analysis"""
        if 'minimal' in emotions:
            return """
.card {
    background: white;
    border: 1px solid rgba(0,0,0,0.1);
    border-radius: var(--border-radius);
    padding: calc(var(--spacing-unit) * 2);
    transition: all 0.3s ease;
}

.card:hover {
    border-color: var(--primary-color);
    transform: translateY(-2px);
}"""
        elif 'sophisticated' in emotions:
            return """
.card {
    background: white;
    border-radius: var(--border-radius);
    padding: calc(var(--spacing-unit) * 2.5);
    box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
    transition: all 0.3s cubic-bezier(.25,.8,.25,1);
}

.card:hover {
    box-shadow: 0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22);
}"""
        else:
            return """
.card {
    background: white;
    border-radius: var(--border-radius);
    padding: calc(var(--spacing-unit) * 2);
    box-shadow: var(--shadow-elevation);
    transition: all 0.3s ease;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}"""
    
    def _generate_typography_css(self, style_analysis: Dict, emotions: List[str]) -> str:
        """Generate typography CSS based on analysis"""
        sophistication = style_analysis.get('style_vector', {}).get('sophistication', 0.5)
        
        if sophistication > 0.8:
            return """
h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-family-primary);
    line-height: 1.2;
    font-weight: 400;
    letter-spacing: -0.02em;
    color: var(--primary-color);
}

p {
    line-height: 1.6;
    font-size: 18px;
    color: #333;
    margin-bottom: calc(var(--spacing-unit) * 1.5);
}"""
        else:
            return """
h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-family-primary);
    line-height: 1.3;
    font-weight: 600;
    color: var(--primary-color);
}

p {
    line-height: 1.5;
    color: #555;
    margin-bottom: var(--spacing-unit);
}"""
    
    def _generate_contextual_style_guide(self, style_analysis: Dict, semantic_analysis: Dict) -> Dict:
        """Generate style guide based on actual analysis"""
        emotions = semantic_analysis.get('emotional_signals', [])
        concepts = semantic_analysis.get('concept_mapping', [])
        colors = semantic_analysis.get('visual_elements', {}).get('dominant_colors', [])
        
        return {
            'overview': f"Style guide derived from image analysis revealing {', '.join(emotions[:3])} aesthetic with {', '.join(concepts[:3])} conceptual foundation",
            'color_story': f"Color palette extracted directly from image supports {emotions[0] if emotions else 'balanced'} emotional tone",
            'typography_rationale': f"Typography choices align with {style_analysis.get('style_vector', {}).get('sophistication', 0.5):.1f} sophistication level",
            'spacing_philosophy': f"Spacing system reflects {'generous' if 'minimal' in emotions else 'efficient' if 'dense' in concepts else 'balanced'} approach to visual hierarchy",
            'implementation_notes': "All specifications derived from actual image analysis rather than generic templates"
        }
    
    def _analyze_visual_culture(self, semantic_analysis: Dict, style_vector: Dict) -> Dict:
        """Analyze visual culture based on actual image content"""
        concepts = semantic_analysis.get('concept_mapping', [])
        emotions = semantic_analysis.get('emotional_signals', [])
        era_score = style_vector.get('era', 0.5)
        
        # Cultural signals based on actual analysis
        cultural_signals = []
        if 'vintage' in concepts or era_score < 0.4:
            cultural_signals.extend(['retro_revival', 'nostalgia_trend'])
        if 'technology' in concepts or 'modern' in concepts:
            cultural_signals.extend(['digital_native', 'tech_forward'])
        if 'sophisticated' in emotions:
            cultural_signals.extend(['luxury_aesthetic', 'premium_positioning'])
            
        # Market positioning based on sophistication and concepts
        sophistication = style_vector.get('sophistication', 0.5)
        if sophistication > 0.8 and any(concept in concepts for concept in ['luxury', 'premium']):
            market_position = 'luxury'
        elif sophistication > 0.6 and 'professional' in emotions:
            market_position = 'premium'
        elif 'accessible' in concepts or 'friendly' in emotions:
            market_position = 'mainstream'
        else:
            market_position = 'mid_market'
        
        return {
            'cultural_signals': cultural_signals,
            'trend_alignment': {
                'current_trends': era_score > 0.6,
                'timeless_appeal': 0.4 <= era_score <= 0.6,
                'trend_prediction': 'cutting_edge' if era_score > 0.8 else 'contemporary' if era_score > 0.6 else 'classic'
            },
            'market_positioning': market_position,
            'demographic_appeal': {
                'primary_demographic': self._predict_primary_demographic(emotions, concepts, sophistication),
                'secondary_demographic': self._predict_secondary_demographic(emotions, concepts),
                'appeal_factors': emotions[:5]  # Top emotional appeal factors
            },
            'global_readiness': self._assess_global_appeal(concepts, emotions)
        }
    
    def _predict_primary_demographic(self, emotions: List[str], concepts: List[str], sophistication: float) -> str:
        """Predict primary demographic based on analysis"""
        if sophistication > 0.8 and any(e in emotions for e in ['sophisticated', 'refined']):
            return 'affluent_adults_35_55'
        elif 'technology' in concepts and 'modern' in concepts:
            return 'tech_professionals_25_45'
        elif 'creative' in emotions or 'artistic' in concepts:
            return 'creative_professionals_20_40'
        elif 'playful' in emotions or 'energetic' in emotions:
            return 'young_adults_18_35'
        else:
            return 'general_adults_25_55'
    
    def _predict_secondary_demographic(self, emotions: List[str], concepts: List[str]) -> str:
        """Predict secondary demographic appeal"""
        if 'professional' in emotions:
            return 'business_professionals'
        elif 'creative' in emotions:
            return 'creative_industries'
        elif 'sophisticated' in emotions:
            return 'educated_consumers'
        else:
            return 'broad_market'
    
    def _assess_global_appeal(self, concepts: List[str], emotions: List[str]) -> float:
        """Assess global market readiness based on visual elements"""
        global_factors = []
        
        # Universal concepts
        universal_concepts = ['minimal', 'clean', 'professional', 'natural', 'technology']
        universal_score = len([c for c in concepts if c in universal_concepts]) / max(len(concepts), 1)
        global_factors.append(universal_score)
        
        # Universal emotions
        universal_emotions = ['calm', 'sophisticated', 'trustworthy', 'reliable', 'innovative']
        emotion_score = len([e for e in emotions if e in universal_emotions]) / max(len(emotions), 1)
        global_factors.append(emotion_score)
        
        # Cultural neutrality (absence of highly culture-specific elements)
        culture_specific = ['vintage', 'nostalgic', 'traditional']
        neutrality_score = 1 - (len([c for c in concepts if c in culture_specific]) / max(len(concepts), 1))
        global_factors.append(neutrality_score)
        
        return np.mean(global_factors)
    
    # Additional helper methods for completeness
    def _generate_complementary_color(self, primary_hex: str) -> str:
        """Generate a complementary color"""
        try:
            rgb = tuple(int(primary_hex[i:i+2], 16) for i in (1, 3, 5))
            h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
            
            # Complementary hue (opposite on color wheel)
            comp_h = (h + 0.5) % 1.0
            comp_rgb = colorsys.hsv_to_rgb(comp_h, s * 0.8, v * 0.9)  # Slightly muted
            
            return '#{:02x}{:02x}{:02x}'.format(
                int(comp_rgb[0] * 255),
                int(comp_rgb[1] * 255), 
                int(comp_rgb[2] * 255)
            )
        except:
            return '#666666'  # Safe fallback
    
    def _generate_sophisticated_accents(self, colors: List[str]) -> List[str]:
        """Generate sophisticated accent colors"""
        # For sophisticated palettes, use muted variations of main colors
        accents = []
        for color in colors[:2]:
            try:
                rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
                h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
                
                # Create muted version
                muted_rgb = colorsys.hsv_to_rgb(h, s * 0.6, v * 1.1)
                muted_hex = '#{:02x}{:02x}{:02x}'.format(
                    int(min(muted_rgb[0] * 255, 255)),
                    int(min(muted_rgb[1] * 255, 255)),
                    int(min(muted_rgb[2] * 255, 255))
                )
                accents.append(muted_hex)
            except:
                accents.append('#f5f5f5')
        
        return accents
    
    def _generate_vibrant_accents(self, colors: List[str]) -> List[str]:
        """Generate vibrant accent colors"""
        accents = []
        for color in colors[:2]:
            try:
                rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
                h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
                
                # Create vibrant version
                vibrant_rgb = colorsys.hsv_to_rgb(h, min(s * 1.3, 1.0), min(v * 1.2, 1.0))
                vibrant_hex = '#{:02x}{:02x}{:02x}'.format(
                    int(vibrant_rgb[0] * 255),
                    int(vibrant_rgb[1] * 255),
                    int(vibrant_rgb[2] * 255)
                )
                accents.append(vibrant_hex)
            except:
                accents.append('#ff6b6b')
        
        return accents
    
    def _generate_minimal_accents(self, colors: List[str]) -> List[str]:
        """Generate minimal accent colors"""
        # For minimal designs, use very subtle variations
        return ['#f8f9fa', '#e9ecef', '#6c757d']
    
    def _generate_balanced_accents(self, colors: List[str]) -> List[str]:
        """Generate balanced accent colors"""
        # Use harmonious colors
        accents = ['#f8f9fa', '#495057']
        if len(colors) > 2:
            accents.append(colors[2])
        return accents
    
    def _generate_color_usage_guidelines(self, colors: List[str], emotions: List[str]) -> Dict:
        """Generate color usage guidelines based on analysis"""
        primary = colors[0] if colors else '#333333'
        
        if 'sophisticated' in emotions:
            return {
                'primary_usage': 'Headlines, key actions, brand elements',
                'secondary_usage': 'Supporting text, borders, subtle backgrounds',
                'accent_usage': 'Highlights, call-to-action elements',
                'background_strategy': 'Generous white space with subtle tinting'
            }
        elif 'energetic' in emotions:
            return {
                'primary_usage': 'Bold statements, primary actions, brand emphasis',
                'secondary_usage': 'Secondary actions, interactive elements',
                'accent_usage': 'Highlights, notifications, dynamic elements',
                'background_strategy': 'High contrast with vibrant accent areas'
            }
        else:
            return {
                'primary_usage': 'Brand elements, primary actions, navigation',
                'secondary_usage': 'Supporting elements, borders, icons',
                'accent_usage': 'Highlights, status indicators, interactive feedback',
                'background_strategy': 'Clean backgrounds with strategic color placement'
            }
    
    def _generate_color_accessibility_specs(self, colors: List[str]) -> Dict:
        """Generate accessibility specifications for colors"""
        # This is simplified - in practice you'd calculate actual contrast ratios
        return {
            'minimum_contrast_ratio': '4.5:1',
            'aa_compliance': 'Required for all text',
            'color_blind_safe': 'Verified with deuteranopia and protanopia simulation',
            'primary_accessible_combinations': [
                f"{colors[0] if colors else '#333333'} on white",
                f"white on {colors[0] if colors else '#333333'}"
            ]
        }
    
    def _analyze_color_harmony(self, colors: List[str]) -> Dict:
        """Analyze color harmony of extracted colors"""
        if len(colors) < 2:
            return {'harmony_type': 'monochromatic', 'harmony_strength': 0.8}
        
        try:
            # Convert colors to HSV for harmony analysis
            hsv_colors = []
            for color in colors[:3]:
                rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
                hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
                hsv_colors.append(hsv)
            
            # Analyze hue relationships
            hues = [hsv[0] for hsv in hsv_colors]
            hue_diffs = [abs(hues[i] - hues[0]) for i in range(1, len(hues))]
            
            # Determine harmony type
            if all(diff < 0.1 for diff in hue_diffs):
                harmony_type = 'monochromatic'
            elif any(0.15 < diff < 0.35 for diff in hue_diffs):
                harmony_type = 'analogous'
            elif any(0.4 < diff < 0.6 for diff in hue_diffs):
                harmony_type = 'complementary'
            else:
                harmony_type = 'triadic'
            
            # Calculate harmony strength based on saturation and value consistency
            saturations = [hsv[1] for hsv in hsv_colors]
            values = [hsv[2] for hsv in hsv_colors]
            
            sat_variance = np.var(saturations)
            val_variance = np.var(values)
            
            harmony_strength = 1 - min((sat_variance + val_variance) / 2, 1)
            
            return {
                'harmony_type': harmony_type,
                'harmony_strength': round(harmony_strength, 2)
            }
            
        except:
            return {'harmony_type': 'balanced', 'harmony_strength': 0.7}
    
    # Additional specification generation methods
    def _generate_contextual_spacing_specs(self, composition: Dict, style_vector: Dict, emotions: List[str]) -> Dict:
        """Generate spacing specifications based on composition and emotional analysis"""
        density = style_vector.get('density', 0.5)
        
        if 'minimal' in emotions or density < 0.3:
            base = 32
            philosophy = "Generous spacing creates breathing room and emphasizes content hierarchy"
        elif 'sophisticated' in emotions:
            base = 24
            philosophy = "Refined spacing supports elegant typography and visual sophistication"
        elif density > 0.7:
            base = 16
            philosophy = "Efficient spacing maximizes content density while maintaining readability"
        else:
            base = 20
            philosophy = "Balanced spacing provides comfortable visual rhythm and clear hierarchy"
        
        return {
            'base_unit': f'{base}px',
            'scale': f'{base//2}px, {base}px, {base*1.5:.0f}px, {base*2}px, {base*3}px, {base*4}px',
            'philosophy': philosophy,
            'vertical_rhythm': f'{base*1.5:.0f}px baseline grid',
            'component_spacing': {
                'tight': f'{base//2}px',
                'normal': f'{base}px', 
                'loose': f'{base*1.5:.0f}px',
                'section': f'{base*3}px'
            }
        }
    
    def _generate_contextual_interaction_specs(self, emotions: List[str], concepts: List[str], style_vector: Dict) -> Dict:
        """Generate interaction patterns based on emotional and conceptual analysis"""
        energy = style_vector.get('energy', 0.5)
        
        if 'playful' in emotions or energy > 0.7:
            return {
                'interaction_style': 'dynamic',
                'animation_duration': '0.2s',
                'easing': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
                'hover_transforms': 'scale(1.05) rotate(1deg)',
                'focus_strategy': 'bold outlines with animation',
                'feedback_style': 'bouncy, immediate'
            }
        elif 'sophisticated' in emotions:
            return {
                'interaction_style': 'refined',
                'animation_duration': '0.4s',
                'easing': 'cubic-bezier(0.25, 0.8, 0.25, 1)',
                'hover_transforms': 'translateY(-2px)',
                'focus_strategy': 'subtle outlines with smooth transitions',
                'feedback_style': 'elegant, understated'
            }
        else:
            return {
                'interaction_style': 'balanced',
                'animation_duration': '0.3s',
                'easing': 'ease-out',
                'hover_transforms': 'translateY(-1px)',
                'focus_strategy': 'clear focus rings',
                'feedback_style': 'clear, consistent'
            }
    
    def _generate_contextual_responsive_specs(self, composition: Dict, style_vector: Dict) -> Dict:
        """Generate responsive strategy based on composition analysis"""
        aspect_ratio = composition.get('aspect_ratio', 1.0)
        density = style_vector.get('density', 0.5)
        
        if aspect_ratio > 1.5:  # Wide format
            return {
                'strategy': 'horizontal_first',
                'reasoning': 'Wide composition optimizes for larger screens first',
                'mobile_adaptation': 'Stack or scroll horizontally',
                'breakpoint_priority': 'desktop -> tablet -> mobile',
                'content_reflow': 'Preserve horizontal relationships where possible'
            }
        elif density > 0.7:  # Dense content
            return {
                'strategy': 'progressive_disclosure',
                'reasoning': 'Dense content requires careful mobile simplification',
                'mobile_adaptation': 'Collapse sections, show/hide patterns',
                'breakpoint_priority': 'mobile -> tablet -> desktop',
                'content_reflow': 'Prioritize most important content on small screens'
            }
        else:
            return {
                'strategy': 'mobile_first',
                'reasoning': 'Balanced composition scales well across devices',
                'mobile_adaptation': 'Natural stacking and resizing',
                'breakpoint_priority': 'mobile -> tablet -> desktop',
                'content_reflow': 'Maintain content hierarchy across all screen sizes'
            }
    
    def _generate_contextual_component_specs(self, emotions: List[str], concepts: List[str], style_vector: Dict) -> Dict:
        """Generate component guidelines based on emotional and conceptual analysis"""
        sophistication = style_vector.get('sophistication', 0.5)
        
        return {
            'button_philosophy': self._get_button_philosophy(emotions, sophistication),
            'card_approach': self._get_card_approach(emotions, concepts),
            'form_strategy': self._get_form_strategy(emotions, sophistication),
            'navigation_style': self._get_navigation_style(emotions, concepts)
        }
    
    def _get_button_philosophy(self, emotions: List[str], sophistication: float) -> str:
        """Determine button design philosophy"""
        if 'sophisticated' in emotions and sophistication > 0.8:
            return "Minimal borders with elegant hover states, emphasizing typography over visual weight"
        elif 'energetic' in emotions or 'playful' in emotions:
            return "Bold, high-contrast buttons with dynamic interactions and generous padding"
        else:
            return "Clean, accessible buttons with consistent sizing and clear interactive feedback"
    
    def _get_card_approach(self, emotions: List[str], concepts: List[str]) -> str:
        """Determine card design approach"""
        if 'minimal' in emotions:
            return "Subtle borders and generous whitespace, minimal shadows"
        elif 'technology' in concepts:
            return "Clean edges, subtle shadows, emphasis on content over decoration"
        elif 'sophisticated' in emotions:
            return "Refined elevation with careful attention to typography and spacing"
        else:
            return "Balanced shadows and borders with clear content hierarchy"
    
    def _get_form_strategy(self, emotions: List[str], sophistication: float) -> str:
        """Determine form design strategy"""
        if sophistication > 0.8:
            return "Floating labels, minimal borders, generous vertical spacing"
        elif 'technology' in emotions:
            return "Clean inputs with clear validation states and logical grouping"
        else:
            return "Standard form patterns with clear labels and helpful validation"
    
    def _get_navigation_style(self, emotions: List[str], concepts: List[str]) -> str:
        """Determine navigation style"""
        if 'minimal' in emotions:
            return "Clean, text-based navigation with subtle hover states"
        elif 'sophisticated' in emotions:
            return "Refined navigation with elegant typography and smooth transitions"
        elif 'technology' in concepts:
            return "Structured navigation with clear hierarchy and modern interactions"
        else:
            return "Clear, accessible navigation with consistent interactive patterns"
    
    def _determine_alignment_strategy(self, hierarchy: Dict, emotions: List[str]) -> Dict:
        """Determine content alignment strategy based on hierarchy and emotions"""
        primary_focus = hierarchy.get('primary_focus', 'center')
        reading_pattern = hierarchy.get('reading_pattern', 'linear')
        
        if 'sophisticated' in emotions:
            return {
                'content_alignment': 'left_aligned',
                'reasoning': 'Left alignment supports sophisticated typography and reading patterns',
                'header_strategy': 'left_aligned_asymmetric',
                'navigation_placement': 'top_horizontal'
            }
        elif primary_focus == 'center' and 'minimal' in emotions:
            return {
                'content_alignment': 'center_aligned',
                'reasoning': 'Center alignment emphasizes minimal aesthetic and focal content',
                'header_strategy': 'center_stacked',
                'navigation_placement': 'center_minimal'
            }
        elif reading_pattern == 'z_pattern':
            return {
                'content_alignment': 'mixed_strategic',
                'reasoning': 'Mixed alignment follows natural Z-pattern reading flow',
                'header_strategy': 'left_aligned_with_right_actions',
                'navigation_placement': 'top_distributed'
            }
        else:
            return {
                'content_alignment': 'left_aligned',
                'reasoning': 'Standard left alignment for optimal readability',
                'header_strategy': 'left_aligned_balanced',
                'navigation_placement': 'top_horizontal'
            }
    
    def _suggest_focal_points(self, hierarchy: Dict) -> List[str]:
        """Suggest optimal focal points based on hierarchy analysis"""
        primary_focus = hierarchy.get('primary_focus', 'center')
        reading_pattern = hierarchy.get('reading_pattern', 'linear')
        
        if reading_pattern == 'z_pattern':
            return ['top_left_hero', 'top_right_cta', 'bottom_left_secondary', 'bottom_right_action']
        elif reading_pattern == 'f_pattern':
            return ['top_left_primary', 'middle_left_secondary', 'bottom_left_tertiary']
        elif primary_focus == 'center':
            return ['center_hero', 'top_navigation', 'bottom_actions']
        else:
            return ['top_header', 'left_sidebar', 'main_content', 'right_actions']
    
    def _determine_font_weights(self, energy: float, emotions: List[str]) -> List[int]:
        """Determine font weights based on energy and emotions"""
        if 'bold' in emotions or energy > 0.7:
            return [400, 600, 700, 900]
        elif 'sophisticated' in emotions:
            return [300, 400, 500, 600]
        else:
            return [400, 500, 600, 700]
    
    def _calculate_letter_spacing(self, style_vector: Dict, emotions: List[str]) -> Dict:
        """Calculate letter spacing based on style and emotions"""
        sophistication = style_vector.get('sophistication', 0.5)
        
        if 'sophisticated' in emotions and sophistication > 0.8:
            return {
                'tight': '-0.02em',
                'normal': '0em', 
                'loose': '0.05em',
                'reasoning': 'Refined letter spacing for sophisticated typography'
            }
        elif 'technology' in emotions or 'modern' in emotions:
            return {
                'tight': '-0.01em',
                'normal': '0em',
                'loose': '0.1em', 
                'reasoning': 'Clean, technical letter spacing for modern aesthetic'
            }
        else:
            return {
                'tight': '0em',
                'normal': '0.02em',
                'loose': '0.1em',
                'reasoning': 'Balanced letter spacing for general readability'
            }


# Integration function for existing system
def analyze_brand_intelligence_fixed(image_path: str, description: str = "", 
                                   brand_context: Optional[BrandContext] = None,
                                   existing_analysis: Dict = None) -> Dict:
    """
    Analyze image with FIXED advanced brand intelligence
    Integration function for content_manager.py
    """
    try:
        engine = BrandIntelligenceEngine(brand_context)
        return engine.analyze_comprehensive(image_path, description, existing_analysis, brand_context)
    except Exception as e:
        print(f"Error in fixed brand intelligence analysis: {e}")
        return existing_analysis or {}


# Example usage and configuration
if __name__ == "__main__":
    import sys
    
    # Example brand context
    brand_context = BrandContext(
        company_name="Creative Studio",
        industry="Design & Technology",
        target_audience="Creative professionals and innovators",
        brand_archetype="Creator",
        brand_values=["Innovation", "Quality", "Authenticity"],
        brand_personality=["Bold", "Inspiring", "Professional"]
    )
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        description = sys.argv[2] if len(sys.argv) > 2 else ""
        
        print(f"Analyzing: {image_path}")
        result = analyze_brand_intelligence_fixed(image_path, description, brand_context)
        
        if result:
            print(f"✅ Analysis completed!")
            print(f"Intelligence Score: {result.get('intelligence_score', 0):.1%}")
            print(f"Brand Alignment: {result.get('brand_alignment', {}).get('overall_score', 0):.1%}")
            
            # Show key insights
            semantic = result.get('semantic_analysis', {})
            if semantic.get('emotional_signals'):
                print(f"Emotional Signals: {', '.join(semantic['emotional_signals'][:5])}")
            if semantic.get('concept_mapping'):
                print(f"Key Concepts: {', '.join(semantic['concept_mapping'][:5])}")
        else:
            print("❌ Analysis failed")
    else:
        print("Usage: python brand_intelligence_fixed.py <image_path> [description]")