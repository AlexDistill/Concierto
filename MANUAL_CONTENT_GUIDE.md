# Manual Content Import Guide

## 🎯 Two Ways to Add Content

### Method 1: Drop Images (Zero Effort)

**Just drag and drop images into:**
```
/content/manual-input/images/
```

**What happens automatically:**
- ✅ **Filename becomes title:** `bold_typography_example.jpg` → "Bold Typography Example"
- ✅ **Tags extracted:** Keywords like "bold", "typography", "minimal", "ui" become tags
- ✅ **JSON metadata created:** Each image gets a companion `.json` file
- ✅ **Available to agents:** Within 4 minutes, all 38 agents can use it for inspiration

**Supported formats:** .jpg, .jpeg, .png, .gif, .webp, .svg, .bmp

**Pro tip:** Use descriptive filenames with keywords:
- `minimal_web_design_2025.png`
- `bold_typography_gradient.jpg`
- `modern_ui_interface_mobile.webp`

---

### Method 2: Google Sheets (Structured Data)

**Setup your sheet with these columns:**
| title | source_url | reference | description | tags | category |
|-------|------------|-----------|-------------|------|----------|

**Example entries:**
```
Bold Typography Trend | https://twitter.com/FigsFromPlums/status/123 | FigsFromPlums post | Typography trends | typography,bold,2025 | design-trends
Minimal UI Examples | https://dribbble.com/shots/12345 | Dribbble | Clean interfaces | minimal,ui,clean | ui-design
```

**Steps to import:**
1. **Create Google Sheet** with the columns above
2. **Fill in your content** (title is required, others optional)
3. **Make publicly viewable:** Share → Anyone with link can view
4. **Get CSV export URL:** File → Download → CSV → Copy URL
5. **Import to system:** `python3 scripts/spreadsheet_importer.py "YOUR_CSV_URL"`

**The CSV URL looks like:**
```
https://docs.google.com/spreadsheets/d/SHEET_ID/export?format=csv&gid=0
```

---

## 🔄 How the System Works

### Automatic Processing Schedule
- **Every 4 minutes:** System checks for new images and spreadsheet updates
- **Immediate processing:** Drop files and they're detected on next cycle
- **Zero duplicates:** Already processed files are skipped
- **Full integration:** New content immediately available to all agents

### What Gets Created
For each piece of content, the system creates:
- **Unique ID:** For tracking and deduplication
- **Metadata JSON:** Structured data with title, tags, source
- **Cache entry:** Added to main content database
- **Agent availability:** Accessible for inspiration and generation

### Content Categories
The system automatically categorizes content:
- **Images:** `visual_inspiration`
- **Spreadsheet:** `inspiration_data`
- **Auto-detected types:** `design-trends`, `ui-design`, `typography`, etc.

---

## 📊 Monitoring Your Content

### View Your Added Content
- **Content Viewer:** http://localhost:8080/content-viewer.html
- **Source Verification:** Open `content/content-verification-report.html`
- **Activity Logs:** Check logs for import confirmations

### Import Status
Check import results:
```bash
# View latest import summary
cat content/manual-input/latest_import.json

# Check processing logs
tail -f logs/autonomous.log | grep "manual"
```

---

## 🛠️ Advanced Usage

### Automatic Spreadsheet Sync
Configure regular imports by adding your CSV URL to the system:
1. Create a config file with your spreadsheet URL
2. System will check for updates automatically
3. New rows are imported without duplicates

### Batch Image Processing
Drop multiple images at once:
- System processes all new images in one cycle
- Each gets individual metadata
- Processed list prevents re-processing

### Custom Metadata for Images
Add a `.json` file alongside your image for custom data:
```json
// bold_design.jpg.json
{
  "title": "Custom Title Override",
  "source_url": "https://inspiration-source.com",
  "tags": ["custom", "tags", "here"],
  "description": "Custom description"
}
```

---

## 📁 Directory Structure

```
content/manual-input/
├── images/                     # Drop images here
│   ├── your-image.jpg         # Your image files
│   ├── your-image_auto.json   # Auto-generated metadata
│   └── README.md              # Instructions
├── spreadsheet-data/          # Imported spreadsheet data
│   ├── spreadsheet_item1.json # Individual import entries
│   └── README.md              # Instructions
├── google-sheets-template.md  # Setup guide
├── latest_import.json         # Last import summary
└── processed_images.json      # Tracking file
```

---

## 🎨 Agent Integration

Once imported, your content is used by:

### Design Agents
- **visual-storyteller:** Creates concepts from your images
- **innovation-catalyst:** Analyzes trends in your references
- **brand-guardian:** Ensures consistency with your examples

### Content Agents
- **content-creator:** Generates copy inspired by your references
- **trend-researcher:** Identifies patterns in your curated content
- **growth-hacker:** Applies successful examples to campaigns

### All 38 Agents
Every agent has access to search and use your manual content for:
- **Inspiration and reference**
- **Style and tone guidance**  
- **Trend analysis**
- **Creative concept generation**

---

## 🚀 Quick Start Checklist

### For Image Upload:
- [ ] Drop images into `/content/manual-input/images/`
- [ ] Use descriptive filenames with keywords
- [ ] Wait 4 minutes for processing
- [ ] Check content viewer for results

### For Spreadsheet:
- [ ] Create Google Sheet with required columns
- [ ] Make publicly viewable
- [ ] Get CSV export URL
- [ ] Run import command
- [ ] Verify in content viewer

### Monitor Results:
- [ ] Check http://localhost:8080/content-viewer.html
- [ ] View source verification report
- [ ] Monitor activity logs
- [ ] Test agent access to new content

**Need help?** Check the instruction files in each folder or the activity logs for troubleshooting.