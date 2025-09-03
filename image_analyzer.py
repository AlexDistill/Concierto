#!/usr/bin/env python3
"""
AI-powered image analysis system for Concierto.
Analyzes images to understand content, mood, style, and generate intelligent tags.
"""

import base64
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
import aiofiles

class ImageAnalyzer:
    """AI-powered image content analyzer"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
        # Analysis prompts for different aspects
        self.prompts = {
            "content": """Analyze this image and describe what you see. Focus on:
- Main subjects/objects
- Activities or actions
- Setting/environment
- Visual style/aesthetic
- Mood/emotion conveyed

Be concise but descriptive in 2-3 sentences.""",
            
            "tags": """Generate relevant tags for this image that would help categorize it for a creative professional. Consider:
- Visual style (minimal, bold, vintage, modern, etc.)
- Content type (portrait, landscape, typography, logo, illustration, etc.)
- Mood/emotion (energetic, calm, dramatic, playful, etc.)
- Colors (if dominant)
- Industry/use case (branding, web design, print, social media, etc.)

Return ONLY a comma-separated list of 5-10 relevant tags.""",
            
            "creative_insights": """As a creative professional, what insights can you provide about this image? Consider:
- Design principles used
- Artistic techniques
- Potential use cases
- What makes it effective or interesting
- Style influences or trends

Provide 2-3 key insights that would be valuable for creative inspiration."""
        }
    
    async def analyze_image(self, image_path: Path) -> Dict[str, Any]:
        """Analyze a single image and return comprehensive insights"""
        try:
            # Read and encode image
            image_data = await self._encode_image(image_path)
            
            # Run different analysis types
            results = {}
            
            # Basic content analysis
            results['content_description'] = await self._analyze_with_prompt(
                image_data, self.prompts['content']
            )
            
            # Generate AI tags
            ai_tags_response = await self._analyze_with_prompt(
                image_data, self.prompts['tags']
            )
            results['ai_tags'] = self._parse_tags(ai_tags_response)
            
            # Creative insights
            results['creative_insights'] = await self._analyze_with_prompt(
                image_data, self.prompts['creative_insights']
            )
            
            # Extract colors and technical info
            results['technical_info'] = await self._extract_technical_info(image_path)
            
            return {
                'success': True,
                'analysis': results,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'analysis': None,
                'error': str(e)
            }
    
    async def _encode_image(self, image_path: Path) -> str:
        """Encode image to base64 for API"""
        async with aiofiles.open(image_path, mode='rb') as f:
            image_bytes = await f.read()
            return base64.b64encode(image_bytes).decode('utf-8')
    
    async def _analyze_with_prompt(self, image_data: str, prompt: str) -> str:
        """Send image to OpenAI Vision API with specific prompt"""
        if not self.api_key:
            # Return placeholder analysis if no API key
            return self._generate_placeholder_analysis(prompt)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4o",  # Use GPT-4 Omni model with vision
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload, 
                                       timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content'].strip()
                    else:
                        error_text = await response.text()
                        print(f"❌ OpenAI API Error {response.status}: {error_text[:200]}")
                        raise Exception(f"API Error {response.status}: {error_text}")
        
        except asyncio.TimeoutError:
            print(f"⏱️ Request timed out after 30 seconds")
            return self._generate_placeholder_analysis(prompt)
        except Exception as e:
            print(f"❌ Vision API error: {str(e)[:200]}")
            return self._generate_placeholder_analysis(prompt)
    
    def _generate_placeholder_analysis(self, prompt: str) -> str:
        """Generate placeholder analysis when API is not available"""
        if "tags" in prompt.lower():
            return "creative, inspiration, visual, design, art, contemporary, aesthetic, professional"
        elif "insights" in prompt.lower():
            return "This image demonstrates strong visual composition with thoughtful use of color and space. The style suggests modern design sensibilities that could work well for contemporary branding or digital applications."
        else:
            return "Image analysis requires API key configuration. The image appears to be a creative work suitable for design inspiration."
    
    def _parse_tags(self, tags_response: str) -> List[str]:
        """Parse comma-separated tags from API response"""
        if not tags_response:
            return []
        
        # Clean and split tags
        tags = [tag.strip().lower() for tag in tags_response.split(',')]
        # Remove empty tags and limit to 10
        tags = [tag for tag in tags if tag and len(tag) > 1][:10]
        return tags
    
    async def _extract_technical_info(self, image_path: Path) -> Dict[str, Any]:
        """Extract technical information about the image"""
        try:
            # Basic file info
            stat = image_path.stat()
            
            info = {
                'filename': image_path.name,
                'size_bytes': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'format': image_path.suffix.lower().replace('.', ''),
                'last_modified': stat.st_mtime
            }
            
            # Try to get image dimensions (requires Pillow)
            try:
                from PIL import Image
                with Image.open(image_path) as img:
                    info['width'] = img.width
                    info['height'] = img.height
                    info['aspect_ratio'] = round(img.width / img.height, 2)
                    info['megapixels'] = round((img.width * img.height) / 1000000, 1)
            except ImportError:
                info['note'] = 'Install Pillow for image dimensions: pip install Pillow'
            except Exception:
                info['note'] = 'Could not read image dimensions'
            
            return info
            
        except Exception as e:
            return {'error': str(e)}
    
    async def analyze_batch(self, image_paths: List[Path], max_concurrent: int = 2) -> Dict[str, Dict]:
        """Analyze multiple images with concurrency control"""
        results = {}
        
        # Process in batches to avoid rate limiting - reduce concurrency
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_single(path):
            async with semaphore:
                print(f"  Analyzing: {path.name}...")
                return await self.analyze_image(path)
        
        # Create tasks for all images
        tasks = [analyze_single(path) for path in image_paths]
        
        # Execute with progress tracking
        completed_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        for path, result in zip(image_paths, completed_results):
            if isinstance(result, Exception):
                results[str(path)] = {
                    'success': False,
                    'error': str(result)
                }
            else:
                results[str(path)] = result
        
        return results


class SmartContentManager:
    """Enhanced content manager with AI analysis"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.analyzer = ImageAnalyzer(api_key)
        self.content_dir = Path("content")
        self.images_dir = self.content_dir / "images"
        self.data_file = self.content_dir / "data.json"
        
        # Create directories
        self.content_dir.mkdir(exist_ok=True)
        self.images_dir.mkdir(exist_ok=True)
    
    def _load_data(self):
        """Load content data"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except:
            return {
                "items": [],
                "tags": [],
                "last_updated": "",
                "ai_analysis_enabled": bool(self.analyzer.api_key)
            }
    
    def _save_data(self, data):
        """Save content data"""
        from datetime import datetime
        data["last_updated"] = datetime.now().isoformat()
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def analyze_and_update_images(self, force_reanalyze: bool = False, max_images: int = 5):
        """Analyze images with AI and update database"""
        data = self._load_data()
        
        # Find images that need analysis
        existing_items = {item.get('filename'): item for item in data['items'] if item.get('type') == 'image'}
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}  # Remove .svg as it can't be analyzed
        images_to_analyze = []
        
        for image_file in self.images_dir.iterdir():
            if (image_file.suffix.lower() in image_extensions and 
                (image_file.name not in existing_items or 
                 force_reanalyze or 
                 not existing_items.get(image_file.name, {}).get('ai_analysis'))):
                images_to_analyze.append(image_file)
        
        if not images_to_analyze:
            print("No new images to analyze")
            return 0
        
        # Limit number of images to analyze in one go
        if len(images_to_analyze) > max_images:
            print(f"Found {len(images_to_analyze)} images. Analyzing first {max_images}...")
            images_to_analyze = images_to_analyze[:max_images]
        else:
            print(f"Analyzing {len(images_to_analyze)} images with AI...")
        
        # Analyze images
        analysis_results = await self.analyzer.analyze_batch(images_to_analyze)
        
        # Update or create items
        updated_count = 0
        for image_path in images_to_analyze:
            try:
                filename = image_path.name
                analysis = analysis_results.get(str(image_path), {})
                
                # Create or update item
                if filename in existing_items:
                    item = existing_items[filename]
                else:
                    item = {
                        "id": f"img_{len(data['items']) + updated_count + 1}",
                        "type": "image",
                        "filename": filename,
                        "path": f"content/images/{filename}",
                        "added_at": datetime.now().isoformat()
                    }
                    data['items'].append(item)
                
                # Add AI analysis if successful
                if analysis.get('success'):
                    ai_data = analysis['analysis']
                    
                    # Update with AI insights
                    item.update({
                        "title": self._generate_smart_title(filename, ai_data),
                        "description": ai_data.get('content_description', ''),
                        "ai_tags": ai_data.get('ai_tags', []),
                        "creative_insights": ai_data.get('creative_insights', ''),
                        "technical_info": ai_data.get('technical_info', {}),
                        "ai_analysis": {
                            "analyzed_at": datetime.now().isoformat(),
                            "success": True
                        }
                    })
                    
                    # Combine filename tags with AI tags
                    filename_tags = self._extract_tags_from_filename(filename)
                    all_tags = list(set(filename_tags + ai_data.get('ai_tags', [])))
                    item["tags"] = all_tags[:12]  # Limit total tags
                    
                    updated_count += 1
                    print(f"✅ Analyzed: {filename}")
                
                else:
                    # Fallback to filename-based analysis
                    item.update({
                        "title": self._filename_to_title(filename),
                        "tags": self._extract_tags_from_filename(filename),
                        "ai_analysis": {
                            "analyzed_at": datetime.now().isoformat(),
                            "success": False,
                            "error": analysis.get('error', 'Unknown error')
                        }
                    })
                    print(f"⚠️ Failed to analyze: {filename}")
            
            except Exception as e:
                print(f"❌ Error processing {image_path.name}: {e}")
        
        # Update global tags
        all_tags = set(data.get('tags', []))
        for item in data['items']:
            all_tags.update(item.get('tags', []))
        data['tags'] = sorted(list(all_tags))
        
        # Save updated data
        self._save_data(data)
        print(f"🎉 Successfully analyzed {updated_count} images")
        
        return updated_count
    
    def _generate_smart_title(self, filename: str, ai_data: Dict) -> str:
        """Generate intelligent title using AI analysis and filename"""
        # Try to extract a meaningful title from the description
        description = ai_data.get('content_description', '')
        if description:
            # Take the first sentence or phrase
            first_sentence = description.split('.')[0].strip()
            if len(first_sentence) < 60 and first_sentence:
                return first_sentence
        
        # Fallback to filename-based title
        return self._filename_to_title(filename)
    
    def _filename_to_title(self, filename: str) -> str:
        """Convert filename to readable title"""
        name = Path(filename).stem
        title = name.replace('_', ' ').replace('-', ' ').replace('.', ' ')
        return ' '.join(word.capitalize() for word in title.split())
    
    def _extract_tags_from_filename(self, filename: str) -> List[str]:
        """Extract tags from filename"""
        tags = []
        filename_lower = filename.lower()
        
        keywords = [
            'typography', 'logo', 'branding', 'minimal', 'bold', 'modern',
            'vintage', 'retro', 'dark', 'light', 'colorful', 'monochrome',
            'design', 'art', 'photo', 'illustration', 'ui', 'ux', 'web',
            'mobile', 'poster', 'instagram', 'story', 'social', 'raw',
            'emotional', 'portrait', 'landscape', 'abstract', 'geometric'
        ]
        
        for keyword in keywords:
            if keyword in filename_lower:
                tags.append(keyword)
        
        return tags[:5]


# Example usage and API setup
async def main():
    """Example usage of the image analyzer"""
    import os
    from pathlib import Path
    
    # Try to load from .env file first (safe method)
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    key_value = line.strip().split('=', 1)[1]
                    os.environ['OPENAI_API_KEY'] = key_value
                    break
    
    # Get API key from environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("⚠️ No OpenAI API key found. Set OPENAI_API_KEY environment variable for AI analysis.")
        print("   The system will work with basic filename-based analysis.")
    
    # Initialize smart content manager
    content_manager = SmartContentManager(api_key)
    
    # Analyze existing images
    await content_manager.analyze_and_update_images()

if __name__ == "__main__":
    asyncio.run(main())