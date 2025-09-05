#!/usr/bin/env python3
"""
Minimal working server - just the essentials
"""

import json
import os
from pathlib import Path
from aiohttp import web

def get_content():
    """Get all content from content/data.json"""
    content_file = Path('content/data.json')
    if content_file.exists():
        with open(content_file) as f:
            return json.load(f)
    return {"items": [], "brands": []}

async def index(request):
    """Serve the dashboard"""
    html = '''<!DOCTYPE html>
<html>
<head>
    <title>Working Dashboard</title>
    <style>
        body { font-family: system-ui; padding: 20px; background: #f0f0f0; }
        h1 { color: #667eea; }
        .content-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
        .content-item { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); cursor: pointer; transition: transform 0.2s; }
        .content-item:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }
        .item-title { font-weight: bold; color: #333; margin-bottom: 8px; }
        .item-description { color: #666; font-size: 14px; line-height: 1.4; }
        .loading { color: #999; padding: 40px; text-align: center; }
        .error { color: red; padding: 20px; }
        .tag { display: inline-block; background: #e0e7ff; color: #667eea; padding: 2px 8px; border-radius: 12px; margin: 2px; font-size: 12px; }
    </style>
</head>
<body>
    <h1>🎨 Concierto Dashboard</h1>
    <div id="status"></div>
    <button onclick="window.location.reload()">🔄 Refresh</button>
    <button onclick="manualLoad()">📥 Load Content</button>
    
    <div id="stats"></div>
    <div id="content" class="content-grid">
        <div class="loading">Loading content...</div>
    </div>
    
    <script>
        console.log('Script started');
        
        function manualLoad() {
            console.log('Manual load triggered');
            loadContent();
        }
        
        function loadContent() {
            console.log('loadContent called');
            const contentDiv = document.getElementById('content');
            const statsDiv = document.getElementById('stats');
            
            fetch('/api/content')
                .then(response => {
                    console.log('Response received:', response.status);
                    return response.json();
                })
                .then(data => {
                    console.log('Data received:', data);
                    
                    // Update stats
                    if (statsDiv) {
                        statsDiv.innerHTML = '<p>📊 Items: ' + (data.items ? data.items.length : 0) + 
                                           ' | 🎨 Brands: ' + (data.brands ? data.brands.length : 0) + '</p>';
                    }
                    
                    // Display content
                    if (data.items && data.items.length > 0) {
                        let html = '';
                        data.items.forEach(item => {
                            html += '<div class="content-item">';
                            html += '<div class="item-title">' + (item.title || 'Untitled') + '</div>';
                            if (item.description) {
                                html += '<div class="item-description">' + 
                                       item.description.substring(0, 150) + 
                                       (item.description.length > 150 ? '...' : '') + 
                                       '</div>';
                            }
                            if (item.tags && item.tags.length > 0) {
                                html += '<div>';
                                item.tags.slice(0, 5).forEach(tag => {
                                    html += '<span class="tag">' + tag + '</span>';
                                });
                                html += '</div>';
                            }
                            html += '</div>';
                        });
                        contentDiv.innerHTML = html;
                    } else {
                        contentDiv.innerHTML = '<div class="loading">No content found</div>';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    contentDiv.innerHTML = '<div class="error">Error loading content: ' + error.message + '</div>';
                });
        }
        
        // Load on page ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', loadContent);
        } else {
            loadContent();
        }
    </script>
</body>
</html>'''
    return web.Response(text=html, content_type='text/html')

async def api_content(request):
    """API endpoint for content"""
    data = get_content()
    return web.json_response(data)

# Create app
app = web.Application()
app.router.add_get('/', index)
app.router.add_get('/api/content', api_content)

if __name__ == '__main__':
    print("🚀 Starting minimal working server on http://localhost:8082")
    print("📁 Reading from content/data.json")
    web.run_app(app, host='localhost', port=8082)