# Google Sheets Template for Content Import

## Quick Setup

1. **Copy this template:** https://docs.google.com/spreadsheets/d/1234567890/copy
   *(Note: Replace with actual template link when created)*

2. **Or create your own sheet with these exact column headers:**

| title | source_url | reference | description | tags | category |
|-------|------------|-----------|-------------|------|----------|
| Bold Typography Trend 2025 | https://twitter.com/FigsFromPlums/status/123 | FigsFromPlums post | Oversized typography with gradients | typography,bold,gradient,2025 | design-trends |
| Minimal UI Inspiration | https://dribbble.com/shots/12345 | Dribbble showcase | Clean interface design | minimal,ui,clean,interface | ui-design |
| Color Palette Reference | https://coolors.co/palette/456789 | Coolors.co | Modern brand colors | colors,palette,branding | color-theory |

## Column Descriptions

- **title** (required): Name or title of the inspiration
- **source_url** (optional): Link to the original source
- **reference** (optional): Attribution or where you found it
- **description** (optional): Detailed description of what makes it inspiring
- **tags** (optional): Comma-separated keywords (typography,bold,modern)
- **category** (optional): Content category (design-trends, ui-design, etc.)

## Usage Instructions

### Step 1: Fill in your content
Add rows with your inspiration sources, one per row.

### Step 2: Make publicly accessible
- Go to File → Share → Change to "Anyone with the link"
- Set permission to "Viewer"

### Step 3: Get CSV export link
- Go to File → Download → Comma-separated values (.csv)
- Copy the download URL (it looks like: https://docs.google.com/spreadsheets/d/SHEET_ID/export?format=csv&gid=0)

### Step 4: Import to Concierto
Run the import command:
```bash
python3 scripts/spreadsheet_importer.py "YOUR_CSV_URL"
```

Or for automatic import, add the URL to your configuration.

## Example Workflow

1. **Find inspiration** on Twitter, Dribbble, Behance, etc.
2. **Add to sheet:** title, source URL, quick note
3. **Run import** or wait for automatic sync
4. **Content is available** to all agents immediately

## Tips for Better Results

### Good Titles
- "Bold Typography in Web Design"
- "Minimalist App Interface Examples"
- "Creative Color Gradients"

### Useful Tags
- Design: minimal, bold, modern, classic, vintage
- Content: typography, layout, color, animation
- Platform: web, mobile, print, social
- Style: gradient, monochrome, colorful, dark, light

### Categories
- design-trends
- ui-design
- color-theory
- typography
- branding
- visual-inspiration
- creative-concepts

## Automatic Sync

You can configure the system to check your sheet every few minutes:
1. Add your CSV URL to the configuration
2. The system will automatically import new rows
3. Agents will have access to the latest inspiration

## Sample CSV URL Format
```
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/export?format=csv&gid=0
```

Replace the SHEET_ID with your actual Google Sheets ID.