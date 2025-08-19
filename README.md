# Concierto - AI Agent Content Orchestration System

A simple, working content curation and dashboard system designed for creative professionals.

## 🎯 **Philosophy: Simple & Working**

After building an over-engineered system with multiple scrapers and complex architecture, we're starting fresh with a focus on:
- **Manual curation over automation** - Quality content beats quantity
- **Working features over complex ones** - Simple dashboard that actually works
- **Easy content management** - Drop files, see results immediately

## 🚀 **Quick Start**

```bash
# Clone the repository
git clone https://github.com/AlexDistill/Concierto.git
cd Concierto

# Install dependencies
pip install aiohttp aiofiles

# Optional: Set up AI image analysis
python3 setup_ai.py

# Start the dashboard
python3 simple_server.py
```

Visit http://localhost:8080 to see your content dashboard.

## 📁 **Project Structure**

```
Concierto/
├── content/                 # Your curated content
│   ├── images/             # Drop your inspiration images here
│   ├── notes/              # Text notes and insights
│   └── data.json           # Simple content database
├── dashboard/              # Web dashboard
│   ├── index.html         # Main dashboard
│   ├── style.css          # Clean, modern styling
│   └── script.js          # Simple interactions
├── simple_server.py       # Lightweight server
├── content_manager.py     # Simple content management
└── README.md              # This file
```

## 💡 **Features**

### ✅ **Working Features**
- **Image Gallery** - Visual inspiration board
- **🤖 AI Image Analysis** - Intelligent content understanding
- **Smart Tagging** - Auto-generated tags from AI + filenames
- **Creative Insights** - AI-powered design analysis
- **Note Taking** - Quick creative insights
- **Search** - Find what you need quickly
- **Manual Curation** - You control the quality

### 🔄 **Planned Features**
- Export collections
- Share boards
- Import from URLs
- Simple automation (when it works)

## 🎨 **Content Types**

- **Visual Inspiration** - Images, designs, art
- **Creative Notes** - Ideas, insights, observations
- **Reference Links** - Useful resources and examples
- **Project Collections** - Group related content

## 🛠 **Development**

This project uses:
- **Python 3.9+** for the backend
- **Vanilla HTML/CSS/JS** for the frontend
- **JSON** for simple data storage
- **aiohttp** for the web server

No complex frameworks, no over-engineering - just working code.

## 📝 **Usage**

1. **Add Images**: Drop files into `content/images/`
2. **Add Notes**: Use the dashboard or edit `content/notes/`
3. **Browse**: Use the web dashboard to explore your content
4. **Organize**: Tag and categorize as you go

## 🎼 **Why "Concierto"?**

A concierto is a musical composition where different instruments work together in harmony. This system orchestrates your creative content in the same way - bringing together visual inspiration, ideas, and references into a cohesive creative workspace.

## 🤝 **Contributing**

This is a personal project, but feedback and suggestions are welcome! Keep it simple, keep it working.

---

**Built with ❤️ for creative professionals who value quality over quantity.**