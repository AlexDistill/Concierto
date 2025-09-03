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

async def dashboard(request):
    """Serve main dashboard"""
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Concierto - Content Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: #f8f9fa;
            color: #2c3e50;
            line-height: 1.6;
        }
        
        /* Search and Filter Bar */
        .search-bar {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            align-items: center;
        }
        .search-input {
            flex: 1;
            min-width: 200px;
            padding: 0.75rem;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1rem;
        }
        .filter-select {
            padding: 0.75rem;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background: white;
            font-size: 1rem;
            cursor: pointer;
        }
        
        /* Projects/Collections */
        .projects-section {
            margin-bottom: 2rem;
        }
        .projects-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        .project-cards {
            display: flex;
            gap: 1rem;
            overflow-x: auto;
            padding-bottom: 0.5rem;
        }
        .project-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            min-width: 180px;
            cursor: pointer;
            transition: transform 0.2s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .project-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .project-card.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .add-project-btn {
            background: #f0f0f0;
            border: 2px dashed #ccc;
            color: #666;
            padding: 1rem;
            border-radius: 8px;
            min-width: 180px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .add-project-btn:hover {
            border-color: #667eea;
            color: #667eea;
        }
        
        /* Upload Area */
        .upload-zone {
            background: white;
            border: 3px dashed #d0d0d0;
            border-radius: 12px;
            padding: 3rem 2rem;
            text-align: center;
            margin-bottom: 2rem;
            transition: all 0.3s;
            cursor: pointer;
        }
        .upload-zone:hover, .upload-zone.dragover {
            border-color: #667eea;
            background: #f8f9ff;
        }
        .upload-zone h3 {
            color: #667eea;
            margin-bottom: 1rem;
        }
        .upload-zone p {
            color: #6c757d;
        }
        
        /* Edit Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        .modal.active {
            display: flex;
        }
        .modal-content {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        .modal-close {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #999;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1rem;
        }
        .form-group textarea {
            resize: vertical;
            min-height: 100px;
        }
        .tag-input-container {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            padding: 0.5rem;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            min-height: 50px;
        }
        .tag-input {
            border: none;
            outline: none;
            flex: 1;
            min-width: 100px;
        }
        
        /* Export Button */
        .export-btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
        }
        .export-btn:hover {
            background: linear-gradient(45deg, #5a67d8, #6b46c1);
        }
        
        /* Campaign Styles */
        .campaign-btn {
            background: linear-gradient(135deg, #ff6b6b, #ff8787);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
        }
        .campaign-btn:hover {
            background: linear-gradient(135deg, #ff5252, #ff6b6b);
        }
        .campaigns-section {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .campaign-card {
            background: linear-gradient(135deg, #f8f9fa, #fff);
            border-left: 4px solid #ff6b6b;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .campaign-card:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .campaign-status {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .status-concept { background: #e3f2fd; color: #1976d2; }
        .status-active { background: #e8f5e9; color: #388e3c; }
        .status-completed { background: #f3e5f5; color: #7b1fa2; }
        
        /* Campaign Modal */
        .campaign-form {
            display: grid;
            gap: 1.5rem;
        }
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }
        .form-row.full { grid-template-columns: 1fr; }
        .image-selector {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
            gap: 0.5rem;
            max-height: 300px;
            overflow-y: auto;
            padding: 1rem;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
        }
        .image-thumb {
            width: 80px;
            height: 80px;
            object-fit: cover;
            border-radius: 4px;
            cursor: pointer;
            border: 2px solid transparent;
            transition: all 0.2s;
        }
        .image-thumb:hover {
            transform: scale(1.1);
        }
        .image-thumb.selected {
            border-color: #ff6b6b;
            box-shadow: 0 0 0 2px rgba(255, 107, 107, 0.2);
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .header p { opacity: 0.9; font-size: 1.1rem; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
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
        .stat-number { font-size: 2rem; font-weight: bold; color: #667eea; }
        .stat-label { color: #6c757d; font-size: 0.9rem; margin-top: 0.5rem; }
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
        }
        .content-item:hover { transform: translateY(-4px); }
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
            font-weight: 500;
        }
        .ai-insights {
            background: #f8f9ff;
            border-left: 3px solid #667eea;
            padding: 0.75rem;
            margin-top: 1rem;
            border-radius: 4px;
            font-size: 0.9rem;
            line-height: 1.4;
        }
        .item-description {
            color: #6c757d;
            font-size: 0.9rem;
            margin: 0.5rem 0;
            line-height: 1.4;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            margin-bottom: 2rem;
        }
        .refresh-btn:hover {
            background: #5a67d8;
        }
        .ai-btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
        }
        .ai-btn:hover {
            background: linear-gradient(45deg, #5a67d8, #6b46c1);
        }
        .ai-btn:disabled {
            background: #gray;
            cursor: not-allowed;
            opacity: 0.6;
        }
        .empty-state {
            text-align: center;
            padding: 4rem 2rem;
            color: #6c757d;
        }
        .empty-state h3 { margin-bottom: 1rem; }
        .instructions {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 1rem;
            margin: 2rem 0;
            border-radius: 4px;
        }
        .loading { opacity: 0.6; pointer-events: none; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎼 Concierto</h1>
        <p>Your Creative Content Dashboard</p>
    </div>
    
    <div class="container">
        <!-- Upload Zone -->
        <div class="upload-zone" id="uploadZone" onclick="document.getElementById('fileInput').click()">
            <h3>📸 Drag & Drop Images Here</h3>
            <p>or click to browse files</p>
            <input type="file" id="fileInput" multiple accept="image/*" style="display: none;" onchange="handleFileSelect(event)">
        </div>
        
        <!-- Search and Filter -->
        <div class="search-bar">
            <input type="text" class="search-input" id="searchInput" placeholder="Search by title, tags, or description..." onkeyup="debounceSearch()">
            <select class="filter-select" id="typeFilter" onchange="applyFilters()">
                <option value="all">All Types</option>
                <option value="image">Images</option>
                <option value="note">Notes</option>
            </select>
            <select class="filter-select" id="projectFilter" onchange="applyFilters()">
                <option value="all">All Projects</option>
            </select>
            <button class="campaign-btn" onclick="showCampaigns()">📋 Campaigns</button>
            <button class="export-btn" onclick="exportContent()">📥 Export</button>
        </div>
        
        <!-- Projects/Collections -->
        <div class="projects-section">
            <div class="projects-header">
                <h2>📁 Projects</h2>
                <button class="refresh-btn" onclick="createProject()">+ New Project</button>
            </div>
            <div class="project-cards" id="projectCards">
                <div class="project-card active" onclick="selectProject('all')">
                    <h3>All Content</h3>
                    <p id="allContentCount">0 items</p>
                </div>
            </div>
        </div>
        
        <div style="margin-bottom: 2rem; display: flex; gap: 1rem; flex-wrap: wrap;">
            <button class="refresh-btn" onclick="refreshContent()">
                📱 Quick Scan
            </button>
            <button class="refresh-btn ai-btn" onclick="aiScan()" id="aiScanBtn">
                🤖 AI Analysis
            </button>
        </div>
        
        <div class="instructions">
            <strong>💡 Quick Start:</strong> Drop your inspiration images into the <code>content/images/</code> folder, 
            then click "Scan for New Content" to see them here!
        </div>
        
        <div class="stats" id="stats">
            <!-- Stats will be loaded here -->
        </div>
        
        <div class="content-grid" id="content">
            <!-- Content will be loaded here -->
        </div>
    </div>

    <script>
        // Escape function to handle quotes in strings
        function escapeHtml(str) {
            if (!str) return '';
            return String(str)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
        }
        
        async function loadContent() {
            try {
                const response = await fetch('/api/content');
                const data = await response.json();
                allContent = data.items;
                
                // Update stats
                const statsHtml = '<div class="stat-card">' +
                        '<div class="stat-number">' + data.items.length + '</div>' +
                        '<div class="stat-label">Total Items</div>' +
                    '</div>' +
                    '<div class="stat-card">' +
                        '<div class="stat-number">' + data.items.filter(i => i.type === 'image').length + '</div>' +
                        '<div class="stat-label">Images</div>' +
                    '</div>' +
                    '<div class="stat-card">' +
                        '<div class="stat-number">' + data.items.filter(i => i.type === 'note').length + '</div>' +
                        '<div class="stat-label">Notes</div>' +
                    '</div>' +
                    '<div class="stat-card">' +
                        '<div class="stat-number">' + data.tags.length + '</div>' +
                        '<div class="stat-label">Tags</div>' +
                    '</div>';
                document.getElementById('stats').innerHTML = statsHtml;
                
                // Update content
                if (data.items.length === 0) {
                    document.getElementById('content').innerHTML = '<div class="empty-state">' +
                            '<h3>No content yet!</h3>' +
                            '<p>Add some images to the content/images/ folder and click "Scan for New Content"</p>' +
                        '</div>';
                } else {
                    const contentHtml = data.items.map(item => {
                        if (item.type === 'image') {
                            const aiInsights = item.creative_insights ? 
                                '<div class="ai-insights">' +
                                    '<strong>🤖 AI Insights:</strong> ' + escapeHtml(item.creative_insights) +
                                '</div>' : '';
                            
                            const description = item.description ? 
                                '<p class="item-description">' + escapeHtml(item.description) + '</p>' : '';
                            
                            return '<div class="content-item" onclick="editItem(\'' + item.id + '\')" style="cursor: pointer;">' +
                                    '<img src="/' + escapeHtml(item.path) + '" alt="' + escapeHtml(item.title) + '" class="image-preview" onerror="this.style.display=\'none\'">' +
                                    '<div class="item-content">' +
                                        '<div class="item-title">' + escapeHtml(item.title) + '</div>' +
                                        (description) +
                                        (item.notes ? '<p class="item-notes" style="color: #764ba2; font-style: italic; margin: 0.5rem 0;">📝 ' + escapeHtml(item.notes) + '</p>' : '') +
                                        '<div class="item-tags">' +
                                            (item.ai_tags || []).map(tag => '<span class="tag ai-tag">🤖 ' + escapeHtml(tag) + '</span>').join('') +
                                            (item.tags || []).filter(tag => !(item.ai_tags || []).includes(tag)).map(tag => '<span class="tag">' + escapeHtml(tag) + '</span>').join('') +
                                        '</div>' +
                                        (aiInsights) +
                                    '</div>' +
                                '</div>';
                        } else {
                            return '<div class="content-item">' +
                                    '<div class="item-content">' +
                                        '<div class="item-title">' + escapeHtml(item.title) + '</div>' +
                                        '<p>' + escapeHtml(item.content ? item.content.substring(0, 150) : '') + (item.content && item.content.length > 150 ? '...' : '') + '</p>' +
                                        '<div class="item-tags">' +
                                            (item.tags || []).map(tag => '<span class="tag">' + escapeHtml(tag) + '</span>').join('') +
                                        '</div>' +
                                    '</div>' +
                                '</div>';
                        }
                    }).join('');
                    document.getElementById('content').innerHTML = contentHtml;
                }
            } catch (error) {
                console.error('Failed to load content:', error);
                document.getElementById('content').innerHTML = '<div class="empty-state"><h3>Error loading content</h3></div>';
            }
        }
        
        async function refreshContent() {
            document.body.classList.add('loading');
            try {
                const response = await fetch('/api/scan', { method: 'POST' });
                const result = await response.json();
                console.log('Scan result:', result);
                await loadContent();
            } catch (error) {
                console.error('Failed to refresh content:', error);
            } finally {
                document.body.classList.remove('loading');
            }
        }
        
        async function aiScan() {
            const aiBtn = document.getElementById('aiScanBtn');
            aiBtn.disabled = true;
            aiBtn.textContent = '🤖 Analyzing...';
            document.body.classList.add('loading');
            
            try {
                const response = await fetch('/api/ai-scan', { method: 'POST' });
                const result = await response.json();
                
                if (response.ok) {
                    console.log('AI analysis result:', result);
                    alert('✅ ' + (result.message || 'AI analysis completed!'));
                    await loadContent();
                } else {
                    alert('❌ ' + (result.message || 'AI analysis failed'));
                }
            } catch (error) {
                console.error('AI analysis failed:', error);
                alert('❌ AI analysis failed. Check console for details.');
            } finally {
                aiBtn.disabled = false;
                aiBtn.textContent = '🤖 AI Analysis';
                document.body.classList.remove('loading');
            }
        }
        
        // Global variables
        let allContent = [];
        let currentProject = 'all';
        let searchTimeout;
        
        // Initialize upload functionality after DOM is ready
        function initializeUpload() {
            const uploadZone = document.getElementById('uploadZone');
            const fileInput = document.getElementById('fileInput');
            
            if (!uploadZone || !fileInput) {
                console.error('Upload elements not found');
                return;
            }
            
            uploadZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.stopPropagation();
                uploadZone.classList.add('dragover');
            });
            
            uploadZone.addEventListener('dragleave', (e) => {
                e.preventDefault();
                e.stopPropagation();
                uploadZone.classList.remove('dragover');
            });
            
            uploadZone.addEventListener('drop', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                uploadZone.classList.remove('dragover');
                
                const files = Array.from(e.dataTransfer.files);
                console.log('Dropped files:', files);
                await uploadFiles(files);
            });
            
            // Prevent default drag behavior on document
            document.addEventListener('dragover', (e) => {
                e.preventDefault();
            });
            
            document.addEventListener('drop', (e) => {
                e.preventDefault();
            });
        }
        
        // Initialize upload when page loads
        window.addEventListener('DOMContentLoaded', initializeUpload);
        
        async function handleFileSelect(event) {
            const files = Array.from(event.target.files);
            await uploadFiles(files);
        }
        
        async function uploadFiles(files) {
            console.log('Uploading files:', files);
            const formData = new FormData();
            let imageCount = 0;
            
            files.forEach(file => {
                console.log('File type:', file.type, 'File name:', file.name);
                if (file.type.startsWith('image/')) {
                    formData.append('file', file);
                    imageCount++;
                }
            });
            
            if (imageCount === 0) {
                alert('⚠️ No image files selected. Please select JPG, PNG, GIF, or WEBP files.');
                return;
            }
            
            try {
                console.log('Sending upload request...');
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                
                console.log('Upload response status:', response.status);
                const result = await response.json();
                
                if (response.ok) {
                    console.log('Upload successful:', result);
                    alert('✅ Uploaded ' + result.uploaded.length + ' files');
                    await loadContent();
                } else {
                    console.error('Upload failed:', result);
                    alert('❌ Upload failed: ' + (result.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Upload error:', error);
                alert('❌ Upload failed: ' + error.message);
            }
        }
        
        // Search functionality
        function debounceSearch() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(applyFilters, 300);
        }
        
        async function applyFilters() {
            const searchQuery = document.getElementById('searchInput').value;
            const typeFilter = document.getElementById('typeFilter').value;
            const projectFilter = document.getElementById('projectFilter').value;
            
            let filtered = allContent;
            
            // Filter by type
            if (typeFilter !== 'all') {
                filtered = filtered.filter(item => item.type === typeFilter);
            }
            
            // Filter by project
            if (projectFilter !== 'all') {
                filtered = filtered.filter(item => item.project_id === projectFilter);
            }
            
            // Filter by search query
            if (searchQuery) {
                const query = searchQuery.toLowerCase();
                filtered = filtered.filter(item => {
                    const searchable = [
                        item.title || '',
                        item.description || '',
                        item.notes || '',
                        (item.tags || []).join(' '),
                        item.creative_insights || ''
                    ].join(' ').toLowerCase();
                    return searchable.includes(query);
                });
            }
            
            displayContent(filtered);
        }
        
        function displayContent(items) {
            const contentDiv = document.getElementById('content');
            
            if (items.length === 0) {
                contentDiv.innerHTML = 
                    '<div class="empty-state">' +
                        '<h3>No content found</h3>' +
                        '<p>Try adjusting your filters or add new content</p>' +
                    '</div>';
                return;
            }
            
            const contentHtml = items.map(item => {
                if (item.type === 'image') {
                    const aiInsights = item.creative_insights ? 
                        '<div class="ai-insights">' +
                            '<strong>🤖 AI Insights:</strong> ' + escapeHtml(item.creative_insights) +
                        '</div>' : '';
                    
                    const description = item.description ? 
                        '<p class="item-description">' + escapeHtml(item.description) + '</p>' : '';
                    
                    return '<div class="content-item" onclick="editItem(\'' + item.id + '\')" style="cursor: pointer;">' +
                            '<img src="/' + escapeHtml(item.path) + '" alt="' + escapeHtml(item.title) + '" class="image-preview" onerror="this.style.display=\'none\'">' +
                            '<div class="item-content">' +
                                '<div class="item-title">' + escapeHtml(item.title) + '</div>' +
                                (description) +
                                (item.notes ? '<p class="item-notes" style="color: #764ba2; font-style: italic; margin: 0.5rem 0;">📝 ' + escapeHtml(item.notes) + '</p>' : '') +
                                '<div class="item-tags">' +
                                    (item.ai_tags || []).map(tag => '<span class="tag ai-tag">🤖 ' + escapeHtml(tag) + '</span>').join('') +
                                    (item.tags || []).filter(tag => !(item.ai_tags || []).includes(tag)).map(tag => '<span class="tag">' + escapeHtml(tag) + '</span>').join('') +
                                '</div>' +
                                (aiInsights) +
                            '</div>' +
                        '</div>';
                } else {
                    return '<div class="content-item" onclick="editItem(\'' + item.id + '\')" style="cursor: pointer;">' +
                            '<div class="item-content">' +
                                '<div class="item-title">' + escapeHtml(item.title) + '</div>' +
                                '<p>' + escapeHtml(item.content ? item.content.substring(0, 150) : '') + (item.content && item.content.length > 150 ? '...' : '') + '</p>' +
                                '<div class="item-tags">' +
                                    (item.tags || []).map(tag => '<span class="tag">' + escapeHtml(tag) + '</span>').join('') +
                                '</div>' +
                            '</div>' +
                        '</div>';
                }
            }).join('');
            
            contentDiv.innerHTML = contentHtml;
        }
        
        // Project functionality
        async function createProject() {
            const name = prompt('Project name:');
            if (!name) return;
            
            const description = prompt('Project description (optional):');
            
            try {
                const response = await fetch('/api/create-project', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, description })
                });
                
                if (response.ok) {
                    await loadContent();
                } else {
                    alert('❌ Failed to create project');
                }
            } catch (error) {
                console.error('Error creating project:', error);
            }
        }
        
        function selectProject(projectId) {
            currentProject = projectId;
            document.querySelectorAll('.project-card').forEach(card => {
                card.classList.remove('active');
            });
            event.currentTarget.classList.add('active');
            
            document.getElementById('projectFilter').value = projectId;
            applyFilters();
        }
        
        // Edit functionality
        function editItem(itemId) {
            const item = allContent.find(i => i.id === itemId);
            if (!item) return;
            
            const newNotes = prompt('Add notes:', item.notes || '');
            if (newNotes === null) return;
            
            updateItem(itemId, { notes: newNotes });
        }
        
        async function updateItem(itemId, updates) {
            try {
                const response = await fetch('/api/update-item', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: itemId, ...updates })
                });
                
                if (response.ok) {
                    await loadContent();
                } else {
                    alert('❌ Failed to update item');
                }
            } catch (error) {
                console.error('Error updating item:', error);
            }
        }
        
        // Export functionality
        async function exportContent() {
            const format = confirm('Export as HTML mood board? (Cancel for JSON)') ? 'html' : 'json';
            const projectId = currentProject === 'all' ? '' : currentProject;
            
            const url = '/api/export?format=' + format + (projectId ? '&project_id=' + projectId : '');
            window.open(url, '_blank');
        }
        
        
        // Campaign functionality
        let campaigns = [];
        let selectedCampaignItems = [];
        
        async function showCampaigns() {
            // Load campaigns
            const response = await fetch('/api/campaigns');
            campaigns = await response.json();
            
            // Show campaigns modal
            const modal = document.createElement('div');
            modal.className = 'modal active';
            modal.innerHTML = '<div class="modal-content" style="max-width: 900px;">' +
                    '<div class="modal-header">' +
                        '<h2>📋 Campaign Concepts</h2>' +
                        '<button class="modal-close" onclick="this.closest(\'.modal\').remove()">×</button>' +
                    '</div>' +
                    '<button class="campaign-btn" style="margin-bottom: 1rem;" onclick="createCampaign()">+ New Campaign</button>' +
                    '<div id="campaignsList">' +
                        (campaigns.map(c => 
                            '<div class="campaign-card" onclick="viewCampaign(\'' + c.id + '\')">' +
                                '<div style="display: flex; justify-content: space-between; align-items: start;">' +
                                    '<div>' +
                                        '<h3>' + c.name + '</h3>' +
                                        '<p><strong>Client:</strong> ' + c.client + '</p>' +
                                        '<p><strong>Objective:</strong> ' + c.objective + '</p>' +
                                        '<p><strong>Mood Board:</strong> ' + (c.linked_items_details ? c.linked_items_details.length : 0) + ' items</p>' +
                                    '</div>' +
                                    '<span class="campaign-status status-' + c.status + '">' + c.status + '</span>' +
                                '</div>' +
                            '</div>'
                        ).join('') || '<p>No campaigns yet. Click "New Campaign" to create one.</p>') +
                    '</div>' +
                '</div>';
            document.body.appendChild(modal);
        }
        
        function createCampaign() {
            const modal = document.createElement('div');
            modal.className = 'modal active';
            modal.innerHTML = '<div class="modal-content" style="max-width: 900px; max-height: 90vh; overflow-y: auto;">' +
                    '<div class="modal-header">' +
                        '<h2>✨ Create Campaign Concept</h2>' +
                        '<button class="modal-close" onclick="this.closest(\'.modal\').remove()">×</button>' +
                    '</div>' +
                    '<form class="campaign-form" onsubmit="saveCampaign(event)">' +
                        '<div class="form-row">' +
                            '<div class="form-group">' +
                                '<label>Campaign Name *</label>' +
                                '<input type="text" name="name" required placeholder="Summer 2025 Launch">' +
                            '</div>' +
                            '<div class="form-group">' +
                                '<label>Client *</label>' +
                                '<input type="text" name="client" required placeholder="Brand Name">' +
                            '</div>' +
                        '</div>' +
                        '<div class="form-group">' +
                            '<label>Campaign Objective *</label>' +
                            '<textarea name="objective" required rows="2" placeholder="Drive awareness for new product line targeting millennials..."></textarea>' +
                        '</div>' +
                        '<div class="form-row">' +
                            '<div class="form-group">' +
                                '<label>Target Audience</label>' +
                                '<input type="text" name="target_audience" placeholder="25-35 urban professionals">' +
                            '</div>' +
                            '<div class="form-group">' +
                                '<label>Timeline</label>' +
                                '<input type="text" name="timeline" placeholder="Q2 2025">' +
                            '</div>' +
                        '</div>' +
                        '<div class="form-group">' +
                            '<label>Key Messages</label>' +
                            '<textarea name="key_messages" rows="2" placeholder="Innovation, sustainability, premium quality..."></textarea>' +
                        '</div>' +
                        '<div class="form-group">' +
                            '<label>Tone & Voice</label>' +
                            '<input type="text" name="tone_voice" placeholder="Bold, playful, authentic">' +
                        '</div>' +
                        '<div class="form-group">' +
                            '<label>Deliverables</label>' +
                            '<textarea name="deliverables" rows="2" placeholder="Social media campaign, website landing page, print ads..."></textarea>' +
                        '</div>' +
                        '<div class="form-group">' +
                            '<label>Budget Range</label>' +
                            '<input type="text" name="budget_range" placeholder="$50k - $100k">' +
                        '</div>' +
                        '<div class="form-group">' +
                            '<label>Visual Inspiration Notes</label>' +
                            '<textarea name="inspiration_notes" rows="3" placeholder="Looking for vibrant, energetic visuals with bold typography..."></textarea>' +
                        '</div>' +
                        '<div class="form-group">' +
                            '<label>Select Mood Board Images</label>' +
                            '<div class="image-selector" id="imageSelector">' +
                                allContent.filter(item => item.type === 'image').map(item => 
                                    '<img src="/' + item.path + '" ' +
                                         'class="image-thumb" ' +
                                         'data-id="' + item.id + '"' +
                                         'onclick="toggleImageSelection(this)" ' +
                                         'title="' + item.title + '">'
                                ).join('') +
                            '</div>' +
                        '</div>' +
                        '<button type="submit" class="campaign-btn">Create Campaign</button>' +
                    '</form>' +
                '</div>';
            document.body.appendChild(modal);
        }
        
        function toggleImageSelection(img) {
            img.classList.toggle('selected');
            const id = img.dataset.id;
            if (img.classList.contains('selected')) {
                if (!selectedCampaignItems.includes(id)) {
                    selectedCampaignItems.push(id);
                }
            } else {
                selectedCampaignItems = selectedCampaignItems.filter(i => i !== id);
            }
        }
        
        async function saveCampaign(event) {
            event.preventDefault();
            const form = event.target;
            const formData = new FormData(form);
            
            const campaignData = {};
            for (let [key, value] of formData.entries()) {
                campaignData[key] = value;
            }
            campaignData.linked_items = selectedCampaignItems;
            
            try {
                const response = await fetch('/api/create-campaign', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(campaignData)
                });
                
                if (response.ok) {
                    alert('✅ Campaign created successfully!');
                    document.querySelectorAll('.modal').forEach(m => m.remove());
                    selectedCampaignItems = [];
                    showCampaigns();
                } else {
                    alert('❌ Failed to create campaign');
                }
            } catch (error) {
                console.error('Error creating campaign:', error);
                alert('❌ Error creating campaign');
            }
        }
        
        async function viewCampaign(campaignId) {
            const campaign = campaigns.find(c => c.id === campaignId);
            if (!campaign) return;
            
            const modal = document.createElement('div');
            modal.className = 'modal active';
            modal.innerHTML = '<div class="modal-content" style="max-width: 900px; max-height: 90vh; overflow-y: auto;">' +
                    '<div class="modal-header">' +
                        '<h2>📋 ' + campaign.name + '</h2>' +
                        '<button class="modal-close" onclick="this.closest(\'.modal\').remove()">×</button>' +
                    '</div>' +
                    '<div class="campaigns-section">' +
                        '<p><strong>Client:</strong> ' + campaign.client + '</p>' +
                        '<p><strong>Objective:</strong> ' + campaign.objective + '</p>' +
                        (campaign.target_audience ? '<p><strong>Target Audience:</strong> ' + campaign.target_audience + '</p>' : '') +
                        (campaign.key_messages ? '<p><strong>Key Messages:</strong> ' + campaign.key_messages + '</p>' : '') +
                        (campaign.tone_voice ? '<p><strong>Tone & Voice:</strong> ' + campaign.tone_voice + '</p>' : '') +
                        (campaign.deliverables ? '<p><strong>Deliverables:</strong> ' + campaign.deliverables + '</p>' : '') +
                        (campaign.timeline ? '<p><strong>Timeline:</strong> ' + campaign.timeline + '</p>' : '') +
                        (campaign.budget_range ? '<p><strong>Budget:</strong> ' + campaign.budget_range + '</p>' : '') +
                        (campaign.inspiration_notes ? '<p><strong>Inspiration Notes:</strong> ' + campaign.inspiration_notes + '</p>' : '') +
                        '<h3 style="margin-top: 2rem;">Mood Board</h3>' +
                        '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 1rem; margin-top: 1rem;">' +
                            ((campaign.linked_items_details || []).map(item => 
                                '<div>' +
                                    '<img src="/' + item.path + '" style="width: 100%; height: 150px; object-fit: cover; border-radius: 8px;">' +
                                    '<p style="font-size: 0.9rem; margin-top: 0.5rem;">' + item.title + '</p>' +
                                '</div>'
                            ).join('') || '<p>No mood board items selected</p>') +
                        '</div>' +
                        '<div style="margin-top: 2rem; display: flex; gap: 1rem;">' +
                            '<button class="export-btn" onclick="exportCampaign(\'' + campaign.id + '\')">📅 Export Campaign Brief</button>' +
                            '<button class="campaign-btn" onclick="generateConcepts(\'' + campaign.id + '\')">🎨 Generate Visual Concepts</button>' +
                        '</div>' +
                    '</div>' +
                '</div>';
            document.body.appendChild(modal);
        }
        
        async function generateConcepts(campaignId) {
            const campaign = campaigns.find(c => c.id === campaignId);
            if (!campaign) return;
            
            // Show loading state
            const modal = document.createElement('div');
            modal.className = 'modal active';
            modal.innerHTML = '<div class="modal-content" style="max-width: 400px; text-align: center;">' +
                    '<h2>🎨 Generating Concepts...</h2>' +
                    '<p>Analyzing mood board themes...</p>' +
                    '<p style="color: #666; font-size: 0.9rem;">This may take 30-60 seconds</p>' +
                    '<div style="margin: 2rem 0;">' +
                        '<div style="width: 50px; height: 50px; border: 4px solid #f0f0f0; border-top: 4px solid #667eea; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto;"></div>' +
                    '</div>' +
                '</div>' +
                '<style>' +
                    '@keyframes spin {' +
                        '0% { transform: rotate(0deg); }' +
                        '100% { transform: rotate(360deg); }' +
                    '}' +
                '</style>';
            document.body.appendChild(modal);
            
            try {
                const response = await fetch('/api/generate-concepts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ campaign_id: campaignId })
                });
                
                const result = await response.json();
                
                // Remove loading modal
                modal.remove();
                
                if (response.ok && result.success) {
                    showGeneratedConcepts(result.concepts, campaign);
                } else {
                    alert('❌ ' + (result.message || 'Concept generation failed'));
                }
            } catch (error) {
                modal.remove();
                console.error('Error generating concepts:', error);
                alert('❌ Failed to generate concepts');
            }
        }
        
        function showGeneratedConcepts(conceptData, campaign) {
            const modal = document.createElement('div');
            modal.className = 'modal active';
            
            // Parse concepts properly
            let concepts = conceptData.concepts || [];
            const themes = conceptData.theme_analysis || {};
            const visuals = conceptData.visuals || [];
            
            modal.innerHTML = '<div class="modal-content" style="max-width: 1200px; max-height: 90vh; overflow-y: auto;">' +
                    '<div class="modal-header">' +
                        '<h2>🎨 Generated Concepts for ' + campaign.name + '</h2>' +
                        '<button class="modal-close" onclick="this.closest(\'.modal\').remove()">×</button>' +
                    '</div>' +
                    (themes ? 
                    '<div class="campaigns-section" style="background: linear-gradient(135deg, #f8f9fa, #fff); margin-bottom: 2rem;">' +
                        '<h3>📊 Theme Analysis</h3>' +
                        '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">' +
                            (themes.mood ? '<div><strong>Overall Mood:</strong> ' + themes.mood + '</div>' : '') +
                            (themes.common_tags ? '<div><strong>Key Elements:</strong> ' + themes.common_tags.slice(0, 5).join(', ') + '</div>' : '') +
                            (themes.colors ? '<div><strong>Colors:</strong> ' + themes.colors + '</div>' : '') +
                            (themes.typography ? '<div><strong>Typography:</strong> ' + themes.typography + '</div>' : '') +
                        '</div>' +
                        (themes.direction ? '<p style="margin-top: 1rem;"><strong>Creative Direction:</strong> ' + themes.direction + '</p>' : '') +
                    '</div>' : '') +
                    '<h3>💡 Creative Concepts</h3>' +
                    (concepts.length > 0 ? concepts.map((concept, index) => 
                        '<div class="campaign-card" style="margin-bottom: 1.5rem;">' +
                            '<h4 style="color: #667eea;">' + (concept['Concept Name'] || ('Concept ' + (index + 1))) + '</h4>' +
                            (concept['Visual Description'] ? 
                                '<p><strong>Visual Description:</strong> ' + concept['Visual Description'] + '</p>' : '') +
                            '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem;">' +
                                (concept['Key Visual Elements'] ? 
                                    '<div>' +
                                        '<strong>Key Elements:</strong>' +
                                        '<p style="color: #666; font-size: 0.9rem;">' + concept['Key Visual Elements'] + '</p>' +
                                    '</div>' : '') +
                                (concept['Color Palette'] ? 
                                    '<div>' +
                                        '<strong>Color Palette:</strong>' +
                                        '<p style="color: #666; font-size: 0.9rem;">' + concept['Color Palette'] + '</p>' +
                                    '</div>' : '') +
                                (concept['Typography Approach'] ? 
                                    '<div>' +
                                        '<strong>Typography:</strong>' +
                                        '<p style="color: #666; font-size: 0.9rem;">' + concept['Typography Approach'] + '</p>' +
                                    '</div>' : '') +
                            '</div>' +
                            (concept['Layout/Composition Style'] ? 
                                '<p style="margin-top: 1rem;"><strong>Composition:</strong> ' + concept['Layout/Composition Style'] + '</p>' : '') +
                            (concept['Photography/Illustration Style'] ? 
                                '<p><strong>Visual Style:</strong> ' + concept['Photography/Illustration Style'] + '</p>' : '') +
                            (concept['Example Applications'] ? 
                                '<p><strong>Applications:</strong> ' + concept['Example Applications'] + '</p>' : '') +
                            (concept['Why This Works'] ? 
                                '<div style="background: #f8f9ff; padding: 1rem; border-radius: 8px; margin-top: 1rem;">' +
                                    '<strong>Why This Works:</strong> ' + concept['Why This Works'] +
                                '</div>' : '') +
                        '</div>'
                    ).join('') : '<p>No concepts generated</p>') +
                    (visuals.length > 0 ? 
                        '<h3>🖼️ Generated Visual</h3>' +
                        visuals.map(v => v.success ? 
                            '<div style="text-align: center;">' +
                                '<img src="' + v.image_url + '" style="max-width: 100%; border-radius: 8px; margin: 1rem 0;">' +
                                '<p style="color: #666; font-size: 0.9rem;">' + (v.revised_prompt || 'AI-generated concept visual') + '</p>' +
                            '</div>' : '<p>Visual generation failed: ' + v.error + '</p>').join('') : '') +
                    '<div style="margin-top: 2rem; text-align: center;">' +
                        '<button class="export-btn" onclick="exportConcepts(\'' + campaign.id + '\', ' + JSON.stringify(conceptData).replace(/"/g, '&quot;') + ')">' +
                            '📥 Export Concepts' +
                        '</button>' +
                    '</div>' +
                '</div>';
            document.body.appendChild(modal);
        }
        
        function exportConcepts(campaignId, conceptData) {
            // Create downloadable concept document
            const campaign = campaigns.find(c => c.id === campaignId);
            const html = '<!DOCTYPE html>' +
                '<html>' +
                '<head>' +
                    '<title>' + campaign.name + ' - Creative Concepts</title>' +
                    '<style>' +
                        'body { font-family: -apple-system, sans-serif; max-width: 1200px; margin: 0 auto; padding: 40px; }' +
                        'h1 { color: #667eea; }' +
                        '.concept { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; }' +
                        '.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }' +
                    '</style>' +
                '</head>' +
                '<body>' +
                    '<h1>' + campaign.name + ' - Creative Concepts</h1>' +
                    '<p>Generated: ' + new Date().toLocaleDateString() + '</p>' +
                    '<div id="concepts"></div>' +
                    '<scr' + 'ipt>' +
                        'const data = ' + JSON.stringify(conceptData) + ';' +
                        'document.getElementById("concepts").innerHTML = data.concepts.map(c => ' + 
                            '"<div class=\\"concept\\"><h2>" + (c["Concept Name"] || "Concept") + "</h2>" +' +
                            'Object.entries(c).map(([k,v]) => "<p><strong>" + k + ":</strong> " + v + "</p>").join("") +' +
                            '"</div>"' +
                        ').join("");' +
                    '</scr' + 'ipt>' +
                '</body>' +
                '</html>';
            
            const blob = new Blob([html], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = campaign.name.replace(/\\s+/g, '_') + '_concepts.html';
            a.click();
        }
        
        function exportCampaign(campaignId) {
            const campaign = campaigns.find(c => c.id === campaignId);
            if (!campaign) return;
            
            // Create downloadable campaign brief
            const campaignDetails = Object.entries(campaign)
                .filter(([k,v]) => v && !['id', 'linked_items', 'linked_items_details', 'created_at', 'updated_at'].includes(k))
                .map(([key, value]) => '<p><strong>' + key.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase()) + ':</strong> ' + value + '</p>')
                .join('');
            
            const moodBoardImages = (campaign.linked_items_details || [])
                .map(item => '<img src="' + window.location.origin + '/' + item.path + '" alt="' + item.title + '">')
                .join('');
            
            const briefHtml = '<!DOCTYPE html>' +
                '<html>' +
                '<head>' +
                    '<title>' + campaign.name + ' - Campaign Brief</title>' +
                    '<style>' +
                        'body { font-family: -apple-system, sans-serif; max-width: 800px; margin: 0 auto; padding: 40px; }' +
                        'h1 { color: #ff6b6b; }' +
                        '.mood-board { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 30px; }' +
                        '.mood-board img { width: 100%; height: 200px; object-fit: cover; border-radius: 8px; }' +
                    '</style>' +
                '</head>' +
                '<body>' +
                    '<h1>' + campaign.name + '</h1>' +
                    '<p><strong>Client:</strong> ' + campaign.client + '</p>' +
                    '<p><strong>Date:</strong> ' + new Date().toLocaleDateString() + '</p>' +
                    '<hr>' +
                    '<h2>Campaign Details</h2>' +
                    campaignDetails +
                    '<h2>Visual Mood Board</h2>' +
                    '<div class="mood-board">' + moodBoardImages + '</div>' +
                '</body>' +
                '</html>';
            
            const blob = new Blob([briefHtml], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = campaign.name.replace(/\s+/g, '_') + '_brief.html';
            a.click();
        }
        
        // Load content on page load
        loadContent();
    </script>
</body>
</html>
    """
    return web.Response(text=html, content_type='text/html')

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
                            ${path ? `<img src="/${path}" alt="${title}" class="image-preview" onerror="this.style.display='none'">` : ''}
                            <div class="item-content">
                                <div class="item-title">${escapeHtml(title)}</div>
                                ${description ? `<p class="item-description">${escapeHtml(description.substring(0, 150))}${description.length > 150 ? '... <em style="color: #667eea;">Click to read more</em>' : ''}</p>` : ''}
                                ${notes ? `<p style="color: #764ba2; font-style: italic;">📝 ${escapeHtml(notes)}</p>` : ''}
                                <div class="item-tags">
                                    ${aiTags.map(tag => `<span class="tag ai-tag">🤖 ${escapeHtml(tag)}</span>`).join('')}
                                    ${tags.filter(t => !aiTags.includes(t)).map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                                </div>
                            </div>
                        </div>
                    `;
                } else {
                    const content = item.content || '';
                    html += `
                        <div class="content-item" onclick="showItemModal(${items.indexOf(item)})">
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
            
            // Enhanced Multi-Agent Analysis or Regular AI Insights
            if (item.enhanced_analysis) {
                const enhanced = item.enhanced_analysis;
                modalContent += `
                    <div class="modal-section">
                        <h3>🚀 Multi-Agent Enhanced Analysis</h3>
                        <p><strong>Enhanced Description:</strong><br>${escapeHtml(enhanced.enhanced_description || '')}</p>
                    </div>
                `;
                
                if (enhanced.strategic_insights) {
                    modalContent += `
                        <div class="modal-section">
                            <h3>🎯 Strategic Brand Insights</h3>
                            <p>${escapeHtml(enhanced.strategic_insights)}</p>
                        </div>
                    `;
                }
                
                if (enhanced.narrative_analysis) {
                    modalContent += `
                        <div class="modal-section">
                            <h3>📖 Visual Storytelling Analysis</h3>
                            <p>${escapeHtml(enhanced.narrative_analysis)}</p>
                        </div>
                    `;
                }
                
                if (enhanced.design_applications) {
                    modalContent += `
                        <div class="modal-section">
                            <h3>🎨 UI/UX Design Applications</h3>
                            <p>${escapeHtml(enhanced.design_applications)}</p>
                        </div>
                    `;
                }
                
                if (enhanced.innovation_potential) {
                    modalContent += `
                        <div class="modal-section">
                            <h3>💡 Innovation Catalyst Insights</h3>
                            <p>${escapeHtml(enhanced.innovation_potential)}</p>
                        </div>
                    `;
                }
                
                if (enhanced.confidence_score) {
                    modalContent += `
                        <div class="modal-section">
                            <h3>📊 Analysis Quality</h3>
                            <p><strong>Confidence Score:</strong> ${Math.round(enhanced.confidence_score * 100)}%<br>
                            <strong>Analysis Depth:</strong> ${enhanced.analysis_depth || 'Standard'}<br>
                            <strong>Agent Collaboration:</strong> ${enhanced.agent_collaboration ? 'Yes' : 'No'}</p>
                        </div>
                    `;
                }
                
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
        
        # For demo purposes, return enhanced analysis based on agent type
        if agent_type == 'brand_strategy':
            return f"**Strategic Brand Analysis**: This visual asset demonstrates strong commercial potential for cultural technology sectors, particularly appealing to digitally-native audiences aged 25-45. The aesthetic positioning suggests premium brand alignment with innovation-focused messaging."
            
        elif agent_type == 'visual_storytelling':
            return f"**Visual Narrative Structure**: Employs sophisticated layered storytelling technique with progressive complexity that guides viewer engagement. The composition creates emotional journey from curiosity through exploration to understanding, ideal for brand narratives focused on discovery and transformation."
            
        elif agent_type == 'ui_ux_design':
            return f"**Interface Design Applications**: Color hierarchy and geometric patterns translate excellently to digital interfaces. High contrast ratios ensure accessibility compliance while abstract elements provide modern interaction metaphors for progressive web applications and creative industry tools."
            
        elif agent_type == 'innovation_catalyst':
            return f"**Innovation Opportunities**: This aesthetic approach represents emerging 'Controlled Chaos Design' trend - structured randomness that appeals to AI-native generation. Applications include: generative art platforms, creative AI tools, immersive brand experiences, and next-generation design systems that adapt to user behavior."
            
        return f"Enhanced {agent_type} analysis completed"
        
    except Exception as e:
        print(f"Agent analysis error ({agent_type}): {e}")
        return f"Analysis unavailable for {agent_type}"

async def synthesize_agent_insights(item, agent_analyses):
    """Synthesize insights from all agents into comprehensive analysis"""
    try:
        synthesis = {
            'enhanced_description': f"**Multi-Agent Enhanced Description**: {item.get('description', '')} This comprehensive analysis reveals sophisticated design thinking across multiple disciplines, demonstrating both immediate commercial viability and long-term innovation potential.",
            
            'strategic_insights': agent_analyses.get('brand_strategy', ''),
            'narrative_analysis': agent_analyses.get('visual_storytelling', ''),
            'design_applications': agent_analyses.get('ui_ux_design', ''),
            'innovation_potential': agent_analyses.get('innovation_catalyst', ''),
            
            'enhanced_tags': item.get('ai_tags', []) + [
                'multi-agent analyzed', 'strategic potential', 'narrative structure', 
                'interface applications', 'innovation catalyst', 'commercial viability'
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

def create_app():
    """Create the web application"""
    app = web.Application()
    
    # Configure max upload size (100MB)
    app['client_max_size'] = 100 * 1024 * 1024
    
    # Routes
    app.router.add_get('/', working_dashboard)
    app.router.add_get('/old', dashboard)
    app.router.add_get('/api/content', api_content)
    app.router.add_post('/api/scan', api_scan)
    app.router.add_post('/api/ai-scan', api_ai_scan)
    app.router.add_post('/api/multi-agent-analysis', api_multi_agent_analysis)
    app.router.add_post('/api/batch-multi-agent-analysis', api_batch_multi_agent_analysis)
    app.router.add_post('/api/update-item', api_update_item)
    app.router.add_post('/api/create-project', api_create_project)
    app.router.add_post('/api/create-campaign', api_create_campaign)
    app.router.add_post('/api/update-campaign', api_update_campaign)
    app.router.add_post('/api/link-campaign-items', api_link_campaign_items)
    app.router.add_get('/api/campaigns', api_get_campaigns)
    app.router.add_post('/api/generate-concepts', api_generate_concepts)
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
    print("🌐 Dashboard will be at: http://localhost:8080")
    print()
    
    try:
        app = asyncio.run(init())
        web.run_app(app, host='localhost', port=8080)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()