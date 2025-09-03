#!/usr/bin/env python3

from aiohttp import web
import json
from pathlib import Path

# Load existing data
data_file = Path('content/data.json')
if data_file.exists():
    with open(data_file) as f:
        data = json.load(f)
else:
    data = {"items": [], "tags": []}

async def index(request):
    html = '''<!DOCTYPE html>
<html>
<head>
    <title>Concierto</title>
    <style>
        body { font-family: Arial; padding: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
        .item { border: 1px solid #ddd; padding: 10px; }
        img { width: 100%; height: 200px; object-fit: cover; }
    </style>
</head>
<body>
    <h1>Concierto Dashboard</h1>
    <div id="stats"></div>
    <div id="content" class="grid"></div>
    
    <script>
        fetch('/api/content')
            .then(r => r.json())
            .then(data => {
                document.getElementById('stats').innerHTML = 'Total: ' + data.items.length + ' items';
                
                var html = '';
                data.items.forEach(item => {
                    if (item.type === 'image') {
                        html += '<div class="item">';
                        html += '<img src="/' + item.path + '">';
                        html += '<p>' + item.title + '</p>';
                        html += '</div>';
                    }
                });
                document.getElementById('content').innerHTML = html;
            });
    </script>
</body>
</html>'''
    return web.Response(text=html, content_type='text/html')

async def api_content(request):
    return web.json_response(data)

async def serve_image(request):
    path = request.match_info['path']
    file_path = Path('content/images') / path
    if file_path.exists():
        return web.FileResponse(file_path)
    return web.Response(status=404)

app = web.Application()
app.router.add_get('/', index)
app.router.add_get('/api/content', api_content)
app.router.add_get('/content/images/{path}', serve_image)

if __name__ == '__main__':
    print("Starting minimal server on http://localhost:8080")
    web.run_app(app, host='localhost', port=8080)