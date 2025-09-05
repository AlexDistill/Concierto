#!/usr/bin/env python3
"""
Advanced Brand Intelligence Engine
Extracts meaning, structure, and specifications from images with contextual brand awareness
"""

import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

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

@dataclass
class SemanticAnalysis:
    """Semantic meaning extracted from image"""
    primary_subjects: List[str]
    emotions: List[str]
    concepts: List[str]
    symbols: List[str]
    composition_type: str
    visual_metaphors: List[str]
    cultural_signals: List[str]
    narrative_elements: List[str]

@dataclass
class DesignSpecifications:
    """Technical design specifications"""
    layout_grid: str
    typography_scale: Dict[str, str]
    color_palette: Dict[str, str]
    component_specs: Dict[str, Any]
    responsive_breakpoints: Dict[str, str]
    accessibility_score: float
    print_specifications: Dict[str, str]
    implementation_tokens: Dict[str, Any]

class BrandIntelligenceEngine:
    """Advanced brand intelligence system"""
    
    def __init__(self, brand_context: Optional[BrandContext] = None):
        self.brand_context = brand_context or BrandContext()
        self.semantic_models = self._load_semantic_models()
        self.brand_archetypes = self._load_brand_archetypes()
        self.design_patterns = self._load_design_patterns()
        
    def _load_semantic_models(self):
        """Load semantic analysis models"""
        return {
            'emotions': {
                # Color-emotion mappings
                'warm_colors': ['excitement', 'energy', 'passion', 'warmth'],
                'cool_colors': ['calm', 'trust', 'professional', 'stability'],
                'bright_colors': ['optimism', 'creativity', 'youth', 'playfulness'],
                'muted_colors': ['sophistication', 'elegance', 'maturity', 'subtlety'],
                'dark_colors': ['authority', 'luxury', 'mystery', 'strength'],
                'light_colors': ['purity', 'simplicity', 'freshness', 'openness']
            },
            'composition_types': {
                'centered': 'formal, stable, traditional',
                'rule_of_thirds': 'dynamic, balanced, professional',
                'diagonal': 'energetic, modern, progressive',
                'symmetrical': 'formal, harmonious, reliable',
                'asymmetrical': 'creative, modern, flexible',
                'minimal': 'clean, focused, premium'
            },
            'visual_elements': {
                'geometric_shapes': 'structured, modern, technological',
                'organic_shapes': 'natural, approachable, human',
                'textures': 'tactile, authentic, crafted',
                'patterns': 'systematic, traditional, decorative',
                'negative_space': 'premium, sophisticated, minimal'
            }
        }
    
    def _load_brand_archetypes(self):
        """Load brand archetype patterns"""
        return {
            'Hero': {
                'visual_traits': ['bold', 'strong', 'confident', 'action-oriented'],
                'color_preferences': ['red', 'black', 'strong_contrasts'],
                'composition_style': 'dynamic',
                'typography': 'sans-serif, bold'
            },
            'Sage': {
                'visual_traits': ['wise', 'knowledgeable', 'trustworthy', 'authoritative'],
                'color_preferences': ['blue', 'gray', 'white', 'muted_tones'],
                'composition_style': 'balanced',
                'typography': 'serif, readable'
            },
            'Creator': {
                'visual_traits': ['innovative', 'artistic', 'original', 'expressive'],
                'color_preferences': ['vibrant', 'unique_combinations', 'artistic'],
                'composition_style': 'creative',
                'typography': 'creative, display'
            },
            'Caregiver': {
                'visual_traits': ['nurturing', 'warm', 'supportive', 'reliable'],
                'color_preferences': ['warm_colors', 'soft_tones', 'pastels'],
                'composition_style': 'harmonious',
                'typography': 'friendly, rounded'
            },
            'Explorer': {
                'visual_traits': ['adventurous', 'free', 'pioneering', 'rugged'],
                'color_preferences': ['earth_tones', 'natural_colors'],
                'composition_style': 'dynamic',
                'typography': 'strong, outdoor'
            }
        }
    
    def _load_design_patterns(self):
        """Load design pattern recognition"""
        return {
            'grid_systems': {
                '12_column': 'flexible, responsive',
                '16_column': 'detailed, complex',
                'modular': 'systematic, consistent',
                'asymmetric': 'creative, unique'
            },
            'spacing_patterns': {
                'tight': '4px base unit',
                'standard': '8px base unit', 
                'generous': '16px base unit',
                'luxurious': '24px base unit'
            },
            'typography_patterns': {
                'minimal': 'single font family',
                'classic': 'serif + sans-serif pair',
                'expressive': 'display + body combination',
                'systematic': 'type scale progression'
            }
        }
    
    def analyze_comprehensive(self, image_path: str, description: str = "", 
                            existing_analysis: Dict = None, brand_context: BrandContext = None) -> Dict:
        """
        Perform comprehensive brand intelligence analysis
        """
        try:
            # Start with existing style vector analysis
            if existing_analysis and 'style_vector' in existing_analysis:
                style_analysis = existing_analysis
            else:
                style_analysis = analyze_style_vector(image_path)
            
            if not style_analysis:
                return None
                
            # Extract semantic meaning
            semantic_analysis = self._analyze_semantics(image_path, description, 
                                                       style_analysis['style_vector'])
            
            # Generate design specifications
            design_specs = self._generate_specifications(style_analysis, semantic_analysis)
            
            # Analyze brand alignment
            brand_alignment = self._analyze_brand_alignment(semantic_analysis, 
                                                          style_analysis['style_vector'], brand_context)
            
            # Extract implementation details
            implementation = self._generate_implementation_specs(style_analysis, design_specs)
            
            # Cultural and trend analysis
            cultural_analysis = self._analyze_cultural_context(semantic_analysis, 
                                                             style_analysis['style_vector'])
            
            return {
                **style_analysis,
                'semantic_analysis': semantic_analysis,
                'design_specifications': design_specs,
                'brand_alignment': brand_alignment,
                'implementation': implementation,
                'cultural_analysis': cultural_analysis,
                'intelligence_score': self._calculate_intelligence_score(semantic_analysis, brand_alignment),
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error in comprehensive analysis: {e}")
            return existing_analysis
    
    def _analyze_semantics(self, image_path: str, description: str, style_vector: Dict) -> Dict:
        """Extract semantic meaning from image and description"""
        try:
            img = Image.open(image_path).convert('RGB')
            
            # Analyze composition structure
            composition = self._analyze_composition(img)
            
            # Extract emotional signals
            emotions = self._extract_emotions(style_vector, description)
            
            # Identify visual concepts
            concepts = self._identify_concepts(description, style_vector)
            
            # Detect symbols and metaphors
            symbols = self._detect_symbols(img, description)
            
            return {
                'composition_analysis': composition,
                'emotional_signals': emotions,
                'concept_mapping': concepts,
                'symbol_detection': symbols,
                'narrative_structure': self._analyze_narrative(description),
                'visual_hierarchy': self._analyze_hierarchy(img),
                'meaning_extraction': self._extract_meaning(description, concepts, emotions)
            }
            
        except Exception as e:
            print(f"Error in semantic analysis: {e}")
            return {}
    
    def _analyze_composition(self, img: Image) -> Dict:
        """Analyze composition structure"""
        width, height = img.size
        aspect_ratio = width / height
        
        # Analyze image regions using rule of thirds
        third_w, third_h = width // 3, height // 3
        
        # Simple composition analysis
        composition_type = 'balanced'
        if abs(aspect_ratio - 1.618) < 0.1:  # Golden ratio
            composition_type = 'golden_ratio'
        elif abs(aspect_ratio - 1.0) < 0.1:  # Square
            composition_type = 'square_centered'
        elif aspect_ratio > 2:  # Wide
            composition_type = 'panoramic'
        elif aspect_ratio < 0.7:  # Tall
            composition_type = 'vertical_emphasis'
            
        return {
            'type': composition_type,
            'aspect_ratio': round(aspect_ratio, 2),
            'dimensions': f"{width}x{height}",
            'format_category': self._categorize_format(width, height),
            'visual_weight_distribution': self._analyze_visual_weight(img)
        }
    
    def _extract_emotions(self, style_vector: Dict, description: str) -> List[str]:
        """Extract emotional signals from style and description"""
        emotions = []
        
        # Style-based emotions
        energy = style_vector.get('energy', 0.5)
        sophistication = style_vector.get('sophistication', 0.5)
        temperature = style_vector.get('temperature', 0.5)
        
        if energy > 0.7:
            emotions.extend(['energetic', 'dynamic', 'exciting'])
        elif energy < 0.3:
            emotions.extend(['calm', 'peaceful', 'serene'])
            
        if sophistication > 0.7:
            emotions.extend(['sophisticated', 'refined', 'elegant'])
        elif sophistication < 0.3:
            emotions.extend(['playful', 'casual', 'approachable'])
            
        if temperature > 0.7:
            emotions.extend(['warm', 'inviting', 'energetic'])
        elif temperature < 0.3:
            emotions.extend(['cool', 'professional', 'calm'])
        
        # Description-based emotions
        emotion_keywords = {
            'happy': ['happy', 'joy', 'smile', 'cheerful', 'bright'],
            'serious': ['serious', 'professional', 'formal', 'business'],
            'creative': ['creative', 'artistic', 'innovative', 'unique'],
            'trustworthy': ['trust', 'reliable', 'stable', 'secure'],
            'modern': ['modern', 'contemporary', 'fresh', 'new'],
            'traditional': ['traditional', 'classic', 'timeless', 'heritage']
        }
        
        desc_lower = description.lower()
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in desc_lower for keyword in keywords):
                emotions.append(emotion)
        
        return list(set(emotions))
    
    def _identify_concepts(self, description: str, style_vector: Dict) -> List[str]:
        """Identify high-level concepts"""
        concepts = []
        
        concept_keywords = {
            'luxury': ['luxury', 'premium', 'exclusive', 'high-end', 'elegant'],
            'technology': ['tech', 'digital', 'innovation', 'future', 'modern'],
            'nature': ['natural', 'organic', 'earth', 'green', 'sustainable'],
            'minimalism': ['minimal', 'clean', 'simple', 'space', 'less'],
            'vintage': ['vintage', 'retro', 'classic', 'old', 'nostalgic'],
            'artistic': ['art', 'creative', 'design', 'aesthetic', 'beauty'],
            'corporate': ['business', 'professional', 'corporate', 'office'],
            'lifestyle': ['lifestyle', 'living', 'home', 'personal', 'daily']
        }
        
        desc_lower = description.lower()
        for concept, keywords in concept_keywords.items():
            if any(keyword in desc_lower for keyword in keywords):
                concepts.append(concept)
        
        # Add concepts based on style vector
        density = style_vector.get('density', 0.5)
        era = style_vector.get('era', 0.5)
        
        if density < 0.3:
            concepts.append('minimalism')
        elif density > 0.7:
            concepts.append('maximalism')
            
        if era > 0.7:
            concepts.append('futuristic')
        elif era < 0.3:
            concepts.append('vintage')
        
        return list(set(concepts))
    
    def _detect_symbols(self, img: Image, description: str) -> List[str]:
        """Detect symbolic elements"""
        symbols = []
        
        # Text-based symbol detection
        symbol_keywords = {
            'geometric': ['circle', 'square', 'triangle', 'geometric', 'pattern'],
            'organic': ['leaf', 'tree', 'flower', 'natural', 'curved'],
            'arrows': ['arrow', 'direction', 'pointing', 'forward'],
            'stars': ['star', 'sparkle', 'shine', 'bright'],
            'hands': ['hand', 'gesture', 'touch', 'reach'],
            'eyes': ['eye', 'vision', 'see', 'watch', 'look'],
            'heart': ['heart', 'love', 'care', 'emotion'],
            'crown': ['crown', 'king', 'queen', 'royal', 'premium']
        }
        
        desc_lower = description.lower()
        for symbol, keywords in symbol_keywords.items():
            if any(keyword in desc_lower for keyword in keywords):
                symbols.append(symbol)
        
        return symbols
    
    def _analyze_narrative(self, description: str) -> Dict:
        """Analyze narrative structure in description"""
        return {
            'story_elements': self._extract_story_elements(description),
            'tone': self._analyze_tone(description),
            'perspective': self._analyze_perspective(description),
            'temporal_context': self._extract_temporal_context(description)
        }
    
    def _analyze_hierarchy(self, img: Image) -> Dict:
        """Analyze visual hierarchy"""
        # Simplified hierarchy analysis
        return {
            'primary_focus': 'center',  # Simplified
            'secondary_elements': 'periphery',
            'reading_pattern': 'z_pattern',  # Common web pattern
            'contrast_areas': 'high'
        }
    
    def _extract_meaning(self, description: str, concepts: List[str], emotions: List[str]) -> Dict:
        """Extract deeper meaning from combined analysis"""
        return {
            'primary_message': self._identify_primary_message(description, concepts),
            'emotional_journey': emotions,
            'brand_story_alignment': self._assess_story_alignment(concepts, emotions),
            'audience_resonance': self._predict_audience_resonance(concepts, emotions)
        }
    
    def _generate_specifications(self, style_analysis: Dict, semantic_analysis: Dict) -> Dict:
        """Generate detailed design specifications"""
        style_vector = style_analysis['style_vector']
        brand_tokens = style_analysis['brand_tokens']
        
        # Generate comprehensive specifications
        return {
            'layout_system': self._generate_layout_specs(style_vector, semantic_analysis),
            'typography_system': self._generate_typography_specs(brand_tokens, semantic_analysis),
            'color_system': self._generate_color_specs(style_vector, brand_tokens),
            'component_library': self._generate_component_specs(style_vector, semantic_analysis),
            'interaction_patterns': self._generate_interaction_specs(semantic_analysis),
            'responsive_strategy': self._generate_responsive_specs(style_vector),
            'accessibility_guidelines': self._generate_accessibility_specs(style_vector),
            'print_specifications': self._generate_print_specs(style_vector, brand_tokens)
        }
    
    def _analyze_brand_alignment(self, semantic_analysis: Dict, style_vector: Dict, brand_context: BrandContext = None) -> Dict:
        """Analyze alignment with brand context"""
        context = brand_context or self.brand_context
        if not context or not context.company_name:
            return {'score': 0.5, 'note': 'No brand context provided'}
        
        # Calculate alignment scores
        archetype_alignment = self._calculate_archetype_alignment(semantic_analysis)
        values_alignment = self._calculate_values_alignment(semantic_analysis)
        audience_alignment = self._calculate_audience_alignment(semantic_analysis)
        
        overall_score = (archetype_alignment + values_alignment + audience_alignment) / 3
        
        return {
            'overall_score': overall_score,
            'archetype_alignment': archetype_alignment,
            'values_alignment': values_alignment,
            'audience_alignment': audience_alignment,
            'recommendations': self._generate_alignment_recommendations(overall_score),
            'brand_consistency': self._assess_brand_consistency(style_vector)
        }
    
    def _generate_implementation_specs(self, style_analysis: Dict, design_specs: Dict) -> Dict:
        """Generate implementation-ready specifications"""
        return {
            'css_variables': self._generate_css_variables(style_analysis),
            'design_tokens': self._generate_design_tokens(style_analysis, design_specs),
            'component_code': self._generate_component_templates(design_specs),
            'style_guide': self._generate_style_guide(style_analysis, design_specs),
            'brand_assets': self._generate_brand_assets(style_analysis)
        }
    
    def _analyze_cultural_context(self, semantic_analysis: Dict, style_vector: Dict) -> Dict:
        """Analyze cultural context and trends"""
        return {
            'cultural_signals': self._identify_cultural_signals(semantic_analysis),
            'trend_alignment': self._assess_trend_alignment(style_vector),
            'market_positioning': self._analyze_market_position(semantic_analysis),
            'demographic_appeal': self._assess_demographic_appeal(semantic_analysis),
            'global_readiness': self._assess_global_readiness(semantic_analysis)
        }
    
    def _calculate_intelligence_score(self, semantic_analysis: Dict, brand_alignment: Dict) -> float:
        """Calculate overall intelligence score"""
        factors = [
            len(semantic_analysis.get('emotional_signals', [])) / 10,  # Emotional depth
            len(semantic_analysis.get('concept_mapping', [])) / 8,     # Concept richness
            brand_alignment.get('overall_score', 0.5),                # Brand alignment
            1.0 if semantic_analysis.get('meaning_extraction') else 0.5  # Meaning extraction
        ]
        return min(np.mean(factors), 1.0)
    
    # Helper methods for specification generation
    def _generate_layout_specs(self, style_vector: Dict, semantic_analysis: Dict) -> Dict:
        density = style_vector.get('density', 0.5)
        
        if density < 0.3:
            return {
                'grid_system': '12-column',
                'spacing_scale': '16px base unit',
                'layout_style': 'minimal_grid',
                'content_width': '1200px max',
                'breakpoints': {'mobile': '768px', 'tablet': '1024px', 'desktop': '1200px'}
            }
        elif density > 0.7:
            return {
                'grid_system': '16-column',
                'spacing_scale': '4px base unit',
                'layout_style': 'dense_grid',
                'content_width': '1400px max',
                'breakpoints': {'mobile': '768px', 'tablet': '1024px', 'desktop': '1400px'}
            }
        else:
            return {
                'grid_system': '12-column',
                'spacing_scale': '8px base unit',
                'layout_style': 'balanced_grid',
                'content_width': '1200px max',
                'breakpoints': {'mobile': '768px', 'tablet': '1024px', 'desktop': '1200px'}
            }
    
    def _generate_css_variables(self, style_analysis: Dict) -> Dict:
        """Generate CSS custom properties"""
        brand_tokens = style_analysis.get('brand_tokens', {})
        style_vector = style_analysis.get('style_vector', {})
        
        return {
            '--primary-color': brand_tokens.get('primary_color', '#667eea'),
            '--secondary-color': brand_tokens.get('secondary_color', '#764ba2'),
            '--font-family-primary': f"{brand_tokens.get('font_class', 'sans-serif')}, system-ui",
            '--spacing-unit': brand_tokens.get('spacing_unit', '8px'),
            '--border-radius': f"{int(style_vector.get('era', 0.5) * 16)}px",
            '--shadow-elevation': f"0 {int(style_vector.get('sophistication', 0.5) * 8)}px {int(style_vector.get('sophistication', 0.5) * 24)}px rgba(0,0,0,0.1)"
        }
    
    # Placeholder methods for complex analysis (would need more sophisticated implementation)
    def _categorize_format(self, width: int, height: int) -> str:
        aspect_ratio = width / height
        if aspect_ratio > 1.5:
            return 'landscape'
        elif aspect_ratio < 0.7:
            return 'portrait'
        else:
            return 'square'
    
    def _analyze_visual_weight(self, img: Image) -> str:
        # Simplified visual weight analysis
        return 'balanced'
    
    def _extract_story_elements(self, description: str) -> List[str]:
        # Simplified story element extraction
        elements = []
        if 'person' in description.lower():
            elements.append('character')
        if any(word in description.lower() for word in ['setting', 'place', 'location']):
            elements.append('setting')
        return elements
    
    def _analyze_tone(self, description: str) -> str:
        # Simplified tone analysis
        if any(word in description.lower() for word in ['serious', 'formal', 'professional']):
            return 'formal'
        elif any(word in description.lower() for word in ['fun', 'playful', 'casual']):
            return 'casual'
        else:
            return 'neutral'
    
    def _analyze_perspective(self, description: str) -> str:
        return 'third_person'  # Simplified
    
    def _extract_temporal_context(self, description: str) -> str:
        return 'present'  # Simplified
    
    def _identify_primary_message(self, description: str, concepts: List[str]) -> str:
        if concepts:
            return f"Primary concept: {concepts[0]}"
        return "Visual communication"
    
    def _assess_story_alignment(self, concepts: List[str], emotions: List[str]) -> float:
        # Simplified alignment assessment
        return 0.7
    
    def _predict_audience_resonance(self, concepts: List[str], emotions: List[str]) -> float:
        # Simplified resonance prediction
        return 0.6
    
    # Additional placeholder methods would be implemented for full functionality
    def _generate_typography_specs(self, brand_tokens: Dict, semantic_analysis: Dict) -> Dict:
        return {
            'primary_font': brand_tokens.get('font_class', 'sans-serif'),
            'font_scale': '1.25 (Major Third)',
            'line_height': '1.5',
            'font_weights': [400, 600, 700]
        }
    
    def _generate_color_specs(self, style_vector: Dict, brand_tokens: Dict) -> Dict:
        return {
            'primary_palette': [brand_tokens.get('primary_color', '#667eea')],
            'secondary_palette': [brand_tokens.get('secondary_color', '#764ba2')],
            'neutral_palette': ['#f8f9fa', '#e9ecef', '#6c757d', '#495057'],
            'accessibility_ratios': 'WCAG AA compliant'
        }
    
    def _calculate_archetype_alignment(self, semantic_analysis: Dict) -> float:
        return 0.7  # Simplified
    
    def _calculate_values_alignment(self, semantic_analysis: Dict) -> float:
        return 0.6  # Simplified
    
    def _calculate_audience_alignment(self, semantic_analysis: Dict) -> float:
        return 0.8  # Simplified
    
    def _generate_alignment_recommendations(self, score: float) -> List[str]:
        if score > 0.8:
            return ["Excellent brand alignment", "Maintain current direction"]
        elif score > 0.6:
            return ["Good alignment with room for improvement", "Consider strengthening brand elements"]
        else:
            return ["Poor alignment", "Significant brand strategy revision needed"]
    
    def _assess_brand_consistency(self, style_vector: Dict) -> float:
        return 0.75  # Simplified
    
    def _generate_design_tokens(self, style_analysis: Dict, design_specs: Dict) -> Dict:
        return {
            'colors': self._generate_color_specs(style_analysis['style_vector'], style_analysis['brand_tokens']),
            'typography': self._generate_typography_specs(style_analysis['brand_tokens'], {}),
            'spacing': {'unit': style_analysis['brand_tokens'].get('spacing_unit', '8px')},
            'borders': {'radius': '4px', 'width': '1px'},
            'shadows': {'elevation': '0 2px 8px rgba(0,0,0,0.1)'}
        }
    
    def _generate_component_specs(self, style_vector: Dict, semantic_analysis: Dict) -> Dict:
        return {
            'buttons': {
                'primary': 'solid background, rounded corners',
                'secondary': 'outlined, transparent background',
                'sizes': ['small', 'medium', 'large']
            },
            'cards': {
                'elevation': 'subtle shadow',
                'padding': style_vector.get('density', 0.5) > 0.5 and '12px' or '16px',
                'radius': '8px'
            }
        }
    
    def _generate_component_templates(self, design_specs: Dict) -> Dict:
        return {
            'button_css': """
            .btn {
                padding: var(--spacing-unit) calc(var(--spacing-unit) * 2);
                border-radius: var(--border-radius);
                border: none;
                font-family: var(--font-family-primary);
                cursor: pointer;
            }
            """,
            'card_css': """
            .card {
                background: white;
                border-radius: var(--border-radius);
                box-shadow: var(--shadow-elevation);
                padding: calc(var(--spacing-unit) * 2);
            }
            """
        }
    
    def _generate_style_guide(self, style_analysis: Dict, design_specs: Dict) -> Dict:
        return {
            'overview': 'Generated style guide based on image analysis',
            'color_usage': 'Primary color for actions, secondary for accents',
            'typography_hierarchy': 'Clear hierarchy with consistent spacing',
            'component_guidelines': 'Consistent padding and spacing throughout'
        }
    
    def _generate_brand_assets(self, style_analysis: Dict) -> Dict:
        return {
            'logo_variations': ['primary', 'monogram', 'wordmark'],
            'color_variations': ['full_color', 'monochrome', 'reversed'],
            'asset_formats': ['svg', 'png', 'pdf'],
            'usage_guidelines': 'Minimum size, clear space requirements'
        }
    
    def _identify_cultural_signals(self, semantic_analysis: Dict) -> List[str]:
        return semantic_analysis.get('symbol_detection', [])
    
    def _assess_trend_alignment(self, style_vector: Dict) -> Dict:
        era_score = style_vector.get('era', 0.5)
        return {
            'current_trends': era_score > 0.6,
            'timeless_appeal': 0.4 <= era_score <= 0.6,
            'trend_prediction': era_score > 0.8 and 'cutting_edge' or 'mainstream'
        }
    
    def _analyze_market_position(self, semantic_analysis: Dict) -> str:
        emotions = semantic_analysis.get('emotional_signals', [])
        if 'sophisticated' in emotions and 'refined' in emotions:
            return 'premium'
        elif 'playful' in emotions or 'casual' in emotions:
            return 'accessible'
        else:
            return 'mainstream'
    
    def _assess_demographic_appeal(self, semantic_analysis: Dict) -> Dict:
        return {
            'primary_demographic': 'adults_25_45',
            'secondary_demographic': 'professionals',
            'appeal_factors': semantic_analysis.get('emotional_signals', [])
        }
    
    def _assess_global_readiness(self, semantic_analysis: Dict) -> float:
        # Simplified global readiness assessment
        return 0.8
    
    def _generate_interaction_specs(self, semantic_analysis: Dict) -> Dict:
        """Generate interaction pattern specifications"""
        emotions = semantic_analysis.get('emotional_signals', [])
        concepts = semantic_analysis.get('concept_mapping', [])
        
        # Determine interaction style based on emotional context
        if 'playful' in emotions:
            interaction_style = 'dynamic'
        elif 'sophisticated' in emotions:
            interaction_style = 'subtle'
        else:
            interaction_style = 'standard'
        
        return {
            'interaction_style': interaction_style,
            'animation_preferences': {
                'easing': 'ease-in-out' if 'smooth' in concepts else 'linear',
                'duration': '0.3s' if 'quick' in concepts else '0.5s',
                'hover_effects': True
            },
            'feedback_patterns': {
                'visual_feedback': True,
                'micro_interactions': 'sophisticated' in emotions,
                'loading_states': 'minimal' if 'clean' in concepts else 'detailed'
            }
        }
    
    def _generate_responsive_specs(self, style_vector: Dict) -> Dict:
        """Generate responsive design specifications"""
        density = style_vector.get('density', 0.5)
        
        return {
            'breakpoint_strategy': 'mobile_first' if density < 0.4 else 'desktop_first',
            'scaling_approach': 'fluid' if density < 0.6 else 'fixed',
            'content_adaptation': {
                'mobile': 'simplified' if density > 0.7 else 'full_featured',
                'tablet': 'adapted',
                'desktop': 'full_featured'
            }
        }
    
    def _generate_accessibility_specs(self, style_vector: Dict) -> Dict:
        """Generate accessibility guidelines"""
        sophistication = style_vector.get('sophistication', 0.5)
        
        return {
            'color_contrast_ratio': '4.5:1' if sophistication > 0.7 else '3:1',
            'font_size_minimum': '16px',
            'keyboard_navigation': True,
            'aria_labels': sophistication > 0.6,
            'screen_reader_optimization': True
        }
    
    def _generate_print_specs(self, style_vector: Dict, brand_tokens: Dict) -> Dict:
        """Generate print design specifications"""
        temperature = style_vector.get('temperature', 0.5)
        
        return {
            'color_profile': 'CMYK',
            'resolution': '300dpi',
            'paper_recommendations': {
                'finish': 'matte' if temperature < 0.5 else 'glossy',
                'weight': '120gsm' if temperature > 0.7 else '80gsm'
            },
            'bleed_requirements': '3mm',
            'color_adjustments': 'increase_warmth' if temperature > 0.6 else 'neutral'
        }


# Integration function for existing system
def analyze_brand_intelligence(image_path: str, description: str = "", 
                             brand_context: Optional[BrandContext] = None,
                             existing_analysis: Dict = None) -> Dict:
    """
    Analyze image with advanced brand intelligence
    Integration function for content_manager.py
    """
    try:
        engine = BrandIntelligenceEngine(brand_context)
        return engine.analyze_comprehensive(image_path, description, existing_analysis)
    except Exception as e:
        print(f"Error in brand intelligence analysis: {e}")
        return existing_analysis or {}


# Example usage and configuration
if __name__ == "__main__":
    import sys
    
    # Example brand context
    brand_context = BrandContext(
        company_name="TechCorp",
        industry="Technology",
        target_audience="Tech professionals, 25-45",
        brand_values=["Innovation", "Trust", "Simplicity"],
        brand_archetype="Sage",
        brand_personality=["Professional", "Reliable", "Forward-thinking"]
    )
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        description = sys.argv[2] if len(sys.argv) > 2 else ""
        
        print(f"\n🧠 Advanced Brand Intelligence Analysis")
        print(f"📁 Image: {image_path}")
        print(f"📝 Description: {description}")
        print("=" * 50)
        
        result = analyze_brand_intelligence(image_path, description, brand_context)
        
        if result:
            print(f"\n🎯 Intelligence Score: {result.get('intelligence_score', 0):.2f}")
            print(f"🎨 Brand Alignment: {result.get('brand_alignment', {}).get('overall_score', 0):.2f}")
            
            semantic = result.get('semantic_analysis', {})
            print(f"\n🧭 Semantic Analysis:")
            print(f"   Emotions: {semantic.get('emotional_signals', [])}")
            print(f"   Concepts: {semantic.get('concept_mapping', [])}")
            
            specs = result.get('design_specifications', {})
            print(f"\n📐 Design Specifications:")
            print(f"   Layout: {specs.get('layout_system', {}).get('grid_system', 'N/A')}")
            print(f"   Typography: {specs.get('typography_system', {}).get('primary_font', 'N/A')}")
            
            # Save detailed results
            with open('brand_intelligence_analysis.json', 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n💾 Detailed results saved to brand_intelligence_analysis.json")
        else:
            print("❌ Analysis failed")
    else:
        print("Usage: python brand_intelligence.py <image_path> [description]")