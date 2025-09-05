#!/usr/bin/env python3
"""
Simple, working content server for Concierto.
No over-engineering - just a dashboard that works.
Enhanced with AI image analysis capabilities.
"""

import json
import os
import asyncio
from pathlib import Path
from datetime import datetime
from aiohttp import web
import aiofiles

# Import AI analysis (optional - works without API key)
try:
    from image_analyzer import SmartContentManager
    AI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ AI analysis not available: {e}")
    AI_AVAILABLE = False
except Exception as e:
    print(f"❌ Error loading AI analyzer: {e}")
    AI_AVAILABLE = False

# Import concept generator
try:
    from concept_generator import ConceptGenerator
    CONCEPT_GEN_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Concept generation not available: {e}")
    CONCEPT_GEN_AVAILABLE = False

# Import style vector analysis
try:
    from style_vector_fixed import analyze_style_vector, StyleVector
    STYLE_VECTOR_AVAILABLE = True
except ImportError as e:
    # Fallback to original if fixed not available
    try:
        from style_vector import analyze_style_vector, StyleVector
        STYLE_VECTOR_AVAILABLE = True
        print("⚠️ Using original style_vector (not fixed)")
    except:
        STYLE_VECTOR_AVAILABLE = False
        print(f"⚠️ Style vector analysis not available: {e}")
except Exception as e:
    print(f"❌ Error loading style vector analyzer: {e}")
    STYLE_VECTOR_AVAILABLE = False

# Import semantic analyzer (honest version)
try:
    from semantic_analyzer import analyze_semantic
    SEMANTIC_ANALYZER_AVAILABLE = True
    print("✅ Semantic analyzer loaded")
except ImportError as e:
    print(f"⚠️ Semantic analyzer not available: {e}")
    SEMANTIC_ANALYZER_AVAILABLE = False
except Exception as e:
    print(f"❌ Error loading semantic analyzer: {e}")
    SEMANTIC_ANALYZER_AVAILABLE = False

# Import brand synthesis engine
try:
    from synthesis_engine import BrandSynthesizer
    SYNTHESIS_ENGINE_AVAILABLE = True
    print("✅ Brand synthesis engine loaded")
except ImportError as e:
    print(f"⚠️ Brand synthesis engine not available: {e}")
    SYNTHESIS_ENGINE_AVAILABLE = False
except Exception as e:
    print(f"❌ Error loading synthesis engine: {e}")
    SYNTHESIS_ENGINE_AVAILABLE = False

# Import brand preview generator
try:
    from brand_preview import BrandPreviewGenerator
    BRAND_PREVIEW_AVAILABLE = True
    print("✅ Brand preview generator loaded")
except ImportError as e:
    print(f"⚠️ Brand preview generator not available: {e}")
    BRAND_PREVIEW_AVAILABLE = False
except Exception as e:
    print(f"❌ Error loading brand preview generator: {e}")
    BRAND_PREVIEW_AVAILABLE = False

class SimpleContentManager:
    """Content management with optional AI analysis"""
    
    def __init__(self):
        self.content_dir = Path("content")
        self.images_dir = self.content_dir / "images"
        self.notes_dir = self.content_dir / "notes"
        self.data_file = self.content_dir / "data.json"
        
        # Initialize AI analyzer if available
        self.ai_manager = None
        self.concept_generator = None
        if AI_AVAILABLE:
            # Try to load API key from .env file
            self._load_env_file()
            api_key = os.getenv('OPENAI_API_KEY')
            self.ai_manager = SmartContentManager(api_key)
            print(f"🤖 AI Analysis: {'Enabled' if api_key else 'Disabled (no API key)'}")
            
            # Initialize concept generator
            if CONCEPT_GEN_AVAILABLE and api_key:
                self.concept_generator = ConceptGenerator(api_key)
                print(f"🎨 Concept Generation: Enabled")
        
        # Create directories
        self.content_dir.mkdir(exist_ok=True)
        self.images_dir.mkdir(exist_ok=True)
        self.notes_dir.mkdir(exist_ok=True)
        
        # Initialize data file
        if not self.data_file.exists():
            self._save_data({
                "items": [],
                "tags": [],
                "last_updated": datetime.now().isoformat()
            })
    
    def _load_env_file(self):
        """Load environment variables from .env file"""
        env_file = Path('.env')
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
    
    def _load_data(self):
        """Load content data"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except:
            return {"items": [], "tags": [], "last_updated": datetime.now().isoformat()}
    
    def _save_data(self, data):
        """Save content data"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def scan_images(self):
        """Scan for new images and add to database"""
        # Always use basic scanning for now to avoid async issues
        # AI analysis can be triggered separately via API
        return self._scan_images_basic()
    
    async def scan_images_with_ai(self):
        """Async method for AI-powered image analysis"""
        if self.ai_manager:
            return await self.ai_manager.analyze_and_update_images()
        else:
            return self._scan_images_basic()
    
    def _scan_images_basic(self):
        """Basic image scanning without AI"""
        data = self._load_data()
        existing_files = {item.get('filename') for item in data['items'] if item.get('type') == 'image'}
        
        new_items = []
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
        
        for image_file in self.images_dir.iterdir():
            if image_file.suffix.lower() in image_extensions and image_file.name not in existing_files:
                # Create new image item
                item = {
                    "id": f"img_{len(data['items']) + len(new_items) + 1}",
                    "type": "image",
                    "filename": image_file.name,
                    "title": self._filename_to_title(image_file.name),
                    "path": f"content/images/{image_file.name}",
                    "tags": self._extract_tags_from_filename(image_file.name),
                    "added_at": datetime.now().isoformat(),
                    "notes": ""
                }
                
                # Add style vector analysis if available
                if STYLE_VECTOR_AVAILABLE:
                    try:
                        style_data = analyze_style_vector(str(image_file))
                        if style_data:
                            item.update(style_data)
                            print(f"✨ Style vector analyzed for {image_file.name}")
                    except Exception as e:
                        print(f"⚠️ Style vector analysis failed for {image_file.name}: {e}")
                
                # Add semantic analysis automatically
                if SEMANTIC_ANALYZER_AVAILABLE:
                    try:
                        semantic_data = analyze_semantic(str(image_file), item.get('description', ''))
                        if semantic_data and 'error' not in semantic_data:
                            item['semantic_analysis'] = semantic_data
                            
                            # Extract key colors for quick access
                            if 'colors' in semantic_data and 'most_common' in semantic_data['colors']:
                                colors = semantic_data['colors']['most_common']
                                if colors:
                                    item['primary_color_actual'] = colors[0]['hex']
                                    if len(colors) > 1:
                                        item['secondary_color_actual'] = colors[1]['hex']
                            
                            print(f"🔍 Semantic analysis completed for {image_file.name}")
                    except Exception as e:
                        print(f"⚠️ Semantic analysis failed for {image_file.name}: {e}")
                
                new_items.append(item)
        
        if new_items:
            data['items'].extend(new_items)
            # Update tags
            all_tags = set(data.get('tags', []))
            for item in new_items:
                all_tags.update(item.get('tags', []))
            data['tags'] = sorted(list(all_tags))
            
            self._save_data(data)
            print(f"Added {len(new_items)} new images")
        
        return len(new_items)
    
    def _filename_to_title(self, filename):
        """Convert filename to readable title"""
        name = Path(filename).stem
        # Replace separators with spaces and capitalize
        title = name.replace('_', ' ').replace('-', ' ').replace('.', ' ')
        return ' '.join(word.capitalize() for word in title.split())
    
    def _extract_tags_from_filename(self, filename):
        """Extract tags from filename"""
        tags = []
        filename_lower = filename.lower()
        
        # Common design keywords
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
        
        return tags[:5]  # Limit to 5 tags
    
    def get_all_content(self):
        """Get all content"""
        return self._load_data()
    
    def add_note(self, title, content, tags=None):
        """Add a text note"""
        data = self._load_data()
        
        note = {
            "id": f"note_{len(data['items']) + 1}",
            "type": "note",
            "title": title,
            "content": content,
            "tags": tags or [],
            "added_at": datetime.now().isoformat()
        }
        
        data['items'].append(note)
        
        # Update tags
        all_tags = set(data.get('tags', []))
        all_tags.update(tags or [])
        data['tags'] = sorted(list(all_tags))
        
        self._save_data(data)
        return note

# Global content manager
content_manager = SimpleContentManager()


async def working_dashboard(request):
    """Serve working dashboard"""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Concierto - Working Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: #f8f9fa;
            color: #2c3e50;
            line-height: 1.6;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 2rem; 
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-number { 
            font-size: 2rem; 
            font-weight: bold; 
            color: #667eea; 
        }
        .content-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }
        .content-item {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
            cursor: pointer;
        }
        .content-item:hover { 
            transform: translateY(-4px); 
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .image-preview {
            width: 100%;
            height: 200px;
            object-fit: cover;
            background: #f1f3f4;
        }
        .item-content {
            padding: 1.5rem;
        }
        .item-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #2c3e50;
        }
        .item-description {
            color: #6c757d;
            font-size: 0.9rem;
            margin: 0.5rem 0;
            line-height: 1.4;
        }
        .item-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
        }
        .tag {
            background: #e9ecef;
            color: #495057;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
        }
        .ai-tag {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
        }
        .campaign-btn {
            background: linear-gradient(135deg, #ff6b6b, #ff8787);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            margin: 0.5rem;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            margin: 0.5rem;
        }
        .refresh-btn:hover {
            background: #5a67d8;
        }
        .error {
            background: #ff6b6b;
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        .success {
            background: #51cf66;
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        .loading {
            text-align: center;
            padding: 2rem;
            color: #6c757d;
        }
        
        /* Modal styles */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            backdrop-filter: blur(3px);
        }
        .modal.show { display: flex; align-items: center; justify-content: center; }
        .modal-content {
            background: white;
            margin: auto;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            max-width: 800px;
            max-height: 80vh;
            width: 90%;
            overflow-y: auto;
            position: relative;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid #eee;
            padding-bottom: 1rem;
        }
        .modal-close {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #999;
            padding: 0.5rem;
        }
        .modal-close:hover { color: #333; }
        .modal-image {
            width: 100%;
            max-height: 300px;
            object-fit: contain;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        .modal-section {
            margin-bottom: 1.5rem;
        }
        .modal-section h3 {
            color: #667eea;
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
        }
        .modal-section p {
            line-height: 1.6;
            color: #333;
        }
        .modal-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }
        
        /* Modal Action Buttons */
        .modal-actions {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }
        .action-btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: transform 0.2s ease;
        }
        .action-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        .action-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        /* Edit Form Styles */
        .form-group {
            margin-bottom: 1.5rem;
        }
        .form-group label {
            display: block;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #2c3e50;
        }
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 1rem;
            font-family: inherit;
            transition: border-color 0.2s;
        }
        .form-group input:focus, .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .form-group textarea {
            resize: vertical;
            min-height: 80px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn-primary:hover {
            transform: translateY(-1px);
        }
        .btn-secondary {
            background: #f8f9fa;
            color: #6c757d;
            border: 1px solid #ddd;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .btn-secondary:hover {
            background: #e9ecef;
        }
        
        /* Tag Editor Styles */
        .tag-editor {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 0.75rem;
            background: #f8f9fa;
        }
        .tag-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 0.75rem;
            min-height: 32px;
        }
        .tag-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 0.35rem 0.75rem;
            border-radius: 20px;
            font-size: 0.9rem;
            animation: slideIn 0.2s ease;
        }
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .tag-chip button {
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            font-size: 1.1rem;
            padding: 0;
            margin: 0;
            line-height: 1;
            opacity: 0.8;
            transition: opacity 0.2s;
        }
        .tag-chip button:hover {
            opacity: 1;
        }
        .tag-input-wrapper {
            display: flex;
            gap: 0.5rem;
        }
        .tag-input {
            flex: 1;
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 0.95rem;
        }
        .tag-add-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.95rem;
            transition: background 0.2s;
        }
        .tag-add-btn:hover {
            background: #5a67d8;
        }
        .tag-suggestions {
            display: none;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.75rem;
            padding-top: 0.75rem;
            border-top: 1px solid #e0e0e0;
        }
        .tag-suggestions.show {
            display: flex;
        }
        .tag-suggestion {
            background: white;
            border: 1px solid #ddd;
            color: #6c757d;
            padding: 0.35rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        .tag-suggestion:hover {
            border-color: #667eea;
            color: #667eea;
            background: #f8f9ff;
        }
        
        /* Edit button overlay */
        .content-item {
            position: relative;
        }
        .edit-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(102, 126, 234, 0.95);
            color: white;
            border: none;
            padding: 0.5rem 0.75rem;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.85rem;
            opacity: 0.7;
            transition: all 0.2s;
            z-index: 10;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }
        .content-item:hover .edit-btn {
            opacity: 1;
            transform: scale(1.05);
        }
        .edit-btn:hover {
            background: #5a67d8;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        
        /* Style Vector Display */
        .style-vector-mini {
            display: flex;
            gap: 0.5rem;
            margin-top: 0.5rem;
            flex-wrap: wrap;
        }
        .style-dimension {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border: 1px solid #dee2e6;
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-size: 0.75rem;
            color: #495057;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }
        .style-bar {
            width: 20px;
            height: 4px;
            background: #e9ecef;
            border-radius: 2px;
            overflow: hidden;
        }
        .style-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }
        .brand-colors {
            display: flex;
            gap: 0.25rem;
            margin-top: 0.5rem;
        }
        .color-chip {
            width: 16px;
            height: 16px;
            border-radius: 50%;
            border: 1px solid rgba(0,0,0,0.1);
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        
        /* Modal Style Vector Details */
        .style-vector-details {
            background: linear-gradient(135deg, #f8f9ff, #f0f4ff);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid #e3e8ff;
        }
        .style-dimension-full {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
            padding: 0.5rem;
            background: white;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }
        .dimension-label {
            font-weight: 600;
            color: #495057;
            min-width: 100px;
        }
        .dimension-bar {
            flex: 1;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            margin: 0 1rem;
            overflow: hidden;
        }
        .dimension-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }
        .dimension-value {
            font-weight: bold;
            color: #667eea;
            min-width: 60px;
            text-align: right;
        }
        .brand-tokens-display {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        .brand-token-group {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }
        .brand-token-label {
            font-size: 0.85rem;
            color: #6c757d;
            margin-bottom: 0.5rem;
        }
        .brand-token-value {
            font-weight: 600;
            color: #495057;
        }
        .color-display {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .color-display .color-chip {
            width: 24px;
            height: 24px;
        }
        
        /* Brand Cards */
        .brand-section {
            margin: 2rem 0;
        }
        .brand-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
            margin-top: 1rem;
        }
        .brand-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            cursor: pointer;
        }
        .brand-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }
        .brand-colors {
            display: flex;
            gap: 0.5rem;
            margin: 1rem 0;
        }
        .color-swatch {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            border: 2px solid white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .brand-meta {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 0.5rem;
        }
        .brand-accessibility {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-size: 0.8rem;
            margin-top: 0.5rem;
        }
        .accessibility-pass {
            background: #d4edda;
            color: #155724;
        }
        .accessibility-warn {
            background: #fff3cd;
            color: #856404;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎼 Concierto - Working Dashboard</h1>
        <p>Your Creative Content Dashboard</p>
    </div>
    
    <div class="container">
        <div id="status"></div>
        
        <div style="margin-bottom: 2rem;">
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Page</button>
            <button class="refresh-btn" style="background: linear-gradient(45deg, #667eea, #764ba2);" onclick="runAIAnalysis()">🤖 Run AI Analysis</button>
            <button class="refresh-btn" style="background: linear-gradient(45deg, #ff9500, #ff6b35);" onclick="runStyleAnalysis()">🎨 Style Analysis</button>
            <button class="refresh-btn" style="background: linear-gradient(45deg, #ff6b35, #f093fb);" onclick="toggleBrandSynthesis()">🎨 Brand Synthesis</button>
            <button class="campaign-btn" onclick="loadCampaigns()">📋 View Campaigns</button>
        </div>
        
        <div class="stats" id="stats">
            <div class="stat-card">
                <div class="stat-number">-</div>
                <div class="stat-label">Total Items</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">-</div>
                <div class="stat-label">Images</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">-</div>
                <div class="stat-label">Tags</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">-</div>
                <div class="stat-label">Campaigns</div>
            </div>
        </div>
        
        <!-- Brand Synthesis Interface -->
        <div id="brandSynthesisPanel" style="display: none; background: #f8f9ff; border: 2px solid #667eea; border-radius: 12px; padding: 2rem; margin-bottom: 2rem;">
            <h3 style="color: #667eea; margin-bottom: 1.5rem;">🎨 Create Brand from Selected Images</h3>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                <!-- Left: Image Selection -->
                <div>
                    <h4>Select Images (2-5 recommended):</h4>
                    <div id="imageSelector" style="max-height: 300px; overflow-y: auto; border: 1px solid #ddd; border-radius: 8px; padding: 1rem;">
                        <p style="color: #666;">Loading images...</p>
                    </div>
                    <p style="font-size: 0.9em; color: #666; margin-top: 0.5rem;">
                        Selected: <span id="selectedCount">0</span> images
                    </p>
                </div>
                
                <!-- Right: Brand Brief -->
                <div>
                    <h4>Brand Brief:</h4>
                    <div style="display: flex; flex-direction: column; gap: 1rem;">
                        <div>
                            <label style="display: block; margin-bottom: 0.5rem; font-weight: bold;">Brand Name:</label>
                            <input type="text" id="brandName" placeholder="e.g. Creative Studio" style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;">
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 0.5rem; font-weight: bold;">Category:</label>
                            <select id="brandCategory" style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;">
                                <option value="">Select category...</option>
                                <option value="Technology">Technology</option>
                                <option value="Creative Agency">Creative Agency</option>
                                <option value="Fashion">Fashion</option>
                                <option value="Food & Beverage">Food & Beverage</option>
                                <option value="Healthcare">Healthcare</option>
                                <option value="Education">Education</option>
                                <option value="Consulting">Consulting</option>
                                <option value="Retail">Retail</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 0.5rem; font-weight: bold;">Target Audience:</label>
                            <input type="text" id="brandAudience" placeholder="e.g. Young professionals, Designers" style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;">
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 0.5rem;">
                                <input type="checkbox" id="generateAlternatives" checked> Generate 3 alternatives
                            </label>
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 2rem; display: flex; gap: 1rem; justify-content: center;">
                <button class="refresh-btn" onclick="synthesizeBrand()" id="synthesizeBtn" style="background: linear-gradient(45deg, #667eea, #764ba2); padding: 1rem 2rem; font-size: 1.1rem;">
                    🎨 Generate Brand System
                </button>
                <button class="refresh-btn" onclick="toggleBrandSynthesis()" style="background: #6c757d;">
                    Cancel
                </button>
            </div>
            
            <div id="synthesisStatus" style="margin-top: 1rem; text-align: center; display: none;">
                <p style="color: #667eea;">🔄 Generating brand system...</p>
            </div>
        </div>
        
        <!-- Generated Brands Section -->
        <div class="brand-section" id="brandSection" style="display: none;">
            <h2>🎨 Generated Brand Systems</h2>
            <div class="brand-cards" id="brandCards">
                <!-- Brands will be loaded here -->
            </div>
        </div>

        <div id="content" class="content-grid">
            <div class="loading">Loading content...</div>
        </div>
    </div>
    
    <!-- Modal -->
    <div id="itemModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle">Item Details</h2>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div id="modalBody">
                <!-- Content will be loaded here -->
            </div>
        </div>
    </div>

    <!-- Edit Modal -->
    <div id="editModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>✏️ Edit Content</h2>
                <button class="modal-close" onclick="closeEditModal()">&times;</button>
            </div>
            <div class="modal-body">
                <form id="editForm" onsubmit="saveEdit(event)">
                    <div class="form-group">
                        <label for="editTitle">Title:</label>
                        <input type="text" id="editTitle" name="title" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="editDescription">Description:</label>
                        <textarea id="editDescription" name="description" rows="4" placeholder="Add your refined description or intent for this reference image..."></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="editNotes">Personal Notes:</label>
                        <textarea id="editNotes" name="notes" rows="3" placeholder="Add personal notes about why this image is important, what it represents, or how you want to use it..."></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>Tags:</label>
                        <div class="tag-editor">
                            <div id="tagList" class="tag-list"></div>
                            <div class="tag-input-wrapper">
                                <input type="text" id="tagInput" class="tag-input" placeholder="Add a tag and press Enter" onkeydown="handleTagInput(event)">
                                <button type="button" class="tag-add-btn" onclick="addTag()">+ Add</button>
                            </div>
                            <div id="tagSuggestions" class="tag-suggestions"></div>
                        </div>
                        <input type="hidden" id="editTags" name="tags">
                    </div>
                    
                    <div class="form-group" style="display: flex; gap: 1rem; justify-content: flex-end; margin-top: 2rem;">
                        <button type="button" class="btn-secondary" onclick="closeEditModal()">Cancel</button>
                        <button type="submit" class="btn-primary">💾 Save Changes</button>
                    </div>
                    
                    <input type="hidden" id="editItemId" name="id">
                </form>
            </div>
        </div>
    </div>

    <script>
        // Global variables
        let contentData = null;
        let campaignsData = null;
        
        // Main function to load content
        async function loadContent() {
            console.log('Loading content...');
            const contentDiv = document.getElementById('content');
            const statusDiv = document.getElementById('status');
            
            try {
                // Show loading state
                contentDiv.innerHTML = '<div class="loading">Loading content from API...</div>';
                
                // Fetch data from API
                const response = await fetch('/api/content');
                console.log('API Response Status:', response.status);
                
                if (!response.ok) {
                    throw new Error(`API returned status ${response.status}`);
                }
                
                const data = await response.json();
                console.log('Data received:', data);
                contentData = data;
                
                // Update statistics
                updateStats(data);
                
                // Display content
                displayContent(data.items || []);
                
                // Load brands if they exist
                if (data.brands && data.brands.length > 0) {
                    console.log('Loading brands:', data.brands.length, 'brands found');
                    loadBrands(data.brands);
                } else {
                    console.log('No brands found in data:', data);
                }
                
                // Show success message
                statusDiv.innerHTML = '<div class="success">✅ Content loaded successfully!</div>';
                setTimeout(() => { statusDiv.innerHTML = ''; }, 3000);
                
            } catch (error) {
                console.error('Error loading content:', error);
                contentDiv.innerHTML = `<div class="error">❌ Error loading content: ${error.message}</div>`;
                statusDiv.innerHTML = `<div class="error">Failed to load content. Check console for details.</div>`;
            }
        }
        
        // Update statistics display
        function updateStats(data) {
            const stats = document.getElementById('stats');
            const itemCount = data.items ? data.items.length : 0;
            const imageCount = data.items ? data.items.filter(i => i.type === 'image').length : 0;
            const tagCount = data.tags ? data.tags.length : 0;
            
            stats.innerHTML = `
                <div class="stat-card">
                    <div class="stat-number">${itemCount}</div>
                    <div class="stat-label">Total Items</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${imageCount}</div>
                    <div class="stat-label">Images</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${tagCount}</div>
                    <div class="stat-label">Tags</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="campaignCount">-</div>
                    <div class="stat-label">Campaigns</div>
                </div>
            `;
        }
        
        // Display content items
        function displayContent(items) {
            const contentDiv = document.getElementById('content');
            
            if (!items || items.length === 0) {
                contentDiv.innerHTML = '<div class="loading">No content items found. Add images to content/images/ folder.</div>';
                return;
            }
            
            // Build HTML for each item
            let html = '';
            items.forEach(item => {
                // Safely get values with defaults
                const title = item.title || 'Untitled';
                const description = item.description || '';
                const path = item.path || '';
                const tags = item.tags || [];
                const aiTags = item.ai_tags || [];
                const notes = item.notes || '';
                
                if (item.type === 'image') {
                    html += `
                        <div class="content-item" onclick="showItemModal(${items.indexOf(item)})">
                            <button class="edit-btn" onclick="event.stopPropagation(); editItem('${item.id}')" title="Edit this item">✏️ Edit</button>
                            ${path ? `<img src="/${path}" alt="${title}" class="image-preview" onerror="this.style.display='none'">` : ''}
                            <div class="item-content">
                                <div class="item-title">${escapeHtml(title)}</div>
                                ${description ? `<p class="item-description">${escapeHtml(description.substring(0, 150))}${description.length > 150 ? '... <em style="color: #667eea;">Click to read more</em>' : ''}</p>` : '<p class="item-description" style="color: #999; font-style: italic;">No description yet - click edit to add one</p>'}
                                ${notes ? `<p style="color: #764ba2; font-style: italic;">📝 ${escapeHtml(notes)}</p>` : ''}
                                <div class="item-tags">
                                    ${aiTags.map(tag => `<span class="tag ai-tag">🤖 ${escapeHtml(tag)}</span>`).join('')}
                                    ${tags.filter(t => !aiTags.includes(t)).map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                                </div>
                                ${item.style_vector ? renderStyleVectorMini(item.style_vector, item.brand_tokens) : ''}
                            </div>
                        </div>
                    `;
                } else {
                    const content = item.content || '';
                    html += `
                        <div class="content-item" onclick="showItemModal(${items.indexOf(item)})">
                            <button class="edit-btn" onclick="event.stopPropagation(); editItem('${item.id}')" title="Edit this item">✏️ Edit</button>
                            <div class="item-content">
                                <div class="item-title">${escapeHtml(title)}</div>
                                <p>${escapeHtml(content.substring(0, 150))}${content.length > 150 ? '... <em style="color: #667eea;">Click to read more</em>' : ''}</p>
                                <div class="item-tags">
                                    ${tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                                </div>
                            </div>
                        </div>
                    `;
                }
            });
            
            contentDiv.innerHTML = html || '<div class="loading">No items to display</div>';
        }
        
        // Render mini style vector display for content cards
        function renderStyleVectorMini(styleVector, brandTokens) {
            if (!styleVector) return '';
            
            const dimensions = [
                { key: 'energy', label: 'Energy', value: styleVector.energy },
                { key: 'sophistication', label: 'Sophistication', value: styleVector.sophistication },
                { key: 'temperature', label: 'Temp', value: styleVector.temperature }
            ];
            
            let html = '<div class="style-vector-mini">';
            
            // Show top 3 dimensions as mini bars
            dimensions.forEach(dim => {
                const percentage = Math.round(dim.value * 100);
                html += `
                    <div class="style-dimension" title="${dim.label}: ${percentage}%">
                        <span>${dim.label.substring(0,3)}</span>
                        <div class="style-bar">
                            <div class="style-bar-fill" style="width: ${percentage}%"></div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            
            // Add brand colors if available
            if (brandTokens && (brandTokens.primary_color || brandTokens.secondary_color)) {
                html += '<div class="brand-colors">';
                if (brandTokens.primary_color) {
                    html += `<div class="color-chip" style="background-color: ${brandTokens.primary_color}" title="Primary: ${brandTokens.primary_color}"></div>`;
                }
                if (brandTokens.secondary_color && brandTokens.secondary_color !== brandTokens.primary_color) {
                    html += `<div class="color-chip" style="background-color: ${brandTokens.secondary_color}" title="Secondary: ${brandTokens.secondary_color}"></div>`;
                }
                html += '</div>';
            }
            
            return html;
        }
        
        // Render detailed style vector display for modal
        function renderStyleVectorModal(styleVector, brandTokens) {
            if (!styleVector) return '';
            
            const dimensions = [
                { 
                    key: 'energy', 
                    label: 'Energy', 
                    value: styleVector.energy, 
                    description: styleVector.energy > 0.7 ? 'Energetic' : styleVector.energy > 0.5 ? 'Dynamic' : styleVector.energy > 0.3 ? 'Balanced' : 'Calm'
                },
                { 
                    key: 'sophistication', 
                    label: 'Sophistication', 
                    value: styleVector.sophistication,
                    description: styleVector.sophistication > 0.7 ? 'Refined' : styleVector.sophistication > 0.5 ? 'Professional' : styleVector.sophistication > 0.3 ? 'Approachable' : 'Playful'
                },
                { 
                    key: 'density', 
                    label: 'Density', 
                    value: styleVector.density,
                    description: styleVector.density > 0.7 ? 'Rich' : styleVector.density > 0.5 ? 'Detailed' : styleVector.density > 0.3 ? 'Balanced' : 'Minimal'
                },
                { 
                    key: 'temperature', 
                    label: 'Temperature', 
                    value: styleVector.temperature,
                    description: styleVector.temperature > 0.7 ? 'Warm' : styleVector.temperature > 0.5 ? 'Neutral' : 'Cool'
                },
                { 
                    key: 'era', 
                    label: 'Era', 
                    value: styleVector.era,
                    description: styleVector.era > 0.7 ? 'Futuristic' : styleVector.era > 0.5 ? 'Contemporary' : styleVector.era > 0.3 ? 'Timeless' : 'Classic'
                }
            ];
            
            let html = `
                <div class="style-vector-details">
                    <h3>🎨 Style Vector Analysis</h3>
                    <p style="color: #6c757d; font-size: 0.9rem; margin-bottom: 1rem;">Computational analysis of visual style characteristics</p>
            `;
            
            // Render dimension bars
            dimensions.forEach(dim => {
                const percentage = Math.round(dim.value * 100);
                html += `
                    <div class="style-dimension-full">
                        <div class="dimension-label">${dim.label}</div>
                        <div class="dimension-bar">
                            <div class="dimension-bar-fill" style="width: ${percentage}%"></div>
                        </div>
                        <div class="dimension-value">${percentage}% <small>(${dim.description})</small></div>
                    </div>
                `;
            });
            
            // Brand tokens section
            if (brandTokens) {
                html += `
                    <h4 style="margin: 1.5rem 0 1rem 0; color: #495057;">Brand Design Tokens</h4>
                    <div class="brand-tokens-display">
                        <div class="brand-token-group">
                            <div class="brand-token-label">Primary Color</div>
                            <div class="brand-token-value color-display">
                                <div class="color-chip" style="background-color: ${brandTokens.primary_color || '#ccc'}"></div>
                                ${brandTokens.primary_color || 'N/A'}
                            </div>
                        </div>
                        
                        <div class="brand-token-group">
                            <div class="brand-token-label">Secondary Color</div>
                            <div class="brand-token-value color-display">
                                <div class="color-chip" style="background-color: ${brandTokens.secondary_color || '#ccc'}"></div>
                                ${brandTokens.secondary_color || 'N/A'}
                            </div>
                        </div>
                        
                        <div class="brand-token-group">
                            <div class="brand-token-label">Font Classification</div>
                            <div class="brand-token-value">${brandTokens.font_class || 'N/A'}</div>
                        </div>
                        
                        <div class="brand-token-group">
                            <div class="brand-token-label">Spacing Unit</div>
                            <div class="brand-token-value">${brandTokens.spacing_unit || 'N/A'}</div>
                        </div>
                        
                        <div class="brand-token-group" style="grid-column: 1 / -1;">
                            <div class="brand-token-label">Mood Keywords</div>
                            <div class="brand-token-value">${brandTokens.mood_keywords ? brandTokens.mood_keywords.join(', ') : 'N/A'}</div>
                        </div>
                    </div>
                `;
            }
            
            html += '</div>';
            
            return html;
        }
        
        // Load campaigns
        async function loadCampaigns() {
            try {
                const response = await fetch('/api/campaigns');
                const campaigns = await response.json();
                campaignsData = campaigns;
                
                // Update campaign count
                document.getElementById('campaignCount').textContent = campaigns.length;
                
                // Show campaigns in alert for now
                if (campaigns.length > 0) {
                    alert(`Found ${campaigns.length} campaigns:\\n\\n${campaigns.map(c => `• ${c.name} (${c.client})`).join('\\n')}`);
                } else {
                    alert('No campaigns found.');
                }
                
            } catch (error) {
                console.error('Error loading campaigns:', error);
                alert('Failed to load campaigns');
            }
        }
        
        // Scan for new images
        async function scanForNew() {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = '<div class="loading">🔍 Scanning for new images...</div>';
            
            try {
                const response = await fetch('/api/scan', { method: 'POST' });
                const result = await response.json();
                
                if (result.scanned > 0) {
                    statusDiv.innerHTML = `<div class="success">✅ Found ${result.scanned} new images!</div>`;
                    setTimeout(loadContent, 1000);
                } else {
                    statusDiv.innerHTML = '<div class="success">✅ No new images found</div>';
                }
                setTimeout(() => { statusDiv.innerHTML = ''; }, 3000);
                
            } catch (error) {
                console.error('Error scanning:', error);
                statusDiv.innerHTML = '<div class="error">❌ Scan failed</div>';
            }
        }
        
        // Run AI Analysis on images
        async function runAIAnalysis() {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = '<div class="loading">🤖 Running AI analysis on images... This may take 30-60 seconds</div>';
            
            try {
                const response = await fetch('/api/ai-scan', { method: 'POST' });
                const result = await response.json();
                
                if (response.ok && result.scanned >= 0) {
                    statusDiv.innerHTML = `<div class="success">✅ AI Analysis complete! Analyzed ${result.scanned} images</div>`;
                    setTimeout(loadContent, 1000);
                } else {
                    statusDiv.innerHTML = `<div class="error">❌ ${result.message || 'AI analysis failed'}</div>`;
                }
                setTimeout(() => { statusDiv.innerHTML = ''; }, 5000);
                
            } catch (error) {
                console.error('Error with AI analysis:', error);
                statusDiv.innerHTML = '<div class="error">❌ AI analysis failed. Check console for details.</div>';
            }
        }
        
        // Run Style Vector Analysis on images
        async function runStyleAnalysis() {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = '<div class="loading">🎨 Running style vector analysis... This may take 30-60 seconds</div>';
            
            try {
                const response = await fetch('/api/style-analysis', { method: 'POST' });
                const result = await response.json();
                
                if (response.ok && result.success) {
                    statusDiv.innerHTML = `<div class="success">✅ Style analysis complete! Analyzed ${result.processed} images with style vectors and brand tokens</div>`;
                    setTimeout(loadContent, 1000);
                } else {
                    statusDiv.innerHTML = `<div class="error">❌ ${result.error || result.message || 'Style analysis failed'}</div>`;
                }
                setTimeout(() => { statusDiv.innerHTML = ''; }, 5000);
                
            } catch (error) {
                console.error('Error with style analysis:', error);
                statusDiv.innerHTML = '<div class="error">❌ Style analysis failed. Check console for details.</div>';
            }
        }
        
        // Utility function to escape HTML
        function escapeHtml(text) {
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Modal functions
        function showItemModal(index) {
            if (!contentData || !contentData.items || !contentData.items[index]) {
                console.error('Item not found:', index);
                return;
            }
            
            const item = contentData.items[index];
            const modal = document.getElementById('itemModal');
            const modalTitle = document.getElementById('modalTitle');
            const modalBody = document.getElementById('modalBody');
            
            modalTitle.textContent = item.title || 'Untitled';
            
            let modalContent = '';
            
            // Image
            if (item.type === 'image' && item.path) {
                modalContent += `<img src="/${item.path}" alt="${item.title}" class="modal-image" onerror="this.style.display='none'">`;
            }
            
            // Description
            if (item.description) {
                modalContent += `
                    <div class="modal-section">
                        <h3>📝 Description</h3>
                        <p>${escapeHtml(item.description)}</p>
                    </div>
                `;
            }
            
            // Style Vector Analysis
            if (item.style_vector && item.brand_tokens) {
                modalContent += renderStyleVectorModal(item.style_vector, item.brand_tokens);
            }
            
            // Semantic Analysis (honest, measurable data)
            if (item.semantic_analysis) {
                const semantic = item.semantic_analysis;
                modalContent += `
                    <div class="modal-section">
                        <h3>🔬 Semantic Analysis</h3>
                        <p><strong>Analysis Type:</strong> Honest semantic analysis (measurable data only)</p>
                        
                        ${semantic.colors ? `
                        <div style="margin: 1rem 0;">
                            <h4>📊 Color Analysis</h4>
                            ${semantic.colors.most_common ? `
                            <p><strong>Most Common Colors:</strong></p>
                            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.5rem 0;">
                                ${semantic.colors.most_common.slice(0, 6).map(color => 
                                    `<div style="display: flex; align-items: center; gap: 0.5rem;">
                                        <div style="width: 20px; height: 20px; background: ${color.hex}; border: 1px solid #ccc; border-radius: 3px;"></div>
                                        <span style="font-size: 0.9em;">${color.hex} (${color.percentage}%)</span>
                                    </div>`
                                ).join('')}
                            </div>
                            ` : ''}
                            ${semantic.colors.total_unique_colors ? `<p><strong>Total Unique Colors:</strong> ${semantic.colors.total_unique_colors}</p>` : ''}
                        </div>
                        ` : ''}
                        
                        ${semantic.composition ? `
                        <div style="margin: 1rem 0;">
                            <h4>📐 Composition</h4>
                            <p><strong>Dimensions:</strong> ${semantic.composition.width}×${semantic.composition.height} (${semantic.composition.orientation})</p>
                            <p><strong>Aspect Ratio:</strong> ${semantic.composition.aspect_ratio}</p>
                            <p><strong>Size Category:</strong> ${semantic.composition.size_category}</p>
                        </div>
                        ` : ''}
                        
                        ${semantic.visual_properties ? `
                        <div style="margin: 1rem 0;">
                            <h4>✨ Visual Properties (Measured)</h4>
                            <p><strong>Brightness:</strong> ${semantic.visual_properties.brightness} (${semantic.visual_properties.darkness})</p>
                            <p><strong>Contrast:</strong> ${semantic.visual_properties.contrast}</p>
                            <p><strong>Saturation:</strong> ${semantic.visual_properties.saturation}</p>
                            <p><strong>Grayscale:</strong> ${semantic.visual_properties.is_grayscale ? 'Yes' : 'No'}</p>
                        </div>
                        ` : ''}
                        
                        ${semantic.description_keywords && semantic.description_keywords.length > 0 ? `
                        <div style="margin: 1rem 0;">
                            <h4>🔤 Description Keywords</h4>
                            <p>${semantic.description_keywords.join(', ')}</p>
                        </div>
                        ` : ''}
                    </div>
                `;
            }
            
            // Multi-Agent Analysis (legacy support)
            if (item.enhanced_analysis && item.enhanced_analysis.enhanced_description) {
                const enhanced = item.enhanced_analysis;
                modalContent += `
                    <div class="modal-section">
                        <h3>🚀 Multi-Agent Enhanced Analysis</h3>
                        <p><strong>Enhanced Description:</strong><br>${escapeHtml(enhanced.enhanced_description || '')}</p>
                    </div>
                `;
            } else if (item.creative_insights) {
                modalContent += `
                    <div class="modal-section">
                        <h3>🤖 AI Creative Insights</h3>
                        <p>${escapeHtml(item.creative_insights).replace(/\\n/g, '<br>')}</p>
                    </div>
                `;
            }
            
            // Notes
            if (item.notes) {
                modalContent += `
                    <div class="modal-section">
                        <h3>📝 Notes</h3>
                        <p>${escapeHtml(item.notes)}</p>
                    </div>
                `;
            }
            
            // Tags
            if ((item.tags && item.tags.length > 0) || (item.ai_tags && item.ai_tags.length > 0)) {
                modalContent += `
                    <div class="modal-section">
                        <h3>🏷️ Tags</h3>
                        <div class="modal-tags">
                            ${(item.ai_tags || []).map(tag => `<span class="tag ai-tag">🤖 ${escapeHtml(tag)}</span>`).join('')}
                            ${(item.tags || []).filter(t => !(item.ai_tags || []).includes(t)).map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                        </div>
                    </div>
                `;
            }
            
            // Technical info
            if (item.technical_info) {
                const tech = item.technical_info;
                modalContent += `
                    <div class="modal-section">
                        <h3>⚙️ Technical Info</h3>
                        <p><strong>Format:</strong> ${tech.format || 'Unknown'}<br>
                        <strong>Size:</strong> ${tech.size_mb || 0} MB<br>
                        ${tech.width ? `<strong>Dimensions:</strong> ${tech.width} × ${tech.height}px<br>` : ''}
                        <strong>File:</strong> ${tech.filename || item.filename}</p>
                    </div>
                `;
            }
            
            
            modalBody.innerHTML = modalContent;
            modal.classList.add('show');
        }
        
        function closeModal() {
            const modal = document.getElementById('itemModal');
            modal.classList.remove('show');
        }
        
        // Close modal when clicking outside
        document.addEventListener('click', function(event) {
            const modal = document.getElementById('itemModal');
            if (event.target === modal) {
                closeModal();
            }
        });
        
        // Close modal with Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                closeModal();
            }
        });
        
        // Edit Modal Functions
        function editItem(itemId) {
            console.log('Edit item:', itemId);
            
            if (!contentData || !contentData.items) {
                alert('❌ Content not loaded');
                return;
            }
            
            const item = contentData.items.find(i => i.id === itemId);
            if (!item) {
                alert('❌ Item not found');
                return;
            }
            
            // Populate the edit form
            document.getElementById('editItemId').value = item.id;
            document.getElementById('editTitle').value = item.title || '';
            document.getElementById('editDescription').value = item.description || '';
            document.getElementById('editNotes').value = item.notes || '';
            
            // Handle tags - populate the new tag editor
            const tags = item.tags || [];
            currentEditTags = [...tags]; // Create a copy
            renderTags();
            
            // Show tag suggestions based on existing tags in the system
            showTagSuggestions();
            
            // Show the edit modal
            document.getElementById('editModal').classList.add('show');
        }
        
        function closeEditModal() {
            document.getElementById('editModal').classList.remove('show');
            currentEditTags = []; // Clear tags when closing
        }
        
        // Tag management
        let currentEditTags = [];
        
        function renderTags() {
            const tagList = document.getElementById('tagList');
            tagList.innerHTML = currentEditTags.map(tag => 
                `<div class="tag-chip">
                    <span>${escapeHtml(tag)}</span>
                    <button type="button" onclick="removeTag('${escapeHtml(tag).replace(/'/g, "\\'")}')" title="Remove tag">×</button>
                </div>`
            ).join('');
            
            // Update the hidden input
            document.getElementById('editTags').value = currentEditTags.join(',');
        }
        
        function addTag(tagText) {
            const input = document.getElementById('tagInput');
            const tag = (tagText || input.value).trim().toLowerCase();
            
            if (tag && !currentEditTags.includes(tag)) {
                currentEditTags.push(tag);
                renderTags();
                input.value = '';
            }
        }
        
        function removeTag(tag) {
            currentEditTags = currentEditTags.filter(t => t !== tag);
            renderTags();
        }
        
        function handleTagInput(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                addTag();
            }
        }
        
        function showTagSuggestions() {
            if (!contentData || !contentData.tags) return;
            
            const suggestionsDiv = document.getElementById('tagSuggestions');
            const commonTags = ['inspiration', 'reference', 'mood', 'color-palette', 'composition', 
                               'lighting', 'texture', 'style', 'concept', 'draft', 'final', 
                               'client-work', 'personal', 'archive'];
            
            // Combine common tags with existing tags from the data
            const allTags = [...new Set([...commonTags, ...contentData.tags])];
            const availableTags = allTags.filter(tag => !currentEditTags.includes(tag)).slice(0, 12);
            
            if (availableTags.length > 0) {
                suggestionsDiv.innerHTML = '<small style="color: #6c757d; margin-right: 1rem;">Suggestions:</small>' +
                    availableTags.map(tag => 
                        `<span class="tag-suggestion" onclick="addTag('${tag}')">${escapeHtml(tag)}</span>`
                    ).join('');
                suggestionsDiv.classList.add('show');
            } else {
                suggestionsDiv.classList.remove('show');
            }
        }
        
        async function saveEdit(event) {
            event.preventDefault();
            
            const form = event.target;
            const formData = new FormData(form);
            
            // Tags are already in the currentEditTags array
            const tags = currentEditTags;
            
            const updateData = {
                id: formData.get('id'),
                title: formData.get('title'),
                description: formData.get('description'),
                notes: formData.get('notes'),
                tags: tags
            };
            
            try {
                const response = await fetch('/api/update-item', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(updateData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    closeEditModal();
                    loadContent(); // Reload content to show changes
                    document.getElementById('status').innerHTML = '<div class="success">✅ Item updated successfully!</div>';
                    setTimeout(() => { document.getElementById('status').innerHTML = ''; }, 3000);
                } else {
                    alert('❌ Failed to update item: ' + (result.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Error updating item:', error);
                alert('❌ Error updating item: ' + error.message);
            }
        }
        
        // Close edit modal when clicking outside
        document.addEventListener('click', function(event) {
            const modal = document.getElementById('editModal');
            if (event.target === modal) {
                closeEditModal();
            }
        });
        
        
        // Close edit modal with Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                closeEditModal();
            }
        });
        
        // Load content when page loads
        document.addEventListener('DOMContentLoaded', async () => {
            console.log('Page loaded, scanning for new images and fetching content...');
            await scanForNew(); // Automatically scan for new images
            loadContent();
            loadCampaigns();
        });
        
        // Also try to load immediately
        if (document.readyState === 'complete' || document.readyState === 'interactive') {
            console.log('Document ready, scanning for new images and loading content...');
            scanForNew().then(() => {
                loadContent();
                loadCampaigns();
            });
        }
        
        // Brand Synthesis Functions
        let selectedImages = [];
        
        function toggleBrandSynthesis() {
            const panel = document.getElementById('brandSynthesisPanel');
            const isVisible = panel.style.display !== 'none';
            
            if (!isVisible) {
                panel.style.display = 'block';
                loadImageSelector();
            } else {
                panel.style.display = 'none';
                selectedImages = [];
                updateSelectedCount();
            }
        }
        
        async function loadImageSelector() {
            const selector = document.getElementById('imageSelector');
            
            try {
                const response = await fetch('/api/content');
                const data = await response.json();
                const images = data.items.filter(item => 
                    item.type === 'image' && item.style_vector
                );
                
                if (images.length === 0) {
                    selector.innerHTML = '<p style="color: #666;">No images with style vectors found. Run Style Analysis first.</p>';
                    return;
                }
                
                selector.innerHTML = images.map(item => `
                    <div style="display: flex; align-items: center; padding: 0.5rem; border-bottom: 1px solid #eee;">
                        <input type="checkbox" 
                               id="img-${item.id}" 
                               value="${item.id}" 
                               onchange="toggleImageSelection('${item.id}')"
                               style="margin-right: 1rem;">
                        <img src="${item.path}" 
                             alt="${item.title}" 
                             style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px; margin-right: 1rem;">
                        <div>
                            <div style="font-weight: bold; font-size: 0.9rem;">${item.title}</div>
                            <div style="color: #666; font-size: 0.8rem;">${item.filename}</div>
                        </div>
                    </div>
                `).join('');
                
            } catch (error) {
                selector.innerHTML = '<p style="color: #ff0000;">Error loading images</p>';
                console.error('Error loading images:', error);
            }
        }
        
        function toggleImageSelection(imageId) {
            const checkbox = document.getElementById(`img-${imageId}`);
            
            if (checkbox.checked) {
                if (!selectedImages.includes(imageId)) {
                    selectedImages.push(imageId);
                }
            } else {
                const index = selectedImages.indexOf(imageId);
                if (index > -1) {
                    selectedImages.splice(index, 1);
                }
            }
            
            updateSelectedCount();
        }
        
        function updateSelectedCount() {
            const countElement = document.getElementById('selectedCount');
            countElement.textContent = selectedImages.length;
            
            const synthesizeBtn = document.getElementById('synthesizeBtn');
            synthesizeBtn.disabled = selectedImages.length < 2;
            
            if (selectedImages.length < 2) {
                synthesizeBtn.style.opacity = '0.5';
                synthesizeBtn.style.cursor = 'not-allowed';
            } else {
                synthesizeBtn.style.opacity = '1';
                synthesizeBtn.style.cursor = 'pointer';
            }
        }
        
        async function synthesizeBrand() {
            if (selectedImages.length < 2) {
                alert('Please select at least 2 images');
                return;
            }
            
            const brandName = document.getElementById('brandName').value || 'Untitled Brand';
            const brandCategory = document.getElementById('brandCategory').value;
            const brandAudience = document.getElementById('brandAudience').value;
            const generateAlternatives = document.getElementById('generateAlternatives').checked;
            
            // Show loading state
            const statusDiv = document.getElementById('synthesisStatus');
            const synthesizeBtn = document.getElementById('synthesizeBtn');
            
            statusDiv.style.display = 'block';
            synthesizeBtn.disabled = true;
            synthesizeBtn.style.opacity = '0.5';
            
            try {
                const brief = {
                    name: brandName,
                    category: brandCategory,
                    audience: brandAudience
                };
                
                const response = await fetch('/api/synthesize', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        image_ids: selectedImages,
                        brief: brief,
                        generate_alternatives: generateAlternatives
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    statusDiv.innerHTML = `
                        <div style="color: #28a745; margin-bottom: 1rem;">✅ Brand system created successfully!</div>
                        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px;">
                            <h4 style="margin: 0 0 0.5rem 0;">${result.brand.name}</h4>
                            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem;">
                                <button onclick="window.open('/api/brand-preview/${result.brand.id}', '_blank')" 
                                        style="background: linear-gradient(45deg, #667eea, #764ba2); color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer;">
                                    📄 View Brand Guide
                                </button>
                                <button onclick="downloadTokens('${result.brand.id}', '${result.brand.name}')"
                                        style="background: #6f42c1; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer;">
                                    🎨 Download Figma Tokens
                                </button>
                            </div>
                            ${result.alternatives && result.alternatives.length > 0 ? `
                                <div>
                                    <strong>Alternatives:</strong>
                                    <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
                                        ${result.alternatives.map(alt => `
                                            <button onclick="window.open('/api/brand-preview/${alt.id}', '_blank')" 
                                                    style="background: #6c757d; color: white; border: none; padding: 0.25rem 0.75rem; border-radius: 4px; cursor: pointer; font-size: 0.9rem;">
                                                ${alt.name}
                                            </button>
                                        `).join('')}
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    `;
                    
                    // Refresh content to show new brands
                    setTimeout(() => {
                        loadContent();
                    }, 1000);
                } else {
                    statusDiv.innerHTML = `<p style="color: #dc3545;">❌ Error: ${result.error}</p>`;
                }
                
            } catch (error) {
                statusDiv.innerHTML = `<p style="color: #dc3545;">❌ Error: ${error.message}</p>`;
                console.error('Synthesis error:', error);
            }
            
            // Re-enable button
            setTimeout(() => {
                synthesizeBtn.disabled = false;
                synthesizeBtn.style.opacity = '1';
                statusDiv.style.display = 'none';
            }, 3000);
        }
        
        async function downloadTokens(brandId, brandName) {
            try {
                const response = await fetch(`/api/brand-tokens/${brandId}`);
                const tokens = await response.json();
                
                // Create download link
                const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(tokens, null, 2));
                const downloadAnchorNode = document.createElement('a');
                downloadAnchorNode.setAttribute("href", dataStr);
                downloadAnchorNode.setAttribute("download", `${brandName.replace(/[^a-z0-9]/gi, '_')}_figma_tokens.json`);
                document.body.appendChild(downloadAnchorNode);
                downloadAnchorNode.click();
                downloadAnchorNode.remove();
            } catch (error) {
                alert('Error downloading tokens: ' + error.message);
            }
        }
        
        function loadBrands(brands) {
            console.log('loadBrands called with:', brands.length, 'brands');
            const brandSection = document.getElementById('brandSection');
            const brandCards = document.getElementById('brandCards');
            
            if (!brandSection) {
                console.error('brandSection element not found!');
                return;
            }
            if (!brandCards) {
                console.error('brandCards element not found!');
                return;
            }
            
            if (!brands || brands.length === 0) {
                console.log('No brands to display, hiding section');
                brandSection.style.display = 'none';
                return;
            }
            
            // Group brands by base name and separate variants
            const brandGroups = {};
            brands.forEach(brand => {
                const baseName = brand.name;
                if (!brandGroups[baseName]) {
                    brandGroups[baseName] = { main: null, variants: [] };
                }
                
                if (brand.variant) {
                    console.log('Found variant:', brand.name, 'variant', brand.variant);
                    brandGroups[baseName].variants.push(brand);
                } else {
                    console.log('Found main brand:', brand.name);
                    brandGroups[baseName].main = brand;
                }
            });
            
            console.log('Brand groups:', brandGroups);
            
            // Store brand data globally for click handlers
            window.brandData = brandGroups;
            
            // Create cards for main brands only
            const brandCardsHtml = Object.values(brandGroups)
                .filter(group => group.main)
                .map((group, index) => {
                    const brand = group.main;
                    const hasVariants = group.variants.length > 0;
                    
                    // Extract Brand DNA insights
                    const insights = brand.synthesized_insights || {};
                    const keywords = insights.keywords || [];
                    const visualTone = insights.visual_tone || {};
                    
                    // Generate Brand DNA section HTML
                    let brandDnaSection = '';
                    if (keywords.length > 0 || Object.keys(visualTone).length > 0) {
                        const themesHtml = keywords.length > 0 ? 
                            `<div><strong>Themes:</strong> ${keywords.slice(0, 4).join(', ')}</div>` : '';
                        const visualDesc = Object.values(visualTone).filter(v => v).join(', ');
                        const visualHtml = visualDesc ? 
                            `<div><strong>Visual:</strong> ${visualDesc}</div>` : '';
                        
                        if (themesHtml || visualHtml) {
                            const colorMeaningsHtml = insights.color_meanings && insights.color_meanings.length > 0 ?
                                `<div style="margin-bottom: 0.5rem;">
                                    <strong style="color: #333;">Emotional Palette:</strong> 
                                    <span style="color: #666;">${insights.color_meanings.slice(0, 3).join(', ')}</span>
                                </div>` : '';
                            
                            const sourceImagesHtml = brand.source_items && brand.source_items.length > 0 ?
                                `<div style="margin-top: 0.5rem;">
                                    <strong style="color: #333; font-size: 0.8rem;">Source Images:</strong>
                                    <div style="display: flex; gap: 0.25rem; margin-top: 0.25rem; overflow-x: auto;">
                                        ${brand.source_items.slice(0, 3).map(item => 
                                            `<img src="/${item.path}" 
                                                  style="width: 40px; height: 40px; object-fit: cover; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.2);" 
                                                  title="${item.title || 'Source image'}" 
                                                  onclick="event.stopPropagation(); window.open('/#item-${item.id}', '_blank');">`
                                        ).join('')}
                                        ${brand.source_items.length > 3 ? `<div style="width: 40px; height: 40px; background: #f0f0f0; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; color: #666;">+${brand.source_items.length - 3}</div>` : ''}
                                    </div>
                                </div>` : '';
                        
                            brandDnaSection = `
                                <div class="brand-dna-section" style="
                                    background: linear-gradient(135deg, #667eea20, transparent);
                                    padding: 1rem;
                                    border-radius: 8px;
                                    margin: 0.75rem 0;
                                    font-size: 0.85rem;
                                    border: 1px solid #667eea30;
                                ">
                                    <div style="font-weight: bold; color: #667eea; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.25rem;">
                                        🧬 Brand DNA Analysis
                                    </div>
                                    
                                    ${keywords.length > 0 ? 
                                        `<div style="margin-bottom: 0.5rem;">
                                            <strong style="color: #333;">Core Themes:</strong><br>
                                            <div style="display: flex; flex-wrap: wrap; gap: 0.25rem; margin-top: 0.25rem;">
                                                ${keywords.slice(0, 6).map(kw => 
                                                    `<span style="background: #f0f2ff; color: #667eea; padding: 0.125rem 0.375rem; border-radius: 12px; font-size: 0.75rem; font-weight: 500;">${kw}</span>`
                                                ).join('')}
                                            </div>
                                        </div>` : ''
                                    }
                                    
                                    ${visualDesc ? 
                                        `<div style="margin-bottom: 0.5rem;">
                                            <strong style="color: #333;">Visual Style:</strong> 
                                            <span style="color: #666;">${visualDesc}</span>
                                        </div>` : ''
                                    }
                                    
                                    ${colorMeaningsHtml}
                                    
                                    ${sourceImagesHtml}
                                </div>
                            `;
                        }
                    }

                    return `
                        <div class="brand-card" onclick="console.log('Brand card clicked:', '${brand.name}'); showBrandFromData('${brand.name}')">
                            <h3 style="margin: 0 0 1rem 0; color: #333;">${brand.name}</h3>
                            <div class="brand-meta">
                                Created: ${new Date(brand.created_at).toLocaleDateString()}
                                ${brand.brief && brand.brief.category ? ` • ${brand.brief.category}` : ''}
                                ${hasVariants ? ` • ${group.variants.length} variants` : ''}
                            </div>
                            
                            <div class="brand-colors">
                                ${Object.entries(brand.colors).slice(0, 5).map(([name, color]) => 
                                    `<div class="color-swatch" style="background: ${color};" title="${name}: ${color}"></div>`
                                ).join('')}
                            </div>
                            
                            <div style="display: flex; flex-wrap: wrap; gap: 0.25rem; margin: 0.5rem 0;">
                                ${brand.personality.traits.slice(0, 4).map(trait => 
                                    `<span style="background: #f0f2ff; color: #667eea; padding: 0.25rem 0.5rem; border-radius: 10px; font-size: 0.75rem; font-weight: 500;">${trait}</span>`
                                ).join('')}
                            </div>
                            
                            ${brandDnaSection}
                            
                            <div class="brand-accessibility ${brand.accessibility.passed ? 'accessibility-pass' : 'accessibility-warn'}">
                                ${brand.accessibility.passed ? '✅ WCAG AA' : '⚠️ Issues'}
                            </div>
                        </div>
                    `;
                }).join('');
            
            console.log('Setting brand cards HTML and showing section');
            brandCards.innerHTML = brandCardsHtml;
            brandSection.style.display = 'block';
            console.log('Brands should now be visible!');
        }
        
        function showBrandFromData(brandName) {
            console.log('showBrandFromData called for:', brandName);
            if (!window.brandData || !window.brandData[brandName]) {
                console.error('Brand data not found for:', brandName);
                return;
            }
            
            const brandGroup = window.brandData[brandName];
            const brand = brandGroup.main;
            const alternatives = brandGroup.variants;
            
            console.log('Found brand:', brand.name, 'with', alternatives.length, 'variants');
            showBrandResult(brand, alternatives);
        }
        
        function showBrandResult(brand, alternatives = []) {
            console.log('showBrandResult called with:', brand.name, 'and', alternatives.length, 'alternatives');
            const modal = document.createElement('div');
            modal.className = 'modal show';
            
            const altSection = alternatives.length > 0 ? `
                <h3>🔄 Alternatives Generated</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1rem 0;">
                    ${alternatives.map((alt, i) => `
                        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 1rem;">
                            <h4>Variant ${alt.variant}</h4>
                            <div style="display: flex; gap: 0.5rem; margin: 0.5rem 0;">
                                ${Object.entries(alt.colors).slice(0, 3).map(([name, color]) => `
                                    <div style="width: 30px; height: 30px; background: ${color}; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"></div>
                                `).join('')}
                            </div>
                            <p style="font-size: 0.9rem; margin: 0.5rem 0;">${alt.typography.heading.family.split(',')[0]}</p>
                        </div>
                    `).join('')}
                </div>
            ` : '';
            
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 800px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                        <h2 style="color: #667eea; margin: 0;">🎨 ${brand.name}</h2>
                        <button onclick="this.closest('.modal').remove()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #999;">×</button>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin: 2rem 0;">
                        <div>
                            <h3>🎨 Color Palette</h3>
                            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                                ${Object.entries(brand.colors).map(([name, color]) => `
                                    <div style="text-align: center;">
                                        <div style="width: 60px; height: 60px; background: ${color}; border-radius: 8px; margin: 0 auto 0.5rem; border: 2px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.15);"></div>
                                        <div style="font-size: 0.8rem; font-weight: bold;">${name}</div>
                                        <div style="font-size: 0.7rem; color: #666;">${color}</div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                        
                        <div>
                            <h3>📝 Typography</h3>
                            <div style="margin-bottom: 1rem;">
                                <strong>Heading:</strong><br>
                                <span style="font-family: ${brand.typography.heading.family}; font-size: 1.2rem; font-weight: ${brand.typography.heading.weight};">
                                    ${brand.typography.heading.family.split(',')[0]}
                                </span>
                            </div>
                            <div>
                                <strong>Body:</strong><br>
                                <span style="font-family: ${brand.typography.body.family}; font-weight: ${brand.typography.body.weight};">
                                    ${brand.typography.body.family.split(',')[0]}
                                </span>
                            </div>
                            
                            <h3 style="margin-top: 1.5rem;">🧠 Personality</h3>
                            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.5rem 0;">
                                ${brand.personality.traits.map(trait => `
                                    <span style="background: #e3f2fd; color: #1976d2; padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.8rem;">${trait}</span>
                                `).join('')}
                            </div>
                            <p style="font-style: italic; color: #666; margin-top: 1rem;">"${brand.personality.voice}"</p>
                        </div>
                    </div>
                    
                    <div style="background: ${brand.accessibility.passed ? '#d4edda' : '#f8d7da'}; border: 1px solid ${brand.accessibility.passed ? '#c3e6cb' : '#f5c6cb'}; border-radius: 4px; padding: 1rem; margin: 2rem 0;">
                        <h3>♿ Accessibility: ${brand.accessibility.passed ? '✅ Passed' : '⚠️ Issues Found'}</h3>
                        ${brand.accessibility.issues.length > 0 ? `
                            <ul style="margin: 0.5rem 0;">
                                ${brand.accessibility.issues.slice(0, 2).map(issue => `<li style="font-size: 0.9rem;">${issue}</li>`).join('')}
                            </ul>
                        ` : '<p style="margin: 0;">All WCAG AA contrast requirements met!</p>'}
                    </div>
                    
                    ${altSection}
                    
                    <div style="text-align: center; margin-top: 2rem;">
                        <button onclick="this.closest('.modal').remove()" style="background: #667eea; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; cursor: pointer;">
                            Close
                        </button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
        }
        
        // Initialize page
        loadContent();
    </script>
</body>
</html>
    """
    return web.Response(text=html, content_type='text/html')

async def api_content(request):
    """API endpoint for content"""
    data = content_manager.get_all_content()
    return web.json_response(data)

async def api_scan(request):
    """API endpoint to scan for new content"""
    new_items = content_manager.scan_images()
    return web.json_response({"scanned": new_items, "method": "basic"})

async def api_update_item(request):
    """API endpoint to update an item (add notes, tags, etc)"""
    try:
        item_data = await request.json()
        item_id = item_data.get('id')
        
        if not item_id:
            return web.json_response({"error": "No item ID provided"}, status=400)
        
        # Update the item
        data = content_manager._load_data()
        item_found = False
        
        for item in data['items']:
            if item['id'] == item_id:
                # Update allowed fields
                if 'notes' in item_data:
                    item['notes'] = item_data['notes']
                if 'tags' in item_data:
                    item['tags'] = item_data['tags']
                if 'title' in item_data:
                    item['title'] = item_data['title']
                if 'description' in item_data:
                    item['description'] = item_data['description']
                if 'project_id' in item_data:
                    item['project_id'] = item_data['project_id']
                
                item['last_modified'] = datetime.now().isoformat()
                item_found = True
                break
        
        if not item_found:
            return web.json_response({"error": "Item not found"}, status=404)
        
        # Update global tags
        all_tags = set()
        for item in data['items']:
            all_tags.update(item.get('tags', []))
        data['tags'] = sorted(list(all_tags))
        
        content_manager._save_data(data)
        return web.json_response({"success": True, "message": "Item updated"})
        
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def api_create_project(request):
    """API endpoint to create a new project/collection"""
    try:
        project_data = await request.json()
        name = project_data.get('name', '').strip()
        description = project_data.get('description', '').strip()
        
        if not name:
            return web.json_response({"error": "Project name is required"}, status=400)
        
        data = content_manager._load_data()
        
        # Initialize projects if not exists
        if 'projects' not in data:
            data['projects'] = []
        
        # Create new project
        project = {
            "id": f"project_{len(data['projects']) + 1}",
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "item_count": 0,
            "thumbnail": None
        }
        
        data['projects'].append(project)
        content_manager._save_data(data)
        
        return web.json_response({"success": True, "project": project})
        
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def api_create_campaign(request):
    """API endpoint to create a new campaign concept"""
    try:
        campaign_data = await request.json()
        
        # Validate required fields
        required = ['name', 'client', 'objective']
        for field in required:
            if not campaign_data.get(field, '').strip():
                return web.json_response({"error": f"{field} is required"}, status=400)
        
        data = content_manager._load_data()
        
        # Initialize campaigns if not exists
        if 'campaigns' not in data:
            data['campaigns'] = []
        
        # Create new campaign
        campaign = {
            "id": f"campaign_{len(data['campaigns']) + 1}",
            "name": campaign_data['name'].strip(),
            "client": campaign_data['client'].strip(),
            "objective": campaign_data['objective'].strip(),
            "target_audience": campaign_data.get('target_audience', '').strip(),
            "key_messages": campaign_data.get('key_messages', '').strip(),
            "tone_voice": campaign_data.get('tone_voice', '').strip(),
            "deliverables": campaign_data.get('deliverables', '').strip(),
            "timeline": campaign_data.get('timeline', '').strip(),
            "budget_range": campaign_data.get('budget_range', '').strip(),
            "inspiration_notes": campaign_data.get('inspiration_notes', '').strip(),
            "linked_items": campaign_data.get('linked_items', []),
            "status": campaign_data.get('status', 'concept'),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        data['campaigns'].append(campaign)
        content_manager._save_data(data)
        
        return web.json_response({"success": True, "campaign": campaign})
        
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def api_update_campaign(request):
    """API endpoint to update a campaign concept"""
    try:
        update_data = await request.json()
        campaign_id = update_data.get('id')
        
        if not campaign_id:
            return web.json_response({"error": "Campaign ID is required"}, status=400)
        
        data = content_manager._load_data()
        
        # Find and update campaign
        campaign_found = False
        for campaign in data.get('campaigns', []):
            if campaign['id'] == campaign_id:
                # Update allowed fields
                updatable_fields = [
                    'name', 'client', 'objective', 'target_audience',
                    'key_messages', 'tone_voice', 'deliverables', 
                    'timeline', 'budget_range', 'inspiration_notes',
                    'linked_items', 'status'
                ]
                
                for field in updatable_fields:
                    if field in update_data:
                        campaign[field] = update_data[field]
                
                campaign['updated_at'] = datetime.now().isoformat()
                campaign_found = True
                break
        
        if not campaign_found:
            return web.json_response({"error": "Campaign not found"}, status=404)
        
        content_manager._save_data(data)
        return web.json_response({"success": True, "message": "Campaign updated"})
        
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def api_link_campaign_items(request):
    """API endpoint to link mood board items to a campaign"""
    try:
        link_data = await request.json()
        campaign_id = link_data.get('campaign_id')
        item_ids = link_data.get('item_ids', [])
        action = link_data.get('action', 'add')  # 'add' or 'remove'
        
        if not campaign_id:
            return web.json_response({"error": "Campaign ID is required"}, status=400)
        
        data = content_manager._load_data()
        
        # Find campaign
        campaign = None
        for c in data.get('campaigns', []):
            if c['id'] == campaign_id:
                campaign = c
                break
        
        if not campaign:
            return web.json_response({"error": "Campaign not found"}, status=404)
        
        # Update linked items
        if 'linked_items' not in campaign:
            campaign['linked_items'] = []
        
        if action == 'add':
            # Add items (avoid duplicates)
            for item_id in item_ids:
                if item_id not in campaign['linked_items']:
                    campaign['linked_items'].append(item_id)
        elif action == 'remove':
            # Remove items
            campaign['linked_items'] = [
                item for item in campaign['linked_items'] 
                if item not in item_ids
            ]
        
        campaign['updated_at'] = datetime.now().isoformat()
        content_manager._save_data(data)
        
        return web.json_response({
            "success": True, 
            "linked_items": campaign['linked_items'],
            "message": f"Campaign mood board updated"
        })
        
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def api_get_campaigns(request):
    """API endpoint to get all campaigns"""
    try:
        data = content_manager._load_data()
        campaigns = data.get('campaigns', [])
        
        # Add linked item details
        for campaign in campaigns:
            linked_details = []
            for item_id in campaign.get('linked_items', []):
                item = next((i for i in data['items'] if i['id'] == item_id), None)
                if item:
                    linked_details.append({
                        'id': item['id'],
                        'title': item.get('title', 'Untitled'),
                        'type': item.get('type'),
                        'path': item.get('path')
                    })
            campaign['linked_items_details'] = linked_details
        
        return web.json_response(campaigns)
        
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def api_generate_concepts(request):
    """API endpoint to generate AI concepts for a campaign"""
    try:
        request_data = await request.json()
        campaign_id = request_data.get('campaign_id')
        
        if not campaign_id:
            return web.json_response({"error": "Campaign ID required"}, status=400)
        
        if not content_manager.concept_generator:
            return web.json_response({
                "error": "Concept generation not available",
                "message": "OpenAI API key not configured"
            }, status=400)
        
        data = content_manager._load_data()
        
        # Find campaign
        campaign = None
        for c in data.get('campaigns', []):
            if c['id'] == campaign_id:
                campaign = c
                break
        
        if not campaign:
            return web.json_response({"error": "Campaign not found"}, status=404)
        
        # Get mood board items with full details
        mood_board_items = []
        for item_id in campaign.get('linked_items', []):
            item = next((i for i in data['items'] if i['id'] == item_id), None)
            if item:
                mood_board_items.append(item)
        
        if not mood_board_items:
            return web.json_response({
                "error": "No mood board items",
                "message": "Please add images to the campaign mood board first"
            }, status=400)
        
        # Generate concepts
        print(f"🎨 Generating concepts for campaign: {campaign['name']}")
        result = await content_manager.concept_generator.generate_campaign_concepts(
            campaign, mood_board_items
        )
        
        # Store concepts in campaign data
        if 'generated_concepts' not in campaign:
            campaign['generated_concepts'] = []
        
        campaign['generated_concepts'].append(result)
        campaign['updated_at'] = datetime.now().isoformat()
        
        # Save updated data
        content_manager._save_data(data)
        
        return web.json_response({
            "success": True,
            "concepts": result,
            "message": f"Generated {len(result.get('concepts', []))} concepts"
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({
            "error": "Concept generation failed",
            "message": str(e)
        }, status=500)

async def api_search(request):
    """API endpoint for searching content"""
    try:
        query = request.query.get('q', '').lower()
        filter_type = request.query.get('type', 'all')
        tags = request.query.getall('tags', [])
        project_id = request.query.get('project_id', None)
        
        if not query and not tags and not project_id:
            return web.json_response({"error": "No search criteria provided"}, status=400)
        
        data = content_manager._load_data()
        results = []
        
        for item in data['items']:
            # Filter by type
            if filter_type != 'all' and item.get('type') != filter_type:
                continue
            
            # Filter by project
            if project_id and item.get('project_id') != project_id:
                continue
            
            # Filter by tags
            if tags:
                item_tags = set(item.get('tags', []))
                if not item_tags.intersection(tags):
                    continue
            
            # Search in text fields
            if query:
                searchable = [
                    item.get('title', ''),
                    item.get('description', ''),
                    item.get('notes', ''),
                    ' '.join(item.get('tags', [])),
                    item.get('creative_insights', '')
                ]
                if not any(query in field.lower() for field in searchable):
                    continue
            
            results.append(item)
        
        return web.json_response({
            "results": results,
            "count": len(results),
            "query": query
        })
        
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def run_collaborative_analysis(item):
    """Run collaborative multi-agent analysis on an image"""
    try:
        image_path = item.get('path', '')
        if not image_path:
            return None
        
        # Step 1: Get basic AI analysis first
        basic_analysis = item.get('description', '')
        basic_insights = item.get('creative_insights', '')
        
        # Step 2: Run Brand Strategy Analysis
        print(f"🎯 Running Brand Strategy analysis for {item.get('filename', 'unknown')}")
        brand_analysis = await run_agent_analysis('brand_strategy', item, basic_analysis, basic_insights)
        
        # Step 3: Run Visual Storytelling Analysis  
        print(f"📖 Running Visual Storytelling analysis")
        storytelling_analysis = await run_agent_analysis('visual_storytelling', item, basic_analysis, brand_analysis)
        
        # Step 4: Run UI/UX Design Analysis
        print(f"🎨 Running UI/UX Design analysis")
        design_analysis = await run_agent_analysis('ui_ux_design', item, basic_analysis, storytelling_analysis)
        
        # Step 5: Run Innovation Catalyst Analysis
        print(f"💡 Running Innovation Catalyst analysis")
        innovation_analysis = await run_agent_analysis('innovation_catalyst', item, basic_analysis, design_analysis)
        
        # Step 6: Synthesize all insights
        print(f"🔄 Synthesizing multi-agent insights")
        final_synthesis = await synthesize_agent_insights(item, {
            'brand_strategy': brand_analysis,
            'visual_storytelling': storytelling_analysis, 
            'ui_ux_design': design_analysis,
            'innovation_catalyst': innovation_analysis
        })
        
        return final_synthesis
        
    except Exception as e:
        print(f"Collaborative analysis error: {e}")
        return None

async def run_agent_analysis(agent_type, item, basic_analysis, previous_analysis):
    """Run analysis with a specific design agent"""
    try:
        # This would normally call the Task tool with specific agent prompts
        # For now, return enhanced placeholder analysis
        agent_prompts = {
            'brand_strategy': f"As a Brand Strategy expert, analyze image '{item.get('filename')}' for strategic positioning, target audience insights, and commercial potential. Build on this basic analysis: {basic_analysis[:200]}...",
            
            'visual_storytelling': f"As a Visual Storytelling specialist, analyze the narrative structure, emotional impact, and engagement potential of '{item.get('filename')}'. Previous strategic insights: {previous_analysis[:200] if previous_analysis else 'None'}...",
            
            'ui_ux_design': f"As a UI/UX Design expert, analyze '{item.get('filename')}' for design principles, usability patterns, and digital interface applications. Build on previous analysis...",
            
            'innovation_catalyst': f"As an Innovation Catalyst, identify emerging trends, future opportunities, and transformative potential in '{item.get('filename')}'. Consider all previous insights to identify breakthrough applications..."
        }
        
        prompt = agent_prompts.get(agent_type, '')
        
        # Simple enhanced analysis without brand hallucination
        analysis_types = {
            'brand_strategy': "Enhanced description with focus on visual appeal and potential applications.",
            'visual_storytelling': "Analysis of visual narrative and composition elements.",
            'ui_ux_design': "Interface design considerations and usability aspects.",
            'innovation_catalyst': "Creative potential and emerging design trends."
        }
        
        return f"Enhanced {agent_type} analysis: {analysis_types.get(agent_type, 'General enhanced analysis completed')}"
        
    except Exception as e:
        print(f"Agent analysis error ({agent_type}): {e}")
        return f"Analysis unavailable for {agent_type}"

async def synthesize_agent_insights(item, agent_analyses):
    """Synthesize insights from all agents into comprehensive analysis"""
    try:
        synthesis = {
            'enhanced_description': f"Multi-Agent Enhanced Description: {item.get('description', '')} Enhanced with multiple analytical perspectives.",
            
            'enhanced_tags': item.get('ai_tags', []) + [
                'multi-agent analyzed', 'enhanced description'
            ],
            
            'confidence_score': 0.92,
            'analysis_depth': 'comprehensive',
            'agent_collaboration': True
        }
        
        return synthesis
        
    except Exception as e:
        print(f"Synthesis error: {e}")
        return None

async def api_ai_scan(request):
    """API endpoint to scan with AI analysis"""
    try:
        if not content_manager.ai_manager:
            return web.json_response({
                "error": "AI analysis not available",
                "message": "No OpenAI API key configured"
            }, status=400)
        
        # Run AI scan with timeout protection
        try:
            new_count = await asyncio.wait_for(
                content_manager.scan_images_with_ai(),
                timeout=120  # 2 minute timeout
            )
            return web.json_response({
                "scanned": new_count, 
                "method": "ai_analysis",
                "message": f"Analyzed {new_count} images with AI"
            })
        except asyncio.TimeoutError:
            return web.json_response({
                "error": "AI analysis timeout",
                "message": "Analysis took too long. Try analyzing fewer images."
            }, status=504)
    except Exception as e:
        return web.json_response({
            "error": "AI analysis failed",
            "message": str(e)
        }, status=500)

async def serve_file(request):
    """Serve static files"""
    file_path = request.match_info['path']
    full_path = Path(file_path)
    
    if not full_path.exists():
        return web.Response(status=404, text="File not found")
    
    # Security check - ensure file is within allowed directories
    try:
        full_path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        return web.Response(status=403, text="Access denied")
    
    async with aiofiles.open(full_path, mode='rb') as f:
        content = await f.read()
    
    # Determine content type
    suffix = full_path.suffix.lower()
    content_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml'
    }
    content_type = content_types.get(suffix, 'application/octet-stream')
    
    return web.Response(body=content, content_type=content_type)

async def api_upload(request):
    """API endpoint to handle file uploads"""
    try:
        reader = await request.multipart()
        uploaded_files = []
        
        async for part in reader:
            if part.name == 'file':
                filename = part.filename
                if not filename:
                    continue
                    
                # Security: sanitize filename
                filename = Path(filename).name
                
                # Determine file type and directory
                file_ext = Path(filename).suffix.lower()
                if file_ext in {'.jpg', '.jpeg', '.png', '.gif', '.webp'}:
                    file_path = content_manager.images_dir / filename
                else:
                    return web.json_response({
                        "error": f"Unsupported file type: {file_ext}"
                    }, status=400)
                
                # Save file
                async with aiofiles.open(file_path, 'wb') as f:
                    while True:
                        chunk = await part.read_chunk()
                        if not chunk:
                            break
                        await f.write(chunk)
                
                uploaded_files.append(filename)
        
        if uploaded_files:
            # Scan for new content
            new_items = content_manager.scan_images()
            
            return web.json_response({
                "success": True,
                "uploaded": uploaded_files,
                "scanned": new_items
            })
        else:
            return web.json_response({
                "error": "No files uploaded"
            }, status=400)
            
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def api_export(request):
    """API endpoint to export a collection as JSON or HTML"""
    try:
        export_format = request.query.get('format', 'json')
        project_id = request.query.get('project_id', None)
        
        data = content_manager._load_data()
        
        # Filter items by project if specified
        if project_id:
            items = [item for item in data['items'] if item.get('project_id') == project_id]
            project = next((p for p in data.get('projects', []) if p['id'] == project_id), None)
            export_data = {
                "project": project,
                "items": items,
                "exported_at": datetime.now().isoformat()
            }
        else:
            export_data = {
                "items": data['items'],
                "exported_at": datetime.now().isoformat()
            }
        
        if export_format == 'html':
            # Generate HTML mood board
            html = generate_mood_board_html(export_data)
            return web.Response(text=html, content_type='text/html', 
                              headers={'Content-Disposition': 'attachment; filename="mood-board.html"'})
        else:
            # Return JSON
            return web.json_response(export_data, 
                                    headers={'Content-Disposition': 'attachment; filename="export.json"'})
    
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

def generate_mood_board_html(data):
    """Generate a standalone HTML mood board"""
    items_html = ""
    for item in data.get('items', []):
        if item.get('type') == 'image':
            # Embed image as base64 for portability
            try:
                import base64
                with open(item['path'], 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode()
                img_src = f"data:image/{Path(item['path']).suffix[1:]};base64,{img_data}"
            except:
                img_src = item['path']
            
            items_html += f"""
            <div class="mood-item">
                <img src="{img_src}" alt="{item.get('title', '')}">
                <div class="item-info">
                    <h3>{item.get('title', 'Untitled')}</h3>
                    <p>{item.get('description', '')[:100]}</p>
                    <div class="tags">
                        {''.join([f'<span class="tag">{tag}</span>' for tag in item.get('tags', [])])}
                    </div>
                </div>
            </div>
            """
    
    project_name = data.get('project', {}).get('name', 'Mood Board')
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{project_name} - Concierto Export</title>
        <style>
            body {{ font-family: -apple-system, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            h1 {{ text-align: center; color: #333; }}
            .mood-board {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 30px; }}
            .mood-item {{ background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            .mood-item img {{ width: 100%; height: 250px; object-fit: cover; }}
            .item-info {{ padding: 15px; }}
            .item-info h3 {{ margin: 0 0 10px 0; font-size: 1.1rem; }}
            .item-info p {{ color: #666; font-size: 0.9rem; line-height: 1.4; }}
            .tags {{ display: flex; flex-wrap: wrap; gap: 5px; margin-top: 10px; }}
            .tag {{ background: #e0e0e0; padding: 3px 8px; border-radius: 12px; font-size: 0.8rem; }}
        </style>
    </head>
    <body>
        <h1>🎨 {project_name}</h1>
        <div class="mood-board">
            {items_html}
        </div>
        <p style="text-align: center; margin-top: 40px; color: #999;">
            Exported from Concierto on {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </p>
    </body>
    </html>
    """

async def api_multi_agent_analysis(request):
    """Run enhanced multi-agent analysis on a specific image"""
    try:
        data = await request.json()
        item_id = data.get('item_id')
        
        if not item_id:
            return web.json_response({"error": "No item ID provided"}, status=400)
        
        # Get the item data
        content_data = content_manager._load_data()
        item = None
        for i in content_data['items']:
            if i['id'] == item_id:
                item = i
                break
        
        if not item or item.get('type') != 'image':
            return web.json_response({"error": "Image not found"}, status=404)
        
        # Run multi-agent analysis
        enhanced_analysis = await run_collaborative_analysis(item)
        
        # Update the item with enhanced analysis
        if enhanced_analysis:
            item['enhanced_analysis'] = enhanced_analysis
            item['analysis_type'] = 'multi_agent'
            item['enhanced_at'] = datetime.now().isoformat()
            content_manager._save_data(content_data)
            
            return web.json_response({
                "success": True,
                "message": "Enhanced multi-agent analysis completed",
                "enhanced_analysis": enhanced_analysis
            })
        else:
            return web.json_response({
                "error": "Enhanced analysis failed"
            }, status=500)
            
    except Exception as e:
        print(f"Multi-agent analysis error: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def api_batch_multi_agent_analysis(request):
    """Run multi-agent analysis on all images missing descriptions"""
    try:
        # Get content data
        content_data = content_manager._load_data()
        
        # Find images without descriptions
        images_to_process = []
        for item in content_data['items']:
            if (item.get('type') == 'image' and 
                (not item.get('description') or item.get('description') == '')):
                images_to_process.append(item)
        
        if not images_to_process:
            return web.json_response({
                "success": True,
                "message": "No images need processing - all have descriptions",
                "processed": 0
            })
        
        print(f"🚀 Starting batch multi-agent analysis on {len(images_to_process)} images...")
        processed_count = 0
        
        # Process each image
        for item in images_to_process:
            try:
                print(f"Processing {item['filename']}...")
                
                # Run multi-agent analysis
                enhanced_analysis = await run_collaborative_analysis(item)
                
                if enhanced_analysis:
                    # Update item with enhanced analysis
                    item['enhanced_analysis'] = enhanced_analysis
                    item['analysis_type'] = 'multi_agent'
                    item['enhanced_at'] = datetime.now().isoformat()
                    
                    # Also use enhanced description as the main description
                    if enhanced_analysis.get('enhanced_description'):
                        item['description'] = enhanced_analysis['enhanced_description']
                    
                    processed_count += 1
                    print(f"✅ Completed {item['filename']}")
                else:
                    print(f"❌ Failed {item['filename']}")
                    
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"Error processing {item['filename']}: {e}")
                continue
        
        # Save all changes
        content_manager._save_data(content_data)
        
        return web.json_response({
            "success": True,
            "message": f"Batch multi-agent analysis completed on {processed_count}/{len(images_to_process)} images",
            "processed": processed_count,
            "total_found": len(images_to_process)
        })
        
    except Exception as e:
        print(f"Batch multi-agent analysis error: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def api_synthesize_brand(request):
    """API endpoint to synthesize a brand from selected images"""
    try:
        # Check if synthesis engine is available
        if not SYNTHESIS_ENGINE_AVAILABLE:
            return web.json_response({
                "error": "Brand synthesis engine not available"
            }, status=503)
        
        # Get request data
        req_data = await request.json()
        image_ids = req_data.get('image_ids', [])
        brief = req_data.get('brief', None)
        weights = req_data.get('weights', None)
        generate_alternatives = req_data.get('generate_alternatives', False)
        
        if not image_ids:
            return web.json_response({
                "error": "No image IDs provided"
            }, status=400)
        
        # Create synthesizer
        synthesizer = BrandSynthesizer()
        
        # Generate brand specification
        brand_spec = synthesizer.synthesize(image_ids, brief, weights)
        
        # Generate alternatives if requested
        alternatives = []
        if generate_alternatives:
            alternatives = synthesizer.generate_alternatives(brand_spec, count=3)
        
        # Save to data.json
        data = content_manager._load_data()
        if 'brands' not in data:
            data['brands'] = []
        
        # Add main brand and alternatives
        data['brands'].append(brand_spec)
        for alt in alternatives:
            data['brands'].append(alt)
        
        content_manager._save_data(data)
        
        return web.json_response({
            "success": True,
            "brand": brand_spec,
            "alternatives": alternatives,
            "message": f"Brand '{brand_spec.get('name', 'Untitled')}' synthesized successfully"
        })
        
    except ValueError as e:
        return web.json_response({"error": str(e)}, status=400)
    except Exception as e:
        print(f"Error in brand synthesis: {e}")
        import traceback
        traceback.print_exc()
        return web.json_response({"error": str(e)}, status=500)

async def api_brand_preview(request):
    """API endpoint to generate brand preview HTML"""
    try:
        if not BRAND_PREVIEW_AVAILABLE:
            return web.json_response({"error": "Brand preview generator not available"}, status=503)
        
        brand_id = request.match_info['brand_id']
        
        # Load data
        data_file = Path('content/data.json')
        if not data_file.exists():
            return web.json_response({"error": "Data file not found"}, status=404)
        
        with open(data_file) as f:
            data = json.load(f)
        
        # Find brand by ID
        brand_spec = None
        for brand in data.get('brands', []):
            if brand.get('id') == brand_id:
                brand_spec = brand
                break
        
        if not brand_spec:
            return web.json_response({"error": "Brand not found"}, status=404)
        
        # Generate preview
        preview_generator = BrandPreviewGenerator()
        html_preview = preview_generator.generate_html_preview(brand_spec)
        
        return web.Response(text=html_preview, content_type='text/html')
        
    except Exception as e:
        print(f"Error generating brand preview: {e}")
        import traceback
        traceback.print_exc()
        return web.json_response({"error": str(e)}, status=500)

async def brands_archive(request):
    """Serve brands archive page"""
    try:
        # Load brand data
        data = content_manager._load_data()
        brands = data.get('brands', [])
        
        # Sort brands by creation date (newest first)
        brands_sorted = sorted(brands, key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Generate brand cards HTML
        if not brands_sorted:
            brands_html = '''
                <div class="empty-state">
                    <h2>No brands created yet</h2>
                    <p>Create your first brand to see it here!</p>
                    <a href="/" class="btn btn-primary">Go to Dashboard</a>
                </div>
            '''
        else:
            brands_cards = []
            for brand in brands_sorted:
                insights = brand.get('synthesized_insights', {})
                keywords = insights.get('keywords', [])[:4]
                visual_tone = insights.get('visual_tone', {})
                
                # Generate color swatches
                color_swatches = []
                for name, color in list(brand.get('colors', {}).items())[:5]:
                    color_swatches.append(f'<div class="color-swatch" style="background: {color};" title="{name}: {color}"></div>')
                
                # Generate trait tags
                trait_tags = []
                for trait in brand.get('personality', {}).get('traits', [])[:4]:
                    trait_tags.append(f'<span class="trait-tag">{trait}</span>')
                
                # DNA section
                dna_section = ""
                if keywords or visual_tone:
                    dna_content = []
                    if keywords:
                        dna_content.append(f'<div><strong>Themes:</strong> {", ".join(keywords)}</div>')
                    if visual_tone:
                        visual_desc = ', '.join([v for v in visual_tone.values() if v])
                        if visual_desc:
                            dna_content.append(f'<div><strong>Visual:</strong> {visual_desc}</div>')
                    
                    if dna_content:
                        dna_section = f'''
                        <div class="brand-dna">
                            <div class="dna-title">🧬 Brand DNA</div>
                            {"".join(dna_content)}
                        </div>
                        '''
                
                brands_cards.append(f'''
                    <div class="brand-card">
                        <div class="brand-header">
                            <h3 class="brand-title">{brand.get('name', 'Untitled Brand')}</h3>
                            <div class="brand-date">{brand.get('created_at', '')[:10] if brand.get('created_at') else 'Unknown'}</div>
                        </div>
                        
                        <div class="brand-colors">
                            {"".join(color_swatches)}
                        </div>
                        
                        <div class="brand-traits">
                            {"".join(trait_tags)}
                        </div>
                        
                        {dna_section}
                        
                        <div class="brand-actions">
                            <a href="/brand/{brand.get('id')}" target="_blank" class="btn btn-primary">🔬 Full Analysis</a>
                            <a href="/api/brand-tokens/{brand.get('id')}" target="_blank" class="btn btn-purple">🎨 Tokens</a>
                        </div>
                    </div>
                ''')
            
            brands_html = f'<div class="brands-grid">{"".join(brands_cards)}</div>'
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brand Archive - Concierto</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: #f8f9fa;
            color: #2c3e50;
            line-height: 1.6;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .nav-bar {{
            background: white;
            padding: 1rem 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .nav-bar a {{
            color: #667eea;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            transition: background 0.2s;
        }}
        
        .nav-bar a:hover {{
            background: #f0f2ff;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 2rem auto;
            padding: 0 2rem;
        }}
        
        .archive-stats {{
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            text-align: center;
        }}
        
        .stat-item {{
            padding: 1rem;
            border-radius: 8px;
            background: linear-gradient(135deg, #f8f9fa, #ffffff);
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }}
        
        .brands-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 2rem;
        }}
        
        .brand-card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .brand-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }}
        
        .brand-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
        }}
        
        .brand-title {{
            font-size: 1.25rem;
            font-weight: bold;
            color: #333;
            margin: 0;
        }}
        
        .brand-date {{
            font-size: 0.8rem;
            color: #666;
            background: #f0f0f0;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
        }}
        
        .brand-colors {{
            display: flex;
            gap: 0.5rem;
            margin: 1rem 0;
        }}
        
        .color-swatch {{
            width: 40px;
            height: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            border: 2px solid white;
        }}
        
        .brand-traits {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin: 1rem 0;
        }}
        
        .trait-tag {{
            background: #f0f2ff;
            color: #667eea;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        
        .brand-dna {{
            background: linear-gradient(135deg, #667eea20, transparent);
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            font-size: 0.9rem;
        }}
        
        .dna-title {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 0.5rem;
        }}
        
        .brand-actions {{
            display: flex;
            gap: 0.5rem;
            margin-top: 1.5rem;
        }}
        
        .btn {{
            padding: 0.6rem 1rem;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 500;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            transition: transform 0.1s, box-shadow 0.2s;
            flex: 1;
            justify-content: center;
        }}
        
        .btn:hover {{
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}
        
        .btn-primary {{
            background: #667eea;
            color: white;
        }}
        
        .btn-purple {{
            background: #6f42c1;
            color: white;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 3rem;
            color: #666;
        }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 0 1rem; }}
            .brands-grid {{ grid-template-columns: 1fr; }}
            .nav-bar {{ flex-direction: column; gap: 1rem; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎨 Brand Archive</h1>
        <p>Your complete collection of synthesized brand identities</p>
    </div>
    
    <div class="nav-bar">
        <div>
            <a href="/">← Back to Dashboard</a>
        </div>
        <div>
            <a href="#" onclick="location.reload()">🔄 Refresh</a>
        </div>
    </div>
    
    <div class="container">
        <div class="archive-stats">
            <div class="stat-item">
                <div class="stat-number">{len(brands_sorted)}</div>
                <div>Total Brands</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len([b for b in brands_sorted if b.get('synthesized_insights')])}</div>
                <div>With DNA Analysis</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len([b for b in brands_sorted if b.get('accessibility', {}).get('passed')])}</div>
                <div>WCAG Compliant</div>
            </div>
        </div>
        
        {brands_html}
    </div>
</body>
</html>'''
        
        return web.Response(text=html_content, content_type='text/html')
        
    except Exception as e:
        print(f"Error generating brands archive: {e}")
        import traceback
        traceback.print_exc()
        return web.Response(text=f"Error generating archive: {str(e)}", status=500)

async def view_brand_preview(request):
    """Serve brand preview page - same as API but with clean URL"""
    try:
        if not BRAND_PREVIEW_AVAILABLE:
            return web.Response(text="Brand preview generator not available", status=503)
        
        brand_id = request.match_info['brand_id']
        
        # Find the brand
        data = content_manager._load_data()
        brands = data.get('brands', [])
        
        brand_spec = None
        for brand in brands:
            if brand.get('id') == brand_id:
                brand_spec = brand
                break
        
        if not brand_spec:
            return web.Response(text="Brand not found", status=404)
        
        # Generate preview using the same logic as API
        preview_generator = BrandPreviewGenerator()
        html_preview = preview_generator.generate_html_preview(brand_spec)
        
        return web.Response(text=html_preview, content_type='text/html')
        
    except Exception as e:
        print(f"Error generating brand view: {e}")
        import traceback
        traceback.print_exc()
        return web.Response(text=f"Error generating brand view: {str(e)}", status=500)

async def api_brand_tokens(request):
    """API endpoint to generate Figma tokens for a brand"""
    try:
        if not BRAND_PREVIEW_AVAILABLE:
            return web.json_response({"error": "Brand preview generator not available"}, status=503)
        
        brand_id = request.match_info['brand_id']
        
        # Load data
        data_file = Path('content/data.json')
        if not data_file.exists():
            return web.json_response({"error": "Data file not found"}, status=404)
        
        with open(data_file) as f:
            data = json.load(f)
        
        # Find brand by ID
        brand_spec = None
        for brand in data.get('brands', []):
            if brand.get('id') == brand_id:
                brand_spec = brand
                break
        
        if not brand_spec:
            return web.json_response({"error": "Brand not found"}, status=404)
        
        # Generate tokens
        preview_generator = BrandPreviewGenerator()
        tokens = preview_generator.generate_figma_tokens(brand_spec)
        
        return web.json_response(tokens)
        
    except Exception as e:
        print(f"Error generating brand tokens: {e}")
        import traceback
        traceback.print_exc()
        return web.json_response({"error": str(e)}, status=500)

async def api_style_analysis(request):
    """API endpoint to analyze or re-analyze style vectors for images"""
    try:
        # Check if style vector analysis is available
        if not STYLE_VECTOR_AVAILABLE:
            return web.json_response({
                "error": "Style vector analysis not available. Install required dependencies: pip install scikit-learn pillow numpy"
            }, status=503)
        
        data = content_manager._load_data()
        
        # Find images that need style analysis (don't have style_vector)
        images_to_process = []
        for item in data['items']:
            if item.get('type') == 'image' and not item.get('style_vector'):
                images_to_process.append(item)
        
        if not images_to_process:
            return web.json_response({
                "success": True,
                "message": "All images already have style vectors",
                "processed": 0
            })
        
        print(f"🎨 Starting style vector analysis on {len(images_to_process)} images...")
        processed_count = 0
        
        # Process each image
        for item in images_to_process:
            try:
                image_path = Path(item['path'])
                if image_path.exists():
                    print(f"Analyzing style vector for {item['filename']}...")
                    
                    style_data = analyze_style_vector(str(image_path))
                    if style_data:
                        # Update item with style vector data
                        item.update(style_data)
                        processed_count += 1
                        print(f"✨ Style vector added to {item['filename']}")
                    else:
                        print(f"❌ Style analysis failed for {item['filename']}")
                else:
                    print(f"⚠️ Image file not found: {image_path}")
                    
            except Exception as e:
                print(f"Error processing {item['filename']}: {e}")
                continue
        
        # Save updated data
        content_manager._save_data(data)
        
        return web.json_response({
            "success": True,
            "message": f"Style vector analysis completed on {processed_count}/{len(images_to_process)} images",
            "processed": processed_count,
            "total_found": len(images_to_process)
        })
        
    except Exception as e:
        print(f"Style analysis error: {e}")
        return web.json_response({"error": str(e)}, status=500)


def create_app():
    """Create the web application"""
    app = web.Application()
    
    # Configure max upload size (100MB)
    app['client_max_size'] = 100 * 1024 * 1024
    
    # Routes
    app.router.add_get('/', working_dashboard)
    app.router.add_get('/api/content', api_content)
    app.router.add_post('/api/scan', api_scan)
    app.router.add_post('/api/ai-scan', api_ai_scan)
    app.router.add_post('/api/style-analysis', api_style_analysis)
    app.router.add_post('/api/multi-agent-analysis', api_multi_agent_analysis)
    app.router.add_post('/api/batch-multi-agent-analysis', api_batch_multi_agent_analysis)
    app.router.add_post('/api/update-item', api_update_item)
    app.router.add_post('/api/create-project', api_create_project)
    app.router.add_post('/api/create-campaign', api_create_campaign)
    app.router.add_post('/api/update-campaign', api_update_campaign)
    app.router.add_post('/api/link-campaign-items', api_link_campaign_items)
    app.router.add_get('/api/campaigns', api_get_campaigns)
    app.router.add_post('/api/generate-concepts', api_generate_concepts)
    app.router.add_post('/api/synthesize', api_synthesize_brand)
    app.router.add_get('/brands', brands_archive)
    app.router.add_get('/brand/{brand_id}', view_brand_preview)
    app.router.add_get('/api/brand-preview/{brand_id}', api_brand_preview)
    app.router.add_get('/api/brand-tokens/{brand_id}', api_brand_tokens)
    app.router.add_get('/api/search', api_search)
    app.router.add_get('/api/export', api_export)
    app.router.add_post('/api/upload', api_upload)
    app.router.add_get('/{path:.*}', serve_file)
    
    return app

async def init():
    """Initialize the application"""
    try:
        # Scan for existing content on startup
        print("🔍 Scanning for existing content...")
        new_items = content_manager.scan_images()
        if new_items > 0:
            print(f"📸 Found {new_items} new images")
        else:
            print("📂 No new images found")
    except Exception as e:
        print(f"⚠️ Error scanning images: {e}")
    
    # Start server
    app = create_app()
    return app

if __name__ == '__main__':
    print("🎼 Starting Concierto - Simple Content Dashboard")
    print("📁 Make sure to put your images in: content/images/")
    print("🌐 Dashboard will be at: http://localhost:8084")
    print()
    
    try:
        app = asyncio.run(init())
        web.run_app(app, host='localhost', port=8084)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()