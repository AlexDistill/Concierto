#!/usr/bin/env python3
"""
Brand Synthesis Engine for Concierto

Creates complete brand systems by mixing style vectors from selected images
and applying design constraints and accessibility standards.
"""

import json
import uuid
import colorsys
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

try:
    from style_vector import StyleVector, analyze_style_vector
    STYLE_VECTOR_AVAILABLE = True
except ImportError:
    print("⚠️ StyleVector not available - synthesis engine will have limited functionality")
    STYLE_VECTOR_AVAILABLE = False


class BrandSynthesizer:
    """
    Generates complete brand systems from selected images using style vector analysis.
    
    Takes style vectors from multiple images, mixes them according to weights,
    and generates a comprehensive brand specification including colors, typography,
    spacing, and personality guidelines while ensuring accessibility compliance.
    """
    
    def __init__(self, data_file: str = "content/data.json"):
        self.data_file = Path(data_file)
        self._load_data()
    
    def _load_data(self):
        """Load content data from JSON file"""
        if self.data_file.exists():
            with open(self.data_file) as f:
                self.data = json.load(f)
        else:
            self.data = {"items": [], "brands": []}
    
    def synthesize(self, image_ids: List[str], brief: Optional[Dict] = None, weights: Optional[List[float]] = None) -> Dict:
        """
        Generate a complete brand specification from selected images.
        
        Args:
            image_ids: List of image IDs from data.json
            brief: Optional brand brief with name, category, audience, avoid_styles
            weights: Optional weights for each image (defaults to equal)
        
        Returns:
            Complete brand specification
        """
        # Get style vectors AND semantic data for selected images
        style_vectors = []
        source_items = []  # Store full items for semantic analysis
        for img_id in image_ids:
            item = self._get_item_by_id(img_id)
            if item and 'style_vector' in item:
                style_vectors.append(item['style_vector'])
                source_items.append(item)
        
        if not style_vectors:
            raise ValueError("No valid style vectors found for given image IDs")
        
        # Mix style vectors
        if weights is None:
            weights = [1.0 / len(style_vectors)] * len(style_vectors)
        
        mixed_vector = self._mix_style_vectors(style_vectors, weights)
        
        # Generate brand specification
        brand_spec = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat(),
            "name": brief.get('name', 'Untitled Brand') if brief else 'Untitled Brand',
            "brief": brief or {},
            "source_images": image_ids,
            "weights": weights,
            "style_vector": mixed_vector,
            "source_items": source_items  # Include full source items for semantic data
        }
        
        # Extract and synthesize insights from source items
        brand_spec["synthesized_insights"] = self._synthesize_insights(source_items, weights)
        
        # Generate color palette
        brand_spec["colors"] = self._generate_color_palette(mixed_vector, brief)
        
        # Generate typography suggestions
        brand_spec["typography"] = self._generate_typography(mixed_vector, brief)
        
        # Generate spacing system
        brand_spec["spacing"] = self._generate_spacing_system(mixed_vector)
        
        # Generate brand personality - now enhanced with insights
        brand_spec["personality"] = self._generate_personality(mixed_vector, brief, source_items)
        
        # Validate accessibility
        accessibility = self.validate_accessibility(brand_spec)
        brand_spec["accessibility"] = accessibility
        
        return brand_spec
    
    def _get_item_by_id(self, item_id: str) -> Optional[Dict]:
        """Find item in data by ID"""
        for item in self.data.get('items', []):
            if item.get('id') == item_id:
                return item
        return None
    
    def _mix_style_vectors(self, vectors: List[Dict], weights: List[float]) -> Dict:
        """Mix multiple style vectors using weighted averages"""
        if not STYLE_VECTOR_AVAILABLE:
            # Fallback: simple averaging of numeric values
            return self._simple_mix(vectors, weights)
        
        # Use StyleVector.mix if available
        try:
            # Ensure vectors are dictionaries
            clean_vectors = []
            for v in vectors:
                if isinstance(v, dict):
                    clean_vectors.append(v)
                else:
                    print(f"Warning: Invalid vector type {type(v)}, skipping")
                    continue
            
            if not clean_vectors:
                return self._simple_mix(vectors, weights)
                
            style_vector_objects = [StyleVector(**v) for v in clean_vectors]
            mixed = StyleVector.mix(style_vector_objects, weights)
            return mixed.__dict__
        except Exception as e:
            print(f"StyleVector mixing failed: {e}")
            # Fallback to simple mixing
            return self._simple_mix(vectors, weights)
    
    def _simple_mix(self, vectors: List[Dict], weights: List[float]) -> Dict:
        """Simple mixing for when StyleVector is not available"""
        mixed = {}
        
        # Mix numeric properties
        numeric_props = ['energy', 'sophistication', 'temperature', 'era', 'openness']
        for prop in numeric_props:
            values = [v.get(prop, 0.5) for v in vectors]
            mixed[prop] = sum(val * weight for val, weight in zip(values, weights))
        
        # Mix color lists
        all_colors = []
        for vector, weight in zip(vectors, weights):
            colors = vector.get('dominant_colors', [])
            # Weight colors by repeating them
            for color in colors:
                all_colors.extend([color] * int(weight * 10))
        
        # Remove duplicates and limit to reasonable number
        unique_colors = list(dict.fromkeys(all_colors))  # Preserve order, remove dupes
        mixed['dominant_colors'] = unique_colors[:8]  # Limit to 8 colors
        
        return mixed
    
    def _synthesize_insights(self, source_items: List[Dict], weights: List[float]) -> Dict:
        """Synthesize insights from source items' semantic analysis and AI insights"""
        import random
        
        # Collect all insights
        all_keywords = []
        all_descriptions = []
        all_creative_insights = []
        color_meanings = []
        visual_properties = {
            'brightness': [],
            'contrast': [],
            'saturation': []
        }
        
        for item, weight in zip(source_items, weights):
            # Get semantic analysis data
            semantic = item.get('semantic_analysis', {})
            if semantic and 'error' not in semantic:
                # Extract keywords
                keywords = semantic.get('description_keywords', [])
                all_keywords.extend(keywords * int(weight * 3))  # Weight the keywords
                
                # Extract visual properties
                props = semantic.get('visual_properties', {})
                if props:
                    visual_properties['brightness'].append(props.get('brightness', 0.5) * weight)
                    visual_properties['contrast'].append(props.get('contrast', 0.5) * weight)
                    visual_properties['saturation'].append(props.get('saturation', 0.5) * weight)
                
                # Extract color information
                colors = semantic.get('colors', {})
                if colors and 'most_common' in colors:
                    for color in colors['most_common'][:3]:
                        # Interpret color meanings
                        hue = color.get('hue', 0)
                        sat = color.get('saturation', 0)
                        bright = color.get('brightness', 0)
                        
                        if 0 <= hue <= 30 or hue >= 330:  # Reds
                            color_meanings.append('passionate' if sat > 0.5 else 'warm')
                        elif 30 < hue <= 60:  # Oranges
                            color_meanings.append('energetic' if bright > 0.5 else 'earthy')
                        elif 60 < hue <= 150:  # Greens
                            color_meanings.append('natural' if sat > 0.3 else 'calming')
                        elif 150 < hue <= 250:  # Blues
                            color_meanings.append('trustworthy' if bright > 0.5 else 'sophisticated')
                        elif 250 < hue <= 330:  # Purples
                            color_meanings.append('creative' if sat > 0.5 else 'luxurious')
            
            # Get AI creative insights
            creative = item.get('creative_insights', '')
            if creative:
                all_creative_insights.append(creative)
            
            # Get descriptions
            desc = item.get('description', '')
            if desc:
                all_descriptions.append(desc)
        
        # Calculate average visual properties
        avg_brightness = sum(visual_properties['brightness']) if visual_properties['brightness'] else 0.5
        avg_contrast = sum(visual_properties['contrast']) if visual_properties['contrast'] else 0.5
        avg_saturation = sum(visual_properties['saturation']) if visual_properties['saturation'] else 0.5
        
        # Get most common keywords (weighted)
        from collections import Counter
        keyword_counts = Counter(all_keywords)
        top_keywords = [kw for kw, _ in keyword_counts.most_common(10)]
        
        # Get most common color meanings
        color_meaning_counts = Counter(color_meanings)
        top_color_meanings = [meaning for meaning, _ in color_meaning_counts.most_common(5)]
        
        return {
            'keywords': top_keywords,
            'color_meanings': top_color_meanings,
            'visual_tone': {
                'brightness': 'bright' if avg_brightness > 0.6 else 'dark' if avg_brightness < 0.4 else 'balanced',
                'contrast': 'high-contrast' if avg_contrast > 0.6 else 'low-contrast' if avg_contrast < 0.4 else 'moderate',
                'saturation': 'vibrant' if avg_saturation > 0.6 else 'muted' if avg_saturation < 0.4 else 'balanced'
            },
            'creative_insights': all_creative_insights,
            'descriptions': all_descriptions
        }
    
    def _generate_color_palette(self, vector: Dict, brief: Optional[Dict]) -> Dict:
        """Generate accessible color palette from style vector"""
        colors = vector.get('dominant_colors', [])
        
        if len(colors) < 5:
            # Generate additional colors if needed
            colors = self._expand_color_palette(colors)
        
        # Sort by brightness for better organization
        colors_with_brightness = [(c, self._get_brightness(c)) for c in colors]
        colors_with_brightness.sort(key=lambda x: x[1], reverse=True)
        
        # Select colors for different roles
        palette = {
            "primary": colors_with_brightness[0][0] if colors_with_brightness else "#2563eb",
            "secondary": colors_with_brightness[1][0] if len(colors_with_brightness) > 1 else "#64748b",
            "accent": colors_with_brightness[2][0] if len(colors_with_brightness) > 2 else "#f59e0b",
            "neutral_dark": "#1f2937",
            "neutral_light": "#f9fafb"
        }
        
        # Ensure accessibility
        palette = self._ensure_accessible_colors(palette)
        
        # Apply brief constraints
        if brief and 'avoid_styles' in brief:
            palette = self._apply_style_constraints(palette, brief['avoid_styles'])
        
        return palette
    
    def _expand_color_palette(self, colors: List[str]) -> List[str]:
        """Generate additional colors if we don't have enough"""
        if not colors:
            return ["#2563eb", "#64748b", "#f59e0b", "#1f2937", "#f9fafb"]
        
        expanded = colors.copy()
        base_color = colors[0]
        
        # Generate variations of the base color
        h, s, v = self._hex_to_hsv(base_color)
        
        # Add lighter and darker versions
        expanded.append(self._hsv_to_hex(h, s * 0.6, min(v * 1.2, 1.0)))  # Lighter
        expanded.append(self._hsv_to_hex(h, s * 1.2, v * 0.8))  # Darker
        
        # Add complementary color
        comp_h = (h + 180) % 360
        expanded.append(self._hsv_to_hex(comp_h, s, v))
        
        return expanded[:8]  # Limit to 8 colors
    
    def _generate_typography(self, vector: Dict, brief: Optional[Dict]) -> Dict:
        """Generate typography suggestions based on style vector"""
        sophistication = vector.get('sophistication', 0.5)
        energy = vector.get('energy', 0.5)
        era = vector.get('era', 0.5)
        
        # Select fonts based on style characteristics
        if sophistication > 0.7:
            if era > 0.6:
                heading_family = "Inter, system-ui, sans-serif"
                body_family = "Inter, system-ui, sans-serif"
            else:
                heading_family = "Playfair Display, serif"
                body_family = "Source Serif Pro, serif"
        elif energy > 0.7:
            heading_family = "Montserrat, sans-serif"
            body_family = "Open Sans, sans-serif"
        else:
            heading_family = "Source Sans Pro, sans-serif"
            body_family = "Source Sans Pro, sans-serif"
        
        # Determine weights based on energy and sophistication
        heading_weight = "700" if energy > 0.6 else "600" if sophistication > 0.6 else "500"
        body_weight = "400"
        
        return {
            "heading": {
                "family": heading_family,
                "weight": heading_weight
            },
            "body": {
                "family": body_family,
                "weight": body_weight
            }
        }
    
    def _generate_spacing_system(self, vector: Dict) -> Dict:
        """Generate spacing system based on style characteristics"""
        energy = vector.get('energy', 0.5)
        sophistication = vector.get('sophistication', 0.5)
        
        # Base unit depends on energy and sophistication
        if energy > 0.7:
            base_unit = 4  # Tighter spacing for energetic brands
            scale = [0.5, 1, 1.25, 2, 3, 5, 8, 13]  # Fibonacci-like
        elif sophistication > 0.7:
            base_unit = 8  # More generous spacing
            scale = [0.5, 1, 1.5, 2, 3, 5, 8]  # Golden ratio inspired
        else:
            base_unit = 6  # Balanced
            scale = [0.5, 1, 1.5, 2, 3, 4]  # Compact
        
        return {
            "unit": f"{base_unit}px",
            "scale": scale,
            "grid": base_unit * 2  # Grid unit for layouts
        }
    
    def _generate_personality(self, vector: Dict, brief: Optional[Dict], source_items: List[Dict] = None) -> Dict:
        """Generate brand personality traits enhanced with semantic insights"""
        import random
        
        energy = vector.get('energy', 0.5)
        sophistication = vector.get('sophistication', 0.5)
        temperature = vector.get('temperature', 0.5)
        era = vector.get('era', 0.5)
        openness = vector.get('openness', 0.5)
        
        # Get synthesized insights if available
        insights = None
        if source_items:
            weights = [1.0 / len(source_items)] * len(source_items)
            insights = self._synthesize_insights(source_items, weights)
        
        # Generate traits based on metrics with much more variety
        traits = []
        
        # Add traits from semantic insights first (if available)
        if insights:
            # Add traits based on color meanings
            color_meanings = insights.get('color_meanings', [])
            if color_meanings:
                traits.extend(color_meanings[:2])  # Add top 2 color-based traits
            
            # Add traits based on visual tone
            visual_tone = insights.get('visual_tone', {})
            if visual_tone.get('saturation') == 'vibrant':
                traits.append(random.choice(['bold', 'expressive', 'vivid']))
            elif visual_tone.get('saturation') == 'muted':
                traits.append(random.choice(['subtle', 'understated', 'refined']))
            
            if visual_tone.get('brightness') == 'bright':
                traits.append(random.choice(['optimistic', 'uplifting', 'radiant']))
            elif visual_tone.get('brightness') == 'dark':
                traits.append(random.choice(['mysterious', 'dramatic', 'profound']))
            
            # Add traits from keywords if they suggest personality
            keywords = insights.get('keywords', [])
            personality_keywords = {
                'minimal': 'minimalist', 'simple': 'straightforward', 'complex': 'sophisticated',
                'organic': 'natural', 'geometric': 'structured', 'flowing': 'fluid',
                'sharp': 'precise', 'soft': 'gentle', 'bold': 'confident'
            }
            for kw in keywords[:5]:
                if kw.lower() in personality_keywords:
                    traits.append(personality_keywords[kw.lower()])
        
        # Energy-based traits
        if energy > 0.8:
            traits.extend(random.sample(['dynamic', 'bold', 'energetic', 'vibrant', 'spirited', 'passionate', 'electric', 'kinetic'], 3))
        elif energy > 0.6:
            traits.extend(random.sample(['active', 'lively', 'engaging', 'animated', 'enthusiastic', 'vivacious'], 2))
        elif energy > 0.4:
            traits.extend(random.sample(['balanced', 'steady', 'measured', 'consistent', 'stable', 'grounded'], 2))
        elif energy > 0.2:
            traits.extend(random.sample(['calm', 'composed', 'relaxed', 'peaceful', 'tranquil', 'serene'], 2))
        else:
            traits.extend(random.sample(['contemplative', 'meditative', 'quiet', 'still', 'restful', 'gentle'], 2))
        
        # Sophistication-based traits
        if sophistication > 0.8:
            traits.extend(random.sample(['luxurious', 'exclusive', 'distinguished', 'prestigious', 'exquisite', 'opulent'], 2))
        elif sophistication > 0.6:
            traits.extend(random.sample(['refined', 'elegant', 'polished', 'cultured', 'sophisticated', 'tasteful'], 2))
        elif sophistication > 0.4:
            traits.extend(random.sample(['professional', 'competent', 'capable', 'practical', 'sensible'], 2))
        elif sophistication > 0.2:
            traits.extend(random.sample(['approachable', 'friendly', 'welcoming', 'inclusive', 'accessible'], 2))
        else:
            traits.extend(random.sample(['casual', 'relaxed', 'informal', 'easygoing', 'laid-back', 'unpretentious'], 2))
        
        # Temperature-based traits
        if temperature > 0.7:
            traits.extend(random.sample(['warm', 'inviting', 'nurturing', 'compassionate', 'embracing'], 1))
        elif temperature < 0.3:
            traits.extend(random.sample(['cool', 'crisp', 'precise', 'analytical', 'rational'], 1))
        
        # Era-based traits
        if era > 0.8:
            traits.extend(random.sample(['futuristic', 'cutting-edge', 'pioneering', 'next-gen', 'revolutionary'], 1))
        elif era > 0.6:
            traits.extend(random.sample(['modern', 'contemporary', 'current', 'progressive', 'forward-thinking'], 1))
        elif era > 0.4:
            traits.extend(random.sample(['timeless', 'enduring', 'lasting', 'perennial'], 1))
        elif era > 0.2:
            traits.extend(random.sample(['established', 'proven', 'trusted', 'reliable'], 1))
        else:
            traits.extend(random.sample(['classic', 'traditional', 'heritage', 'vintage', 'retro', 'nostalgic'], 1))
        
        # Openness-based traits (if available)
        if openness > 0.7:
            traits.extend(random.sample(['innovative', 'creative', 'imaginative', 'visionary', 'experimental'], 1))
        elif openness < 0.3:
            traits.extend(random.sample(['practical', 'straightforward', 'no-nonsense', 'direct'], 1))
        
        # Generate more varied voice guidelines
        voice_options = []
        
        # Build voice based on multiple factors
        if sophistication > 0.7 and energy > 0.6:
            voice_options = [
                "Confident and articulate, with measured enthusiasm",
                "Polished yet dynamic, balancing expertise with energy",
                "Authoritative and engaging, commanding attention respectfully"
            ]
        elif sophistication > 0.7 and energy < 0.4:
            voice_options = [
                "Thoughtful and eloquent, every word carefully chosen",
                "Quietly confident, letting expertise speak for itself",
                "Refined and contemplative, with depth and nuance"
            ]
        elif sophistication > 0.6 and temperature > 0.6:
            voice_options = [
                "Professional yet personable, building genuine connections",
                "Knowledgeable and approachable, expertise without intimidation",
                "Competent and caring, balancing skill with empathy"
            ]
        elif sophistication < 0.4 and energy > 0.6:
            voice_options = [
                "Bold and direct, cutting through the noise",
                "Energetic and accessible, speaking everyone's language",
                "Enthusiastic and unpretentious, keeping it real"
            ]
        elif sophistication < 0.4 and temperature > 0.6:
            voice_options = [
                "Warm and conversational, like talking with a friend",
                "Friendly and informal, creating comfortable connections",
                "Genuine and relatable, down-to-earth and authentic"
            ]
        elif energy > 0.7:
            voice_options = [
                "Dynamic and inspiring, igniting passion and action",
                "Vibrant and motivating, pushing boundaries forward",
                "Electric and compelling, impossible to ignore"
            ]
        elif energy < 0.3:
            voice_options = [
                "Calm and reassuring, a steady presence in chaos",
                "Peaceful and grounding, bringing clarity through stillness",
                "Gentle yet confident, soft power at its best"
            ]
        elif temperature < 0.3:
            voice_options = [
                "Precise and analytical, data-driven decision making",
                "Clear and logical, letting facts lead the way",
                "Crisp and efficient, maximum impact with minimum words"
            ]
        else:
            voice_options = [
                "Balanced and versatile, adapting to every situation",
                "Clear and consistent, reliable in every interaction",
                "Steady and trustworthy, the voice you can count on"
            ]
        
        voice = random.choice(voice_options) if voice_options else "Authentic and engaging, true to our values"
        
        # Enhance voice with insights if available
        if insights and insights.get('creative_insights'):
            # Extract tone words from creative insights
            creative_text = ' '.join(insights['creative_insights']).lower()
            
            # Look for tone indicators in the creative insights
            if any(word in creative_text for word in ['professional', 'corporate', 'business']):
                voice = voice.replace('engaging', 'professional')
            if any(word in creative_text for word in ['playful', 'fun', 'whimsical']):
                voice = voice.replace('professional', 'playful').replace('refined', 'spirited')
            if any(word in creative_text for word in ['luxury', 'premium', 'exclusive']):
                voice = voice.replace('friendly', 'exclusive').replace('casual', 'premium')
        
        # Generate contextual do's and don'ts based on the complete personality profile
        dos = []
        donts = []
        
        # Add insights-based guidelines if available
        if insights:
            # Based on visual tone
            visual_tone = insights.get('visual_tone', {})
            if visual_tone.get('brightness') == 'bright':
                dos.append(random.choice([
                    "Use bright, optimistic imagery that energizes",
                    "Favor light backgrounds and open spaces",
                    "Embrace white space as a design element"
                ]))
            elif visual_tone.get('brightness') == 'dark':
                dos.append(random.choice([
                    "Use dramatic lighting and deep shadows",
                    "Create depth with rich, dark backgrounds",
                    "Emphasize contrast for visual impact"
                ]))
            
            # Based on keywords
            keywords = insights.get('keywords', [])
            keyword_str = ' '.join(keywords).lower()
            if 'minimal' in keyword_str or 'simple' in keyword_str:
                dos.append("Strip away unnecessary elements")
                donts.append("Avoid visual clutter or decoration")
            if 'organic' in keyword_str or 'natural' in keyword_str:
                dos.append("Use organic shapes and natural textures")
                donts.append("Avoid harsh geometric patterns")
            if 'tech' in keyword_str or 'digital' in keyword_str:
                dos.append("Embrace digital-first design principles")
                donts.append("Don't rely on print-era conventions")
        
        # Based on sophistication level  
        if sophistication > 0.7:
            dos.extend(random.sample([
                "Choose quality over quantity in all decisions",
                "Curate experiences with intention and purpose",
                "Invest in premium materials and craftsmanship",
                "Present information with elegant restraint",
                "Focus on subtlety and understated luxury"
            ], 2))
            donts.extend(random.sample([
                "Never dilute the brand with discount messaging",
                "Avoid loud or attention-seeking tactics",
                "Don't compromise craftsmanship for speed",
                "Never use cheap materials or finishes",
                "Avoid overcommunicating or overselling"
            ], 2))
        elif sophistication < 0.4:
            dos.extend(random.sample([
                "Keep designs approachable and friendly",
                "Use familiar visual metaphors and icons",
                "Make interfaces intuitive and easy to navigate",
                "Focus on functionality over form",
                "Use warm, welcoming photography"
            ], 2))
            donts.extend(random.sample([
                "Don't intimidate with complex layouts",
                "Avoid pretentious design flourishes",
                "Never sacrifice usability for aesthetics",
                "Don't create barriers with exclusive design",
                "Avoid cold or sterile visual presentation"
            ], 2))
        
        # Based on energy level
        if energy > 0.7:
            dos.extend(random.sample([
                "Use bold colors and strong contrasts",
                "Create dynamic layouts with movement",
                "Employ active, energetic photography",
                "Use exclamation points and action verbs",
                "Feature people in motion and activity"
            ], 2))
            donts.extend(random.sample([
                "Never use muted or passive color schemes",
                "Avoid static, symmetrical compositions",
                "Don't use contemplative or quiet imagery",
                "Never appear sluggish or hesitant",
                "Avoid overly formal presentations"
            ], 2))
        elif energy < 0.3:
            dos.extend(random.sample([
                "Use generous white space and breathing room",
                "Employ soft, muted color palettes",
                "Create zen-like, minimalist layouts",
                "Use contemplative, peaceful imagery",
                "Focus on single focal points"
            ], 2))
            donts.extend(random.sample([
                "Don't use busy or chaotic layouts",
                "Avoid bright, jarring color combinations",
                "Never rush the visual narrative",
                "Don't overcrowd with multiple messages",
                "Avoid aggressive or pushy design elements"
            ], 2))
        
        # Based on temperature
        if temperature > 0.7:
            dos.extend(random.sample([
                "Use warm color temperatures (reds, oranges, yellows)",
                "Feature authentic human faces and emotions",
                "Include community and group imagery",
                "Use soft, rounded shapes and forms",
                "Incorporate tactile, touchable textures"
            ], 1))
            donts.extend(random.sample([
                "Never use cold, clinical aesthetics",
                "Avoid isolated or lonely imagery",
                "Don't use harsh, angular designs",
                "Never appear distant or unapproachable"
            ], 1))
        elif temperature < 0.3:
            dos.extend(random.sample([
                "Use cool color temperatures (blues, grays)",
                "Employ clean, precise geometric shapes",
                "Focus on product features and specifications",
                "Use technical diagrams and infographics",
                "Maintain crisp, sharp edges and lines"
            ], 1))
            donts.extend(random.sample([
                "Don't overuse warm, emotional imagery",
                "Avoid overly casual or playful elements",
                "Never compromise precision for warmth"
            ], 1))
        
        # Based on era
        if era > 0.7:
            dos.extend(random.sample([
                "Use cutting-edge design trends and techniques",
                "Incorporate AR/VR and interactive elements",
                "Feature futuristic, forward-looking imagery",
                "Employ gradient meshes and 3D elements",
                "Use variable fonts and fluid typography"
            ], 1))
            donts.extend(random.sample([
                "Don't use dated design patterns",
                "Avoid skeuomorphic or web 2.0 aesthetics",
                "Never appear technologically behind"
            ], 1))
        elif era < 0.3:
            dos.extend(random.sample([
                "Use classic typography and timeless layouts",
                "Reference heritage and craftsmanship",
                "Employ vintage photography and illustrations",
                "Use traditional color combinations",
                "Honor established design principles"
            ], 1))
            donts.extend(random.sample([
                "Don't chase fleeting design trends",
                "Avoid ultra-modern aesthetics that clash",
                "Never abandon timeless design values"
            ], 1))
        
        # Add brief-specific constraints
        if brief and 'avoid_styles' in brief:
            for style in brief['avoid_styles']:
                donts.append(f"Avoid {style} aesthetic or approach")
        
        # Ensure variety and remove duplicates
        dos = list(dict.fromkeys(dos))[:5]  # Remove duplicates, limit to 5
        donts = list(dict.fromkeys(donts))[:5]  # Remove duplicates, limit to 5
        
        return {
            "traits": list(dict.fromkeys(traits))[:8],  # More unique traits
            "voice": voice,
            "do": dos,
            "dont": donts
        }
    
    def validate_accessibility(self, brand_spec: Dict) -> Dict:
        """
        Validate accessibility of brand specification
        
        Returns dict with:
        - passed: boolean
        - issues: list of problems
        - suggestions: list of improvements
        """
        issues = []
        suggestions = []
        
        colors = brand_spec.get('colors', {})
        
        # Check WCAG AA contrast ratios (4.5:1 for normal text)
        text_colors = [colors.get('neutral_dark', '#000')]
        bg_colors = [colors.get('neutral_light', '#fff'), colors.get('primary', '#000')]
        
        for text_color in text_colors:
            for bg_color in bg_colors:
                contrast = self._calculate_contrast_ratio(text_color, bg_color)
                if contrast < 4.5:
                    issues.append(f"Low contrast: {text_color} on {bg_color} ({contrast:.1f}:1)")
                    suggestions.append(f"Increase contrast between {text_color} and {bg_color}")
        
        # Check if colors work in grayscale
        grayscale_issues = self._check_grayscale_compatibility(colors)
        issues.extend(grayscale_issues)
        
        # Check color count
        if len(colors) > 5:
            issues.append(f"Too many colors ({len(colors)}), recommend 5 or fewer")
            suggestions.append("Reduce color palette to 5 colors maximum")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "contrast_ratios": self._get_all_contrast_ratios(colors)
        }
    
    def generate_alternatives(self, base_spec: Dict, count: int = 3) -> List[Dict]:
        """Generate alternative brand specifications"""
        alternatives = []
        
        for i in range(count):
            alt_spec = base_spec.copy()
            alt_spec["id"] = str(uuid.uuid4())
            alt_spec["name"] = f"{base_spec['name']} - Alternative {i+1}"
            
            # Shift style vector slightly
            style_vector = alt_spec["style_vector"].copy()
            style_vector = self._shift_style_vector(style_vector, variation=i+1)
            alt_spec["style_vector"] = style_vector
            
            # Regenerate derived properties
            alt_spec["colors"] = self._generate_color_palette(style_vector, base_spec.get('brief'))
            alt_spec["typography"] = self._generate_typography(style_vector, base_spec.get('brief'))
            alt_spec["spacing"] = self._generate_spacing_system(style_vector)
            alt_spec["personality"] = self._generate_personality(style_vector, base_spec.get('brief'))
            
            # Validate accessibility
            alt_spec["accessibility"] = self.validate_accessibility(alt_spec)
            
            alternatives.append(alt_spec)
        
        return alternatives
    
    def save_brand(self, brand_spec: Dict) -> None:
        """Save brand specification to data file"""
        if "brands" not in self.data:
            self.data["brands"] = []
        
        # Remove any existing brand with same ID
        self.data["brands"] = [b for b in self.data["brands"] if b.get("id") != brand_spec["id"]]
        
        # Add new brand
        self.data["brands"].append(brand_spec)
        
        # Save to file
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    # Helper methods for color operations
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _rgb_to_hex(self, r: int, g: int, b: int) -> str:
        """Convert RGB tuple to hex color"""
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _hex_to_hsv(self, hex_color: str) -> Tuple[float, float, float]:
        """Convert hex color to HSV tuple"""
        r, g, b = self._hex_to_rgb(hex_color)
        return colorsys.rgb_to_hsv(r/255, g/255, b/255)
    
    def _hsv_to_hex(self, h: float, s: float, v: float) -> str:
        """Convert HSV tuple to hex color"""
        r, g, b = colorsys.hsv_to_rgb(h/360, s, v)
        return self._rgb_to_hex(int(r*255), int(g*255), int(b*255))
    
    def _get_brightness(self, hex_color: str) -> float:
        """Get perceived brightness of a color (0-1)"""
        r, g, b = self._hex_to_rgb(hex_color)
        # Using relative luminance formula
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255
    
    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate WCAG contrast ratio between two colors"""
        def get_luminance(hex_color):
            r, g, b = self._hex_to_rgb(hex_color)
            # Convert to relative luminance
            for c in [r, g, b]:
                c = c / 255.0
                if c <= 0.03928:
                    c = c / 12.92
                else:
                    c = ((c + 0.055) / 1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        lum1 = get_luminance(color1)
        lum2 = get_luminance(color2)
        
        # Ensure lighter color is in numerator
        if lum1 < lum2:
            lum1, lum2 = lum2, lum1
        
        return (lum1 + 0.05) / (lum2 + 0.05)
    
    def _ensure_accessible_colors(self, palette: Dict) -> Dict:
        """Ensure color palette meets accessibility standards"""
        # Check and fix main text combinations
        dark = palette.get('neutral_dark', '#1f2937')
        light = palette.get('neutral_light', '#f9fafb')
        
        # Ensure sufficient contrast for text
        contrast = self._calculate_contrast_ratio(dark, light)
        if contrast < 4.5:
            # Darken the dark color or lighten the light color
            if self._get_brightness(dark) > 0.3:
                palette['neutral_dark'] = '#000000'
            if self._get_brightness(light) < 0.8:
                palette['neutral_light'] = '#ffffff'
        
        return palette
    
    def _check_grayscale_compatibility(self, colors: Dict) -> List[str]:
        """Check if colors are distinguishable in grayscale"""
        issues = []
        color_list = list(colors.values())
        
        # Convert to grayscale and check for similar values
        gray_values = []
        for color in color_list:
            brightness = self._get_brightness(color)
            gray_values.append((color, brightness))
        
        # Check for colors that are too similar in grayscale
        for i, (color1, bright1) in enumerate(gray_values):
            for j, (color2, bright2) in enumerate(gray_values[i+1:], i+1):
                if abs(bright1 - bright2) < 0.2:  # Too similar
                    issues.append(f"Colors {color1} and {color2} may be indistinguishable in grayscale")
        
        return issues
    
    def _get_all_contrast_ratios(self, colors: Dict) -> Dict:
        """Calculate contrast ratios for all color combinations"""
        ratios = {}
        color_items = list(colors.items())
        
        for i, (name1, color1) in enumerate(color_items):
            for name2, color2 in color_items[i+1:]:
                ratio = self._calculate_contrast_ratio(color1, color2)
                ratios[f"{name1}_vs_{name2}"] = round(ratio, 2)
        
        return ratios
    
    def _apply_style_constraints(self, palette: Dict, avoid_styles: List[str]) -> Dict:
        """Apply style constraints from brief"""
        # This is a placeholder for more sophisticated constraint application
        # Could modify colors based on avoided styles
        return palette
    
    def _shift_style_vector(self, vector: Dict, variation: int) -> Dict:
        """Create slight variations in style vector for alternatives"""
        shifted = vector.copy()
        
        # Apply small random shifts based on variation number
        import random
        random.seed(hash(str(vector)) + variation)  # Deterministic but varied
        
        shift_amount = 0.1 * variation  # Increase shift for each variation
        
        for key in ['energy', 'sophistication', 'temperature', 'era', 'openness']:
            if key in shifted:
                # Apply small shift while keeping in valid range
                shift = (random.random() - 0.5) * shift_amount
                shifted[key] = max(0, min(1, shifted[key] + shift))
        
        return shifted


if __name__ == "__main__":
    # Test the synthesizer
    synthesizer = BrandSynthesizer()
    
    # Create a test brand
    test_spec = synthesizer.synthesize(
        image_ids=["test_id"],
        brief={
            "name": "Test Brand",
            "category": "Technology",
            "audience": "Developers"
        }
    )
    
    print("Generated brand specification:")
    print(json.dumps(test_spec, indent=2))