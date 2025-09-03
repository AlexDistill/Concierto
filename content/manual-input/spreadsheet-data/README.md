# Google Sheets Integration

## Setup Instructions

1. **Create a Google Sheet with these columns:**
   - `title` (required) - Name/title of the inspiration
   - `source_url` (optional) - Link to original source
   - `reference` (optional) - Attribution or notes
   - `description` (optional) - Detailed description
   - `tags` (optional) - Comma-separated tags
   - `category` (optional) - Content category

2. **Make the sheet publicly viewable:**
   - File → Share → Anyone with the link can view
   - File → Download → CSV → Copy the download link

3. **Import the data:**
   - Run: `python3 scripts/spreadsheet_importer.py [CSV_URL]`
   - Or configure automatic import in the system

## Example Sheet Structure:
```
title                    | source_url                      | reference           | tags                    | category
Bold Typography Trend    | https://example.com/post1       | Seen on FigsFromPlums| typography,bold,trends  | design-trends
Minimal UI Examples      | https://dribbble.com/shot/123   | Dribbble inspiration | minimal,ui,clean        | ui-design
Color Palette Ideas      | https://coolors.co/palette/456  | Color inspiration    | colors,palette,modern   | color-theory
```

## Template Sheet:
Copy this template: [Create template link here]

## Automatic Import:
The system can check your sheet regularly for updates. Configure the CSV URL in the settings.
