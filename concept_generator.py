#!/usr/bin/env python3
"""
AI-powered concept generation for campaigns.
Analyzes mood board themes and generates visual concepts using OpenAI.
"""

import json
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class ConceptGenerator:
    """Generate creative concepts based on campaign briefs and mood boards"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.chat_url = "https://api.openai.com/v1/chat/completions"
        self.image_url = "https://api.openai.com/v1/images/generations"
    
    async def analyze_themes(self, campaign: Dict, mood_board_items: List[Dict]) -> Dict:
        """Analyze common themes across mood board items"""
        
        # Compile all the analysis data from mood board items
        themes_data = {
            'colors': [],
            'styles': [],
            'moods': [],
            'subjects': [],
            'techniques': [],
            'all_tags': [],
            'descriptions': []
        }
        
        for item in mood_board_items:
            # Collect AI tags and descriptions
            themes_data['all_tags'].extend(item.get('ai_tags', []))
            themes_data['all_tags'].extend(item.get('tags', []))
            if item.get('description'):
                themes_data['descriptions'].append(item['description'])
            
            # Extract from creative insights
            insights = item.get('creative_insights', '')
            if 'color' in insights.lower():
                # Extract color mentions
                for word in ['vibrant', 'monochrome', 'colorful', 'muted', 'bold', 'pastel', 'saturated']:
                    if word in insights.lower():
                        themes_data['colors'].append(word)
            
            # Extract style keywords
            for style in ['minimal', 'vintage', 'modern', 'retro', 'bohemian', 'eclectic', 'classic']:
                if style in str(item).lower():
                    themes_data['styles'].append(style)
        
        # Deduplicate and count frequencies
        theme_analysis = {
            'dominant_colors': self._get_top_items(themes_data['colors'], 3),
            'visual_styles': self._get_top_items(themes_data['styles'], 3),
            'common_tags': self._get_top_items(themes_data['all_tags'], 10),
            'mood': self._determine_overall_mood(themes_data['all_tags'])
        }
        
        # Use GPT to synthesize themes
        prompt = f"""
        Analyze these visual themes for a campaign:
        
        Campaign: {campaign['name']}
        Client: {campaign['client']}
        Objective: {campaign['objective']}
        Target Audience: {campaign.get('target_audience', 'General')}
        
        Mood Board Analysis:
        - Common Tags: {', '.join(theme_analysis['common_tags'])}
        - Visual Styles: {', '.join(theme_analysis['visual_styles'])}
        - Overall Mood: {theme_analysis['mood']}
        
        Image Descriptions:
        {' | '.join(themes_data['descriptions'][:3])}
        
        Provide a concise theme analysis with:
        1. Core visual themes (2-3 themes)
        2. Color palette recommendation
        3. Typography style suggestion
        4. Key visual elements to incorporate
        5. Overall creative direction
        
        Format as JSON with keys: themes, colors, typography, elements, direction
        """
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "response_format": {"type": "json_object"}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.chat_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        analysis = json.loads(result['choices'][0]['message']['content'])
                        return {**theme_analysis, **analysis}
                    else:
                        return theme_analysis
        except:
            return theme_analysis
    
    def _get_top_items(self, items: List[str], n: int) -> List[str]:
        """Get top N most frequent items"""
        from collections import Counter
        if not items:
            return []
        counter = Counter(items)
        return [item for item, _ in counter.most_common(n)]
    
    def _determine_overall_mood(self, tags: List[str]) -> str:
        """Determine overall mood from tags"""
        mood_keywords = {
            'energetic': ['vibrant', 'bold', 'dynamic', 'playful', 'energetic'],
            'calm': ['minimal', 'serene', 'calm', 'peaceful', 'soft'],
            'sophisticated': ['elegant', 'sophisticated', 'luxury', 'premium', 'refined'],
            'playful': ['fun', 'playful', 'whimsical', 'colorful', 'quirky'],
            'nostalgic': ['vintage', 'retro', 'nostalgic', 'classic', 'timeless']
        }
        
        mood_scores = {}
        for mood, keywords in mood_keywords.items():
            score = sum(1 for tag in tags if any(kw in tag.lower() for kw in keywords))
            if score > 0:
                mood_scores[mood] = score
        
        if mood_scores:
            return max(mood_scores, key=mood_scores.get)
        return 'balanced'
    
    async def generate_concepts(self, campaign: Dict, themes: Dict, num_concepts: int = 3) -> List[Dict]:
        """Generate creative concepts based on campaign brief and themes"""
        
        prompt = f"""
        Generate {num_concepts} unique creative concepts for this campaign:
        
        CAMPAIGN BRIEF:
        - Name: {campaign['name']}
        - Client: {campaign['client']}
        - Objective: {campaign['objective']}
        - Target Audience: {campaign.get('target_audience', 'General')}
        - Key Messages: {campaign.get('key_messages', 'Not specified')}
        - Tone & Voice: {campaign.get('tone_voice', 'Not specified')}
        - Deliverables: {campaign.get('deliverables', 'Various')}
        
        VISUAL THEMES ANALYSIS:
        - Core Themes: {themes.get('themes', 'Modern, clean')}
        - Color Palette: {themes.get('colors', 'Vibrant')}
        - Typography: {themes.get('typography', 'Bold, readable')}
        - Visual Elements: {themes.get('elements', 'Abstract shapes')}
        - Creative Direction: {themes.get('direction', 'Contemporary')}
        - Overall Mood: {themes.get('mood', 'Energetic')}
        
        For each concept, provide:
        1. Concept Name
        2. Visual Description (detailed, specific)
        3. Key Visual Elements
        4. Color Palette (specific colors)
        5. Typography Approach
        6. Layout/Composition Style
        7. Photography/Illustration Style
        8. Example Applications (social, web, print)
        9. Why This Works (connection to brief)
        
        Return as JSON array with these exact keys for each concept.
        Make each concept distinct and actionable.
        """
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 2000,
                "response_format": {"type": "json_object"}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.chat_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        concepts_data = json.loads(result['choices'][0]['message']['content'])
                        
                        # Ensure we have a list of concepts
                        if 'concepts' in concepts_data:
                            return concepts_data['concepts']
                        elif isinstance(concepts_data, list):
                            return concepts_data
                        else:
                            # Wrap single concept in list
                            return [concepts_data]
                    else:
                        error = await response.text()
                        print(f"Error generating concepts: {error}")
                        return []
        
        except Exception as e:
            print(f"Exception generating concepts: {e}")
            return []
    
    async def generate_visual(self, concept: Dict, size: str = "1024x1024") -> Dict:
        """Generate a visual mockup using DALL-E based on concept"""
        
        # Create detailed prompt from concept
        prompt = f"""
        Create a professional marketing visual:
        
        Style: {concept.get('Photography/Illustration Style', 'Modern photography')}
        Colors: {concept.get('Color Palette', 'Vibrant colors')}
        Composition: {concept.get('Layout/Composition Style', 'Dynamic layout')}
        Elements: {concept.get('Key Visual Elements', 'Abstract shapes')}
        Mood: {concept.get('Visual Description', 'Energetic and modern')}
        
        High quality, professional advertising imagery, commercial photography style.
        """
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "dall-e-3",
                "prompt": prompt[:4000],  # DALL-E has character limit
                "n": 1,
                "size": size,
                "quality": "standard",
                "style": "vivid"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.image_url, headers=headers, json=payload,
                                       timeout=aiohttp.ClientTimeout(total=60)) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            'success': True,
                            'image_url': result['data'][0]['url'],
                            'revised_prompt': result['data'][0].get('revised_prompt', prompt)
                        }
                    else:
                        error = await response.text()
                        return {
                            'success': False,
                            'error': f"DALL-E error: {error}"
                        }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to generate image: {str(e)}"
            }
    
    async def generate_campaign_concepts(self, campaign: Dict, mood_board_items: List[Dict]) -> Dict:
        """Complete concept generation pipeline"""
        
        print(f"🎨 Starting concept generation for: {campaign['name']}")
        
        # Step 1: Analyze themes
        print("  📊 Analyzing mood board themes...")
        themes = await self.analyze_themes(campaign, mood_board_items)
        
        # Step 2: Generate concepts
        print("  💡 Generating creative concepts...")
        concepts = await self.generate_concepts(campaign, themes)
        
        # Step 3: Generate visuals for top concept (optional)
        visuals = []
        if concepts and len(concepts) > 0:
            print("  🖼️ Generating visual mockup...")
            # Generate visual for first concept
            visual_result = await self.generate_visual(concepts[0])
            if visual_result['success']:
                visuals.append(visual_result)
        
        return {
            'campaign_id': campaign['id'],
            'campaign_name': campaign['name'],
            'theme_analysis': themes,
            'concepts': concepts,
            'visuals': visuals,
            'generated_at': datetime.now().isoformat()
        }


# Standalone test function
async def test_generator():
    """Test the concept generator with sample data"""
    import os
    
    # Load API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OpenAI API key found")
        return
    
    generator = ConceptGenerator(api_key)
    
    # Test campaign
    campaign = {
        'id': 'test_1',
        'name': 'Summer Beach Campaign',
        'client': 'BeachCo',
        'objective': 'Launch summer collection',
        'target_audience': '25-40 beach lovers'
    }
    
    # Test mood board items (would come from your database)
    mood_board = [
        {
            'ai_tags': ['beach', 'vibrant', 'summer', 'colorful'],
            'description': 'Bright beach scene with vibrant colors',
            'creative_insights': 'Uses bold, saturated colors to convey energy'
        }
    ]
    
    result = await generator.generate_campaign_concepts(campaign, mood_board)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(test_generator())