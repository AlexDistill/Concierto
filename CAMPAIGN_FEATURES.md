# Campaign Management System

## 🎯 Overview

Concierto now includes a comprehensive Campaign Management System that allows you to:
- Create detailed campaign concepts
- Link mood board images to campaigns
- Track campaign details and deliverables
- Export campaign briefs
- (Coming Soon) AI-powered theme analysis and concept generation

## 📋 Campaign Features

### 1. **Campaign Creation**
Create comprehensive campaign briefs with:
- **Campaign Name** - The campaign title
- **Client** - Client/brand name
- **Objective** - Campaign goals and KPIs
- **Target Audience** - Demographics and psychographics
- **Key Messages** - Core communication points
- **Tone & Voice** - Brand personality and style
- **Deliverables** - Expected outputs
- **Timeline** - Project schedule
- **Budget Range** - Financial parameters
- **Inspiration Notes** - Creative direction notes

### 2. **Mood Board Integration**
- Link any images from your content library to campaigns
- Visual selection interface with thumbnails
- View all linked images in campaign overview
- Export mood boards with campaign briefs

### 3. **Campaign Management**
- View all campaigns in organized cards
- Status tracking (concept, active, completed)
- Edit and update campaign details
- Link/unlink mood board items dynamically

### 4. **Export Capabilities**
- Export complete campaign briefs as HTML
- Includes all campaign details and mood board
- Self-contained files for easy sharing
- Professional formatting for client presentations

## 🚀 How to Use

### Creating a Campaign

1. Click the **"📋 Campaigns"** button in the dashboard
2. Click **"+ New Campaign"** 
3. Fill in campaign details:
   - Required: Name, Client, Objective
   - Optional: All other fields
4. Select mood board images by clicking thumbnails
5. Click **"Create Campaign"**

### Managing Campaigns

- Click any campaign card to view details
- View linked mood board items
- Export campaign brief as HTML
- (Coming Soon) Generate AI visual concepts

## 🔗 API Reference

### Create Campaign
```bash
curl -X POST http://localhost:8080/api/create-campaign \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Campaign Name",
    "client": "Client Name",
    "objective": "Campaign objectives...",
    "target_audience": "Target demographics...",
    "key_messages": "Core messages...",
    "tone_voice": "Brand voice...",
    "linked_items": ["img_1", "img_2"]
  }'
```

### Get All Campaigns
```bash
curl http://localhost:8080/api/campaigns
```

### Update Campaign
```bash
curl -X POST http://localhost:8080/api/update-campaign \
  -H "Content-Type: application/json" \
  -d '{
    "id": "campaign_1",
    "name": "Updated Name",
    "status": "active"
  }'
```

### Link Items to Campaign
```bash
curl -X POST http://localhost:8080/api/link-campaign-items \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "campaign_1",
    "item_ids": ["img_3", "img_4"],
    "action": "add"
  }'
```

## 🎨 Coming Soon: AI-Powered Features

### Theme Analysis
- Automatic detection of visual themes across mood board
- Color palette extraction
- Style and mood analysis
- Common elements identification

### Visual Concept Generation
- AI-generated concepts based on campaign brief
- Theme-aware image generation using DALL-E
- Multiple concept variations
- Style transfer from mood board

### Content Suggestions
- Copy recommendations based on visual themes
- Hashtag and keyword suggestions
- Platform-specific content adaptations

## 📊 Campaign Data Structure

Campaigns are stored in `content/data.json`:

```json
{
  "campaigns": [{
    "id": "campaign_1",
    "name": "Summer Vibes 2025",
    "client": "BeachCo",
    "objective": "Launch summer collection",
    "target_audience": "25-40 eco-conscious",
    "key_messages": "Sustainable, vibrant",
    "tone_voice": "Fresh, energetic",
    "deliverables": "Social, web, print",
    "timeline": "Q2 2025",
    "budget_range": "$50k-100k",
    "inspiration_notes": "Beach lifestyle focus",
    "linked_items": ["img_1", "img_5"],
    "status": "concept",
    "created_at": "2025-08-28T...",
    "updated_at": "2025-08-28T..."
  }]
}
```

## 💡 Best Practices

1. **Comprehensive Briefs**: Fill in as much detail as possible for better AI concept generation
2. **Curated Mood Boards**: Select 5-10 images that best represent the campaign vision
3. **Clear Objectives**: Specific, measurable objectives lead to better creative outputs
4. **Regular Updates**: Keep campaign status and details current
5. **Export for Sharing**: Use HTML export for client presentations

## 🔧 Technical Details

- **Backend**: Python/aiohttp API endpoints
- **Frontend**: Vanilla JavaScript with modal interfaces
- **Storage**: JSON database with relational linking
- **AI Integration**: OpenAI GPT-4 Vision API (configured)

---

The Campaign Management System transforms Concierto from a simple mood board tool into a comprehensive creative campaign platform.