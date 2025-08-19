#!/usr/bin/env python3
"""
Simple, working content server for Concierto.
No over-engineering - just a dashboard that works.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from aiohttp import web
import aiofiles

class SimpleContentManager:
    """Dead simple content management"""
    
    def __init__(self):
        self.content_dir = Path("content")
        self.images_dir = self.content_dir / "images"
        self.notes_dir = self.content_dir / "notes"
        self.data_file = self.content_dir / "data.json"
        
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
                    "path": str(image_file.relative_to(Path.cwd())),
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
        
        return new_items
    
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
        <button class="refresh-btn" onclick="refreshContent()">
            📱 Scan for New Content
        </button>
        
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
        async function loadContent() {
            try {
                const response = await fetch('/api/content');
                const data = await response.json();
                
                // Update stats
                const statsHtml = `
                    <div class="stat-card">
                        <div class="stat-number">${data.items.length}</div>
                        <div class="stat-label">Total Items</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.items.filter(i => i.type === 'image').length}</div>
                        <div class="stat-label">Images</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.items.filter(i => i.type === 'note').length}</div>
                        <div class="stat-label">Notes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.tags.length}</div>
                        <div class="stat-label">Tags</div>
                    </div>
                `;
                document.getElementById('stats').innerHTML = statsHtml;
                
                // Update content
                if (data.items.length === 0) {
                    document.getElementById('content').innerHTML = `
                        <div class="empty-state">
                            <h3>No content yet!</h3>
                            <p>Add some images to the content/images/ folder and click "Scan for New Content"</p>
                        </div>
                    `;
                } else {
                    const contentHtml = data.items.map(item => {
                        if (item.type === 'image') {
                            return `
                                <div class="content-item">
                                    <img src="/${item.path}" alt="${item.title}" class="image-preview" 
                                         onerror="this.style.display='none'">
                                    <div class="item-content">
                                        <div class="item-title">${item.title}</div>
                                        <div class="item-tags">
                                            ${item.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                                        </div>
                                    </div>
                                </div>
                            `;
                        } else {
                            return `
                                <div class="content-item">
                                    <div class="item-content">
                                        <div class="item-title">${item.title}</div>
                                        <p>${item.content.substring(0, 150)}${item.content.length > 150 ? '...' : ''}</p>
                                        <div class="item-tags">
                                            ${item.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                                        </div>
                                    </div>
                                </div>
                            `;
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
                await fetch('/api/scan', { method: 'POST' });
                await loadContent();
            } catch (error) {
                console.error('Failed to refresh content:', error);
            } finally {
                document.body.classList.remove('loading');
            }
        }
        
        // Load content on page load
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
    return web.json_response({"scanned": len(new_items), "new_items": new_items})

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

def create_app():
    """Create the web application"""
    app = web.Application()
    
    # Routes
    app.router.add_get('/', dashboard)
    app.router.add_get('/api/content', api_content)
    app.router.add_post('/api/scan', api_scan)
    app.router.add_get('/{path:.*}', serve_file)
    
    return app

async def init():
    """Initialize the application"""
    # Scan for existing content on startup
    print("🔍 Scanning for existing content...")
    new_items = content_manager.scan_images()
    if new_items:
        print(f"📸 Found {len(new_items)} new images")
    
    # Start server
    app = create_app()
    return app

if __name__ == '__main__':
    print("🎼 Starting Concierto - Simple Content Dashboard")
    print("📁 Make sure to put your images in: content/images/")
    print("🌐 Dashboard will be at: http://localhost:8080")
    print()
    
    web.run_app(init(), host='localhost', port=8080)