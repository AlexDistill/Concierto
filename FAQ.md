# Concierto FAQ - Frequently Asked Questions

## 🚀 Quick Start Commands

### **How do I start the system?**
```bash
./launch_concierto.sh
```
This starts the full system (API server + scheduled content ingestion).

### **How do I start just the web server?**
```bash
python main.py server
```

### **How do I run content ingestion manually?**
```bash
python main.py ingest
```

### **How do I check if everything is working?**
```bash
python main.py health
```

## 📊 System Information Commands

### **How do I see system statistics?**
```bash
python main.py stats
```
Shows total items, breakdown by source, top tags, etc.

### **How do I see what sources are available?**
```bash
python main.py health
```
This shows all sources and whether they're healthy.

### **How do I run ingestion from specific sources only?**
```bash
python main.py ingest --sources twitter,siteinspire
python main.py ingest --sources manual
```

### **How do I fetch more items per source?**
```bash
python main.py ingest --limit 50
```

## 📥 Content Import

### **How do I import from Google Sheets?**
1. Make your Google Sheet public (Anyone with link can view)
2. Get the CSV export URL: File → Download → CSV
3. Run:
```bash
python main.py import-csv "https://docs.google.com/spreadsheets/d/YOUR_ID/export?format=csv"
```

### **How do I add images manually?**
1. Drop images into: `content/manual-input/images/`
2. Images are automatically processed during ingestion
3. Use descriptive filenames for better tag extraction

### **What image formats are supported?**
- `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.svg`, `.bmp`

## 🔧 Troubleshooting

### **Port 8080 is already in use**
The launch script automatically kills existing processes, but you can also:
```bash
lsof -ti:8080 | xargs kill -9
```

### **Twitter scraping isn't working**
This is expected due to Twitter API restrictions. The system will:
- Try multiple fallback methods
- Log clear error messages
- Continue working with other sources

### **Content isn't showing in dashboard**
1. Check if server is running: `python main.py health`
2. Check if ingestion found content: `python main.py stats`
3. Restart the system: `./launch_concierto.sh`

### **How do I enable debug logging?**
Add `--debug` to any command:
```bash
python main.py run --debug
python main.py ingest --debug
```

## 🌐 Dashboard Access

### **Where is the dashboard?**
- Main dashboard: http://localhost:8080/dashboard
- API health check: http://localhost:8080/api/health
- Content API: http://localhost:8080/api/content

### **How do I change the server port?**
```bash
python main.py server --port 8081
python main.py run --port 8081
```

## 📁 File Locations

### **Where is content stored?**
- Main content database: `content/scraped/content_cache.json`
- Manual images: `content/manual-input/images/`
- Spreadsheet imports: `content/manual-input/spreadsheet-data/`

### **Where are the logs?**
- Console output shows main events
- Detailed logs available with `--debug` flag

### **Where is configuration stored?**
- Main config: `config/settings.py`
- Environment variables for sensitive data

## 🔄 Content Sources

### **What sources are available?**
1. **Twitter** (@FigsFromPlums) - Design inspiration tweets
2. **SiteInspire** - Latest website designs via RSS
3. **Manual** - Your uploaded images and spreadsheet imports

### **How often does automatic ingestion run?**
- Default: Every 30 minutes when using `python main.py run`
- Configurable in `config/settings.py`

### **How do I disable a specific source?**
Edit `config/settings.py` and set `enabled: False` for that source.

## 📊 Content Management

### **How do I see all content?**
Visit: http://localhost:8080/api/content

### **How do I delete content items?**
Use the API:
```bash
curl -X DELETE http://localhost:8080/api/content/ITEM_ID
```

### **How do I backup my content?**
The content database is in `content/scraped/content_cache.json` - copy this file.

## 🛠️ Development

### **How do I run different commands?**
```bash
python main.py --help                    # See all commands
python main.py ingest --help            # Help for specific command
```

### **How do I modify source configurations?**
Edit `config/settings.py` and restart the system.

### **How do I add a new content source?**
1. Create new class in `sources/` extending `ContentSource`
2. Register it in `core/pipeline.py`
3. Add configuration in `config/settings.py`

## 🆘 Emergency Commands

### **System completely broken?**
```bash
# Check what's wrong
python main.py health --debug

# Fresh restart
./launch_concierto.sh
```

### **Need to reset everything?**
```bash
# Backup first!
cp content/scraped/content_cache.json content_backup.json

# Then you can delete and restart
rm content/scraped/content_cache.json
./launch_concierto.sh
```

### **Performance issues?**
```bash
# Check system stats
python main.py stats

# Run with debug to see bottlenecks
python main.py ingest --debug --limit 5
```

## 📞 Quick Reference Card

| Task | Command |
|------|---------|
| **Start everything** | `./launch_concierto.sh` |
| **Check health** | `python main.py health` |
| **Manual ingestion** | `python main.py ingest` |
| **View statistics** | `python main.py stats` |
| **Import Google Sheets** | `python main.py import-csv URL` |
| **Debug mode** | Add `--debug` to any command |
| **Change port** | Add `--port 8081` to server commands |
| **Specific sources** | `--sources twitter,siteinspire,manual` |
| **More items** | `--limit 50` |

---

💡 **Pro Tips:**
- Use `--debug` flag to see detailed logs
- The system continues working even if one source fails
- Images are automatically tagged based on filename keywords
- Google Sheets must be public to import via CSV URL
- All existing data is preserved during system updates