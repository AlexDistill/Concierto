# Manual Content Input Instructions

## How to add content:

1. **Images**: 
   - Drop image files (.jpg, .png, .gif, .webp, .svg) directly into this folder
   - Optionally add a .json file with the same name for metadata
   
   Example: mydesign.png + mydesign.png.json

2. **Metadata JSON format**:
   ```json
   {
     "title": "Amazing Design Concept",
     "description": "This design showcases...",
     "tags": ["minimal", "typography", "bold"],
     "category": "branding",
     "source_url": "https://example.com"
   }
   ```

3. **Inspiration Data**:
   Create a .json file with inspiration content:
   ```json
   {
     "content": "Design insight or concept text",
     "inspiration": "What makes this inspiring",
     "tags": ["creative", "innovative"],
     "reference": "Source or attribution"
   }
   ```

4. **Bulk Import**:
   You can add multiple files at once. The ingester will process them all.

Files added here will be:
- Automatically detected on the next ingestion cycle
- Analyzed and categorized
- Made available to all agents for inspiration
- Preserved in the content cache

The system checks this folder every few minutes!
