#!/usr/bin/env python3
"""
Brand Preview Generator - Visual output system for synthesized brands
Creates professional HTML previews, PDF style guides, and Figma tokens
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List
import base64


class BrandPreviewGenerator:
    """Generates visual previews and exports for brand specifications"""
    
    def __init__(self):
        self.spacing_scale = [4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96]
        self.font_sizes = [12, 14, 16, 18, 20, 24, 32, 40, 48, 56, 64]
        
    def generate_html_preview(self, brand_spec: Dict[str, Any]) -> str:
        """Generate a complete HTML preview focused on brand positioning and story"""
        
        # Extract brand data
        colors = brand_spec.get('colors', {})
        typography = brand_spec.get('typography', {})
        personality = brand_spec.get('personality', {})
        accessibility = brand_spec.get('accessibility', {})
        brand_name = brand_spec.get('name', 'Untitled Brand')
        brief = brand_spec.get('brief', {})
        source_image_ids = brand_spec.get('source_images', [])
        
        # Get actual image paths from source_items
        source_images = []
        source_items = brand_spec.get('source_items', [])
        if source_items:
            # Use source_items if available (has full item data)
            for item in source_items:
                if item.get('path'):
                    source_images.append({
                        'path': item['path'],
                        'id': item.get('id', ''),
                        'title': item.get('title', 'Source Image'),
                        'description': item.get('description', '')
                    })
        else:
            # Fallback to just IDs if source_items not available
            source_images = source_image_ids
        
        # Generate brand positioning content
        brand_story = self._generate_brand_story(brand_spec)
        brand_archetype = self._determine_brand_archetype(personality)
        messaging_framework = self._generate_messaging_framework(brand_spec)
        
        # Generate CSS custom properties
        css_variables = self._generate_css_variables(brand_spec)
        
        # Create the complete HTML focused on brand positioning
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{brand_name} - Brand Positioning Guide</title>
    <style>
        {css_variables}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: var(--font-body);
            font-size: var(--font-size-base);
            line-height: 1.7;
            color: var(--color-text-primary);
            background: var(--color-background);
        }}
        
        /* Typography optimized for storytelling */
        h1 {{ font-family: var(--font-heading); font-size: clamp(2.5rem, 8vw, 4rem); font-weight: var(--font-weight-heading); line-height: 1.1; margin-bottom: 1.5rem; }}
        h2 {{ font-family: var(--font-heading); font-size: clamp(1.8rem, 5vw, 2.5rem); font-weight: var(--font-weight-heading); line-height: 1.2; margin: 3rem 0 1.5rem; }}
        h3 {{ font-family: var(--font-heading); font-size: clamp(1.3rem, 3vw, 1.8rem); font-weight: var(--font-weight-heading); line-height: 1.3; margin: 2rem 0 1rem; }}
        
        p {{ margin-bottom: 1.5rem; font-size: 1.1rem; }}
        .large-text {{ font-size: 1.3rem; line-height: 1.6; }}
        .quote {{ font-size: 1.5rem; font-style: italic; color: var(--color-primary); margin: 2rem 0; text-align: center; }}
        
        /* Layout focused on story flow */
        .container {{ max-width: 900px; margin: 0 auto; padding: 0 2rem; }}
        .wide-container {{ max-width: 1400px; margin: 0 auto; padding: 0 2rem; }}
        .section {{ margin: 4rem 0; }}
        .hero {{ min-height: 100vh; display: flex; align-items: center; justify-content: center; text-align: center; position: relative; }}
        
        /* Hero with brand mood */
        .hero-content {{
            background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
            color: white;
            padding: 4rem;
            border-radius: 2rem;
            max-width: 800px;
            position: relative;
            overflow: hidden;
        }}
        
        .hero-content::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"><g fill="none" fill-rule="evenodd"><g fill="%23ffffff" fill-opacity="0.1"><circle cx="10" cy="10" r="1"/></g></g></svg>');
            pointer-events: none;
        }}
        
        .hero-tagline {{
            font-size: 1.2rem;
            opacity: 0.9;
            margin-top: 1rem;
            font-weight: 300;
        }}
        
        /* Brand story sections */
        .story-section {{
            background: white;
            padding: 3rem;
            border-radius: 1rem;
            margin: 3rem 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}
        
        .archetype-section {{
            background: linear-gradient(45deg, var(--color-primary), var(--color-secondary));
            color: white;
            padding: 3rem;
            border-radius: 1rem;
            margin: 3rem 0;
            text-align: center;
        }}
        
        /* Mood board from source images */
        .mood-board {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
            padding: 1rem;
        }}
        
        .mood-board a {{
            position: relative;
            display: block;
            border-radius: 0.75rem;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            background: white;
        }}
        
        .mood-image {{
            width: 250px;
            height: 250px;
            object-fit: cover;
            display: block;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .mood-image:hover {{
            transform: translateY(-4px) scale(1.02);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}
        
        .source-dna-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin: 2rem 0;
            justify-items: center;
        }}
        
        .source-image-link {{
            text-decoration: none;
            display: block;
            transition: transform 0.2s ease;
        }}
        
        .source-image-link:hover {{
            transform: translateY(-2px);
        }}
        
        /* Personality as visual story */
        .personality-showcase {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin: 3rem 0;
        }}
        
        .personality-card {{
            background: white;
            padding: 2rem;
            border-radius: 1rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            text-align: center;
            border-top: 4px solid var(--color-primary);
        }}
        
        .personality-icon {{
            font-size: 3rem;
            margin-bottom: 1rem;
        }}
        
        /* Color story */
        .color-story {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
            margin: 2rem 0;
        }}
        
        .color-narrative {{
            text-align: center;
            padding: 2rem;
        }}
        
        .color-hero {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
            margin: 0 auto 1rem;
            box-shadow: 0 8px 30px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 0.9rem;
        }}
        
        /* Messaging framework */
        .messaging-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin: 2rem 0;
        }}
        
        .message-card {{
            background: var(--color-background-alt);
            padding: 2rem;
            border-radius: 1rem;
            border-left: 6px solid var(--color-primary);
        }}
        
        /* Applications in context */
        .application-showcase {{
            margin: 3rem 0;
        }}
        
        .application-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin: 2rem 0;
        }}
        
        .application-example {{
            background: white;
            border-radius: 1rem;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}
        
        .application-preview {{
            height: 200px;
            background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.2rem;
            font-weight: bold;
        }}
        
        .application-description {{
            padding: 1.5rem;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .hero-content {{ padding: 2rem; }}
            .story-section {{ padding: 2rem; }}
            .container {{ padding: 0 1rem; }}
        }}
    </style>
</head>
<body>
    <!-- Hero with brand essence -->
    <div class="hero">
        <div class="hero-content">
            <h1>{brand_name}</h1>
            <p class="hero-tagline">{brand_story.get('essence', 'Defining moments, creating connections')}</p>
            <p class="large-text" style="margin-top: 2rem;">"{personality.get('voice', 'We believe in authentic expression and meaningful impact.')}"</p>
        </div>
    </div>
    
    <div class="container">
        <!-- Source DNA - Show the source images prominently -->
        {self._generate_mood_board_section(source_images, brand_spec)}
        
        <!-- Brand Archetype -->
        <div class="archetype-section">
            <h2>{brand_archetype.get('name', 'The Innovator')}</h2>
            <p class="large-text">{brand_archetype.get('description', 'Driven by the desire to create meaningful change and inspire others to reach their potential.')}</p>
            <div style="margin-top: 2rem; display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
                {self._generate_archetype_traits(brand_archetype)}
            </div>
        </div>
        
        <!-- Brand Story -->
        <div class="story-section">
            <h2>Brand Story</h2>
            <p class="large-text">{brand_story.get('narrative', self._generate_brand_narrative(brand_spec))}</p>
            
            <h3>What We Believe</h3>
            <p>{brand_story.get('beliefs', self._generate_brand_beliefs(brand_spec))}</p>
            
            <h3>Our Promise</h3>
            <div class="quote">"{brand_story.get('promise', self._generate_brand_promise(brand_spec))}"</div>
        </div>
        
        <!-- Brand Insights & DNA -->
        {self._generate_insights_section(brand_spec)}
        
        <!-- Personality as Story -->
        <div class="section">
            <h2>Brand Personality</h2>
            <div class="personality-showcase">
                {self._generate_personality_story_cards(personality)}
            </div>
        </div>
        
        <!-- Color Meaning -->
        <div class="section">
            <h2>Color Psychology</h2>
            <p class="large-text">Each color in our palette tells part of our story and evokes specific emotions that align with our brand purpose.</p>
            <div class="color-story">
                {self._generate_color_meanings(colors, personality)}
            </div>
        </div>
        
        <!-- Messaging Framework -->
        <div class="section">
            <h2>How We Communicate</h2>
            <div class="messaging-grid">
                {self._generate_messaging_cards(messaging_framework)}
            </div>
        </div>
    </div>
    
    <!-- Brand Applications -->
    <div class="wide-container">
        <div class="application-showcase">
            <h2 style="text-align: center; margin-bottom: 3rem;">Brand in Action</h2>
            <div class="application-grid">
                {self._generate_application_examples(brand_spec)}
            </div>
        </div>
    </div>
    
    <div style="background: var(--color-background-alt); padding: 4rem 0; margin-top: 4rem; text-align: center;">
        <div class="container">
            <p style="color: var(--color-text-secondary); font-size: 0.9rem;">
                Generated on {datetime.now().strftime('%B %d, %Y')} • {brand_name} Brand Positioning Guide
            </p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_css_variables(self, brand_spec: Dict[str, Any]) -> str:
        """Generate CSS custom properties from brand specification"""
        colors = brand_spec.get('colors', {})
        typography = brand_spec.get('typography', {})
        
        # Convert colors to CSS variables
        css_vars = [":root {"]
        
        # Color variables
        for name, color in colors.items():
            var_name = name.lower().replace(' ', '-').replace('_', '-')
            css_vars.append(f"  --color-{var_name}: {color};")
            
            # Add RGB values for opacity usage
            if color.startswith('#'):
                try:
                    rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                    css_vars.append(f"  --color-{var_name}-rgb: {rgb[0]}, {rgb[1]}, {rgb[2]};")
                except:
                    pass
        
        # Default color mappings
        primary_color = list(colors.values())[0] if colors else '#667eea'
        secondary_color = list(colors.values())[1] if len(colors) > 1 else '#764ba2'
        
        css_vars.extend([
            f"  --color-primary: {primary_color};",
            f"  --color-secondary: {secondary_color};",
            "  --color-primary-dark: color-mix(in srgb, var(--color-primary) 80%, black);",
            "  --color-secondary-dark: color-mix(in srgb, var(--color-secondary) 80%, black);",
            "  --color-background: #ffffff;",
            "  --color-background-alt: #f8f9fa;",
            "  --color-text-primary: #2c3e50;",
            "  --color-text-secondary: #6c757d;",
            "  --color-border: #e9ecef;",
        ])
        
        # Typography variables
        heading_font = typography.get('heading', {}).get('family', '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif')
        body_font = typography.get('body', {}).get('family', '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif')
        
        css_vars.extend([
            f"  --font-heading: {heading_font};",
            f"  --font-body: {body_font};",
            f"  --font-weight-heading: {typography.get('heading', {}).get('weight', 600)};",
            f"  --font-weight-body: {typography.get('body', {}).get('weight', 400)};",
            "  --font-weight-bold: 600;",
        ])
        
        # Font size scale
        font_sizes = {
            'xs': '12px',
            'sm': '14px',
            'base': '16px',
            'lg': '18px',
            'xl': '20px',
            'h4': '20px',
            'h3': '24px',
            'h2': '32px',
            'h1': '40px',
            'hero': '48px'
        }
        
        for size_name, size_value in font_sizes.items():
            css_vars.append(f"  --font-size-{size_name}: {size_value};")
        
        # Line heights
        css_vars.extend([
            "  --line-height-base: 1.6;",
            "  --line-height-heading: 1.2;",
        ])
        
        # Spacing scale (8px grid)
        spacing_scale = {
            'xs': '4px',
            'sm': '8px',
            'md': '16px',
            'lg': '24px',
            'xl': '32px',
            'xxl': '48px'
        }
        
        for space_name, space_value in spacing_scale.items():
            css_vars.append(f"  --space-{space_name}: {space_value};")
        
        # Border radius
        css_vars.extend([
            "  --border-radius: 8px;",
            "  --border-radius-sm: 4px;",
            "  --border-radius-lg: 12px;",
        ])
        
        css_vars.append("}")
        
        return "\n".join(css_vars)
    
    def _generate_color_swatches(self, colors: Dict[str, str]) -> str:
        """Generate HTML for color swatches"""
        if not colors:
            return "<p>No colors defined</p>"
        
        swatches = []
        for name, color in colors.items():
            clean_name = name.replace('_', ' ').title()
            swatches.append(f"""
                <div class="color-swatch">
                    <div class="color-circle" style="background-color: {color};"></div>
                    <div class="color-name">{clean_name}</div>
                    <div class="color-hex">{color.upper()}</div>
                </div>
            """)
        
        return "".join(swatches)
    
    def _generate_personality_cards(self, personality: Dict[str, Any]) -> str:
        """Generate HTML for personality trait cards"""
        traits = personality.get('traits', ['Professional', 'Modern', 'Reliable'])
        
        cards = []
        for i, trait in enumerate(traits[:6]):  # Limit to 6 traits
            primary_class = 'primary' if i < 2 else ''
            cards.append(f"""
                <div class="trait-card {primary_class}">
                    <strong>{trait}</strong>
                </div>
            """)
        
        return "".join(cards)
    
    def _generate_spacing_blocks(self) -> str:
        """Generate HTML for spacing demonstration"""
        blocks = []
        for size in [4, 8, 16, 24, 32, 48]:
            blocks.append(f"""
                <div class="spacing-block" style="height: {size}px; width: {size * 4}px;">
                    {size}px
                </div>
            """)
        
        return "".join(blocks)
    
    def generate_figma_tokens(self, brand_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Figma Tokens plugin compatible JSON"""
        colors = brand_spec.get('colors', {})
        typography = brand_spec.get('typography', {})
        
        tokens = {
            "global": {
                "colors": {
                    "brand": {}
                },
                "typography": {
                    "fontFamilies": {},
                    "fontWeights": {},
                    "fontSize": {}
                },
                "spacing": {}
            }
        }
        
        # Color tokens
        for name, color in colors.items():
            clean_name = name.lower().replace(' ', '-').replace('_', '-')
            tokens["global"]["colors"]["brand"][clean_name] = {
                "value": color,
                "type": "color"
            }
        
        # Typography tokens
        if typography.get('heading', {}).get('family'):
            tokens["global"]["typography"]["fontFamilies"]["heading"] = {
                "value": typography['heading']['family'],
                "type": "fontFamilies"
            }
        
        if typography.get('body', {}).get('family'):
            tokens["global"]["typography"]["fontFamilies"]["body"] = {
                "value": typography['body']['family'],
                "type": "fontFamilies"
            }
        
        # Font weights
        for weight_name, weight_value in [("regular", "400"), ("medium", "500"), ("semibold", "600"), ("bold", "700")]:
            tokens["global"]["typography"]["fontWeights"][weight_name] = {
                "value": weight_value,
                "type": "fontWeights"
            }
        
        # Font sizes
        font_sizes = {
            "xs": "12",
            "sm": "14", 
            "base": "16",
            "lg": "18",
            "xl": "20",
            "2xl": "24",
            "3xl": "32",
            "4xl": "40",
            "5xl": "48"
        }
        
        for size_name, size_value in font_sizes.items():
            tokens["global"]["typography"]["fontSize"][size_name] = {
                "value": size_value,
                "type": "fontSize"
            }
        
        # Spacing tokens
        spacing_values = {
            "xs": "4",
            "sm": "8", 
            "md": "16",
            "lg": "24",
            "xl": "32",
            "2xl": "48",
            "3xl": "64"
        }
        
        for space_name, space_value in spacing_values.items():
            tokens["global"]["spacing"][space_name] = {
                "value": space_value,
                "type": "spacing"
            }
        
        return tokens
    
    def generate_style_guide_pdf_html(self, brand_spec: Dict[str, Any]) -> str:
        """Generate HTML optimized for PDF generation"""
        brand_name = brand_spec.get('name', 'Untitled Brand')
        colors = brand_spec.get('colors', {})
        typography = brand_spec.get('typography', {})
        personality = brand_spec.get('personality', {})
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{brand_name} Style Guide</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #2c3e50;
        }}
        
        .page {{
            page-break-after: always;
            min-height: 250mm;
        }}
        
        .page:last-child {{
            page-break-after: avoid;
        }}
        
        h1 {{ font-size: 32px; margin-bottom: 20px; color: {list(colors.values())[0] if colors else '#667eea'}; }}
        h2 {{ font-size: 24px; margin: 30px 0 15px; color: #2c3e50; }}
        h3 {{ font-size: 18px; margin: 20px 0 10px; }}
        
        .cover {{
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
        }}
        
        .color-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin: 20px 0;
        }}
        
        .color-item {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .color-square {{
            width: 60px;
            height: 60px;
            margin-right: 20px;
            border: 1px solid #ddd;
        }}
        
        .color-info h4 {{
            margin: 0;
            font-size: 16px;
        }}
        
        .color-info p {{
            margin: 5px 0;
            color: #666;
            font-family: 'Monaco', monospace;
        }}
        
        .trait-list {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin: 20px 0;
        }}
        
        .trait-item {{
            padding: 10px;
            background: #f8f9fa;
            border-left: 4px solid {list(colors.values())[0] if colors else '#667eea'};
        }}
        
        .component-example {{
            margin: 20px 0;
            padding: 20px;
            border: 1px solid #ddd;
            background: #f8f9fa;
        }}
    </style>
</head>
<body>
    <!-- Cover Page -->
    <div class="page cover">
        <h1 style="font-size: 48px; margin-bottom: 30px;">{brand_name}</h1>
        <p style="font-size: 18px; color: #666; margin-bottom: 40px;">Brand Style Guide</p>
        <p style="color: #999;">Generated on {datetime.now().strftime('%B %d, %Y')}</p>
    </div>
    
    <!-- Colors Page -->
    <div class="page">
        <h1>Color Palette</h1>
        <p>This color system ensures consistency and accessibility across all brand touchpoints.</p>
        
        <div style="margin-top: 30px;">
            {self._generate_pdf_colors(colors)}
        </div>
        
        <h2>Usage Guidelines</h2>
        <ul style="margin-left: 20px;">
            <li>Primary colors should dominate the visual hierarchy</li>
            <li>Use secondary colors for accents and highlights</li>
            <li>Ensure sufficient contrast for text readability</li>
            <li>Test colors in both digital and print applications</li>
        </ul>
    </div>
    
    <!-- Typography Page -->
    <div class="page">
        <h1>Typography</h1>
        
        <h2>Font Families</h2>
        <div style="margin: 20px 0;">
            <h3>Heading Font</h3>
            <p style="font-size: 24px; font-weight: bold; margin: 10px 0;">{typography.get('heading', {}).get('family', 'System Default')}</p>
            <p>Weight: {typography.get('heading', {}).get('weight', '600')}</p>
            
            <h3 style="margin-top: 30px;">Body Font</h3>
            <p style="font-size: 16px; margin: 10px 0;">{typography.get('body', {}).get('family', 'System Default')}</p>
            <p>Weight: {typography.get('body', {}).get('weight', '400')}</p>
        </div>
        
        <h2>Type Scale</h2>
        <div style="margin: 20px 0;">
            <div style="margin: 15px 0;"><span style="font-size: 32px; font-weight: bold;">H1 - 32px</span> <span style="color: #666;">Main headings</span></div>
            <div style="margin: 15px 0;"><span style="font-size: 24px; font-weight: bold;">H2 - 24px</span> <span style="color: #666;">Section titles</span></div>
            <div style="margin: 15px 0;"><span style="font-size: 18px; font-weight: bold;">H3 - 18px</span> <span style="color: #666;">Subsections</span></div>
            <div style="margin: 15px 0;"><span style="font-size: 16px;">Body - 16px</span> <span style="color: #666;">Paragraph text</span></div>
            <div style="margin: 15px 0;"><span style="font-size: 14px;">Small - 14px</span> <span style="color: #666;">Captions, labels</span></div>
        </div>
    </div>
    
    <!-- Components Page -->
    <div class="page">
        <h1>Components</h1>
        
        <h2>Buttons</h2>
        <div class="component-example">
            <div style="margin: 10px 0;">
                <span style="background: {list(colors.values())[0] if colors else '#667eea'}; color: white; padding: 8px 16px; border-radius: 4px; margin-right: 10px;">Primary Button</span>
                <span style="border: 2px solid {list(colors.values())[0] if colors else '#667eea'}; color: {list(colors.values())[0] if colors else '#667eea'}; padding: 6px 14px; border-radius: 4px;">Outline Button</span>
            </div>
        </div>
        
        <h2>Cards</h2>
        <div class="component-example">
            <div style="border: 1px solid #ddd; padding: 20px; border-radius: 8px; background: white;">
                <h3 style="color: {list(colors.values())[0] if colors else '#667eea'};">Card Title</h3>
                <p>This is an example of how cards should be styled with consistent spacing and typography.</p>
            </div>
        </div>
        
        <h2>Forms</h2>
        <div class="component-example">
            <div style="margin: 10px 0;">
                <label style="display: block; font-weight: bold; margin-bottom: 5px;">Label</label>
                <div style="border: 1px solid #ddd; padding: 8px; border-radius: 4px; background: white;">Input field example</div>
            </div>
        </div>
    </div>
    
    <!-- Guidelines Page -->
    <div class="page">
        <h1>Brand Guidelines</h1>
        
        <h2>Personality Traits</h2>
        <div class="trait-list">
            {self._generate_pdf_traits(personality)}
        </div>
        
        <h2>Voice & Tone</h2>
        <div style="background: linear-gradient(135deg, {list(colors.values())[0] if colors else '#667eea'}20, transparent); 
                    padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p style="font-size: 20px; line-height: 1.6; font-style: italic; color: #333; margin: 0;">
                "{personality.get('voice', 'Authentic and engaging, true to our values')}"
            </p>
        </div>
        
        <h2>Implementation Guidelines</h2>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 20px;">
            <div>
                <h3 style="color: #28a745;">✓ Do</h3>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    {self._generate_pdf_dos(personality)}
                </ul>
            </div>
            <div>
                <h3 style="color: #dc3545;">✗ Don't</h3>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    {self._generate_pdf_donts(personality)}
                </ul>
            </div>
        </div>
        
        <h2>Living the Brand</h2>
        <p style="margin-top: 20px; line-height: 1.6;">
            This brand guide is a living document that evolves with your organization. 
            Every interaction is an opportunity to reinforce these values and create meaningful connections.
        </p>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_pdf_colors(self, colors: Dict[str, str]) -> str:
        """Generate PDF-optimized color display"""
        if not colors:
            return "<p>No colors defined</p>"
        
        items = []
        for name, color in colors.items():
            clean_name = name.replace('_', ' ').title()
            items.append(f"""
                <div class="color-item">
                    <div class="color-square" style="background-color: {color};"></div>
                    <div class="color-info">
                        <h4>{clean_name}</h4>
                        <p>{color.upper()}</p>
                    </div>
                </div>
            """)
        
        return "".join(items)
    
    def _generate_pdf_traits(self, personality: Dict[str, Any]) -> str:
        """Generate PDF-optimized personality traits"""
        traits = personality.get('traits', ['Professional', 'Modern', 'Reliable'])
        
        items = []
        for trait in traits[:8]:  # Limit for PDF layout
            items.append(f'<div class="trait-item"><strong>{trait.capitalize()}</strong></div>')
        
        return "".join(items)
    
    def _generate_pdf_dos(self, personality: Dict[str, Any]) -> str:
        """Generate PDF-optimized do's list"""
        dos = personality.get('do', [])
        if not dos:
            # Fallback to generic do's if none provided
            dos = [
                "Maintain consistency across all touchpoints",
                "Use the defined color palette",
                "Follow typography guidelines"
            ]
        
        items = []
        for do in dos[:5]:  # Limit to 5 for PDF layout
            items.append(f'<li>{do}</li>')
        
        return "".join(items)
    
    def _generate_pdf_donts(self, personality: Dict[str, Any]) -> str:
        """Generate PDF-optimized don'ts list"""
        donts = personality.get('dont', [])
        if not donts:
            # Fallback to generic don'ts if none provided
            donts = [
                "Don't alter the color palette",
                "Avoid inconsistent messaging",
                "Never compromise brand values"
            ]
        
        items = []
        for dont in donts[:5]:  # Limit to 5 for PDF layout
            items.append(f'<li>{dont}</li>')
        
        return "".join(items)

    def _generate_brand_story(self, brand_spec: Dict[str, Any]) -> Dict[str, str]:
        """Generate brand story elements based on personality and brief"""
        personality = brand_spec.get('personality', {})
        brief = brand_spec.get('brief', {})
        traits = personality.get('traits', [])
        
        # Generate story based on personality traits
        if 'innovative' in [t.lower() for t in traits]:
            essence = "Pioneering new possibilities, one breakthrough at a time"
        elif 'authentic' in [t.lower() for t in traits]:
            essence = "Genuine connections through honest expression"
        elif 'bold' in [t.lower() for t in traits]:
            essence = "Fearless vision, transformative impact"
        else:
            essence = "Creating meaningful experiences that inspire"
            
        return {
            'essence': essence,
            'narrative': self._generate_brand_narrative(brand_spec),
            'beliefs': self._generate_brand_beliefs(brand_spec),
            'promise': self._generate_brand_promise(brand_spec)
        }
    
    def _generate_brand_narrative(self, brand_spec: Dict[str, Any]) -> str:
        """Generate brand narrative based on personality and context"""
        personality = brand_spec.get('personality', {})
        brief = brand_spec.get('brief', {})
        traits = personality.get('traits', [])
        category = brief.get('category', 'Brand')
        
        # Create narrative based on traits
        primary_traits = traits[:3] if traits else ['innovative', 'authentic', 'impactful']
        
        narratives = {
            'innovative': f"In a world that moves fast, {brand_spec.get('name', 'we')} moves faster. Born from the belief that innovation isn't just about technology—it's about reimagining what's possible when creativity meets purpose.",
            'authentic': f"Real stories deserve real voices. {brand_spec.get('name', 'We')} exists to amplify authenticity in a world of facades, creating spaces where genuine expression flourishes.",
            'bold': f"Some see obstacles. We see opportunities. {brand_spec.get('name', 'Our story')} is written by those brave enough to challenge conventions and create the change they want to see.",
            'creative': f"Creativity isn't just what we do—it's who we are. {brand_spec.get('name', 'We')} believe that inspired thinking can transform not just brands, but entire communities.",
            'professional': f"Excellence isn't an act, it's a habit. {brand_spec.get('name', 'Our foundation')} is built on the principle that professional mastery and human connection go hand in hand."
        }
        
        # Select narrative based on primary trait
        primary_trait = primary_traits[0].lower() if primary_traits else 'innovative'
        for trait_key in narratives.keys():
            if trait_key in primary_trait:
                return narratives[trait_key]
        
        return narratives['innovative']
    
    def _generate_brand_beliefs(self, brand_spec: Dict[str, Any]) -> str:
        """Generate brand beliefs statement"""
        personality = brand_spec.get('personality', {})
        traits = [t.lower() for t in personality.get('traits', [])]
        
        beliefs = []
        if any(trait in traits for trait in ['authentic', 'honest', 'genuine']):
            beliefs.append("Authenticity creates deeper connections than perfection")
        if any(trait in traits for trait in ['innovative', 'creative', 'forward']):
            beliefs.append("Innovation flourishes when diverse perspectives collide")
        if any(trait in traits for trait in ['bold', 'confident', 'strong']):
            beliefs.append("Bold action creates lasting change")
        if any(trait in traits for trait in ['collaborative', 'community', 'together']):
            beliefs.append("Great things happen when we lift each other up")
        
        if not beliefs:
            beliefs = ["Quality and integrity should never be compromised", "Every interaction is an opportunity to create value"]
        
        return ". ".join(beliefs) + "."
    
    def _generate_brand_promise(self, brand_spec: Dict[str, Any]) -> str:
        """Generate brand promise statement"""
        personality = brand_spec.get('personality', {})
        brief = brand_spec.get('brief', {})
        traits = [t.lower() for t in personality.get('traits', [])]
        category = brief.get('category', '')
        
        if 'technology' in category.lower():
            return "We'll never stop pushing boundaries to make technology more human"
        elif 'creative' in category.lower():
            return "Your story deserves to be told with authenticity and impact"
        elif 'consulting' in category.lower():
            return "We're not just advisors—we're partners in your success"
        elif any(trait in traits for trait in ['premium', 'luxury', 'sophisticated']):
            return "Excellence isn't just our standard—it's our starting point"
        else:
            return "We'll always choose substance over style, and results over recognition"
    
    def _determine_brand_archetype(self, personality: Dict[str, Any]) -> Dict[str, str]:
        """Determine brand archetype based on personality traits"""
        traits = [t.lower() for t in personality.get('traits', [])]
        
        archetypes = {
            'innovator': {
                'name': 'The Innovator',
                'description': 'Driven by the desire to create meaningful change and inspire others to reach their potential.',
                'keywords': ['innovative', 'creative', 'forward-thinking', 'pioneering']
            },
            'sage': {
                'name': 'The Sage',
                'description': 'Motivated by the desire to understand the world and share wisdom with others.',
                'keywords': ['wise', 'knowledgeable', 'thoughtful', 'analytical', 'professional']
            },
            'hero': {
                'name': 'The Hero',
                'description': 'Determined to prove worth through courageous action and making a positive difference.',
                'keywords': ['bold', 'confident', 'strong', 'determined', 'brave']
            },
            'creator': {
                'name': 'The Creator',
                'description': 'Yearns to create something of enduring value and express a unique vision.',
                'keywords': ['creative', 'artistic', 'expressive', 'imaginative', 'original']
            },
            'caregiver': {
                'name': 'The Caregiver',
                'description': 'Motivated by compassion and generosity to help others and create a better world.',
                'keywords': ['caring', 'nurturing', 'supportive', 'helpful', 'compassionate']
            },
            'explorer': {
                'name': 'The Explorer',
                'description': 'Driven by a deep desire for freedom and finding new experiences.',
                'keywords': ['adventurous', 'free', 'independent', 'authentic', 'spontaneous']
            }
        }
        
        # Score each archetype based on trait matches
        scores = {}
        for archetype_key, archetype_data in archetypes.items():
            score = 0
            for keyword in archetype_data['keywords']:
                if any(keyword in trait for trait in traits):
                    score += 1
            scores[archetype_key] = score
        
        # Return highest scoring archetype
        best_archetype = max(scores.items(), key=lambda x: x[1])[0]
        return archetypes[best_archetype]
    
    def _generate_messaging_framework(self, brand_spec: Dict[str, Any]) -> Dict[str, str]:
        """Generate messaging framework"""
        personality = brand_spec.get('personality', {})
        brief = brand_spec.get('brief', {})
        traits = personality.get('traits', [])
        
        return {
            'core_message': f"We believe in {traits[0].lower() if traits else 'meaningful'} solutions that create lasting impact.",
            'value_proposition': f"Through {', '.join(traits[:2]).lower() if len(traits) >= 2 else 'innovative thinking'}, we deliver results that matter.",
            'brand_pillars': traits[:3] if len(traits) >= 3 else ['Quality', 'Innovation', 'Impact'],
            'tone_guidelines': personality.get('voice', 'Professional yet approachable, confident without being arrogant')
        }
    
    def _generate_archetype_traits(self, archetype: Dict[str, str]) -> str:
        """Generate archetype trait badges"""
        keywords = archetype.get('keywords', ['innovative', 'creative', 'impactful'])
        
        badges = []
        for keyword in keywords[:4]:  # Limit to 4 for visual balance
            badges.append(f"""
                <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 2rem; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;">
                    {keyword}
                </span>
            """)
        
        return "".join(badges)
    
    def _generate_insights_section(self, brand_spec: Dict[str, Any]) -> str:
        """Generate section displaying synthesized insights from source materials"""
        insights = brand_spec.get('synthesized_insights', {})
        
        if not insights:
            return ""
        
        # Extract insights data
        keywords = insights.get('keywords', [])
        color_meanings = insights.get('color_meanings', [])
        visual_tone = insights.get('visual_tone', {})
        creative_insights = insights.get('creative_insights', [])
        
        # Build keywords display
        keyword_badges = []
        for kw in keywords[:8]:  # Limit to 8 keywords
            keyword_badges.append(f'<span class="trait-badge">{kw}</span>')
        
        # Build visual tone description
        tone_desc = []
        if visual_tone.get('brightness'):
            tone_desc.append(visual_tone['brightness'])
        if visual_tone.get('contrast'):
            tone_desc.append(visual_tone['contrast'])
        if visual_tone.get('saturation'):
            tone_desc.append(visual_tone['saturation'])
        
        # Build creative insights summary
        insights_html = ""
        if creative_insights:
            # Combine and summarize creative insights
            combined_insights = ' '.join(creative_insights[:3])  # Use first 3 insights
            if len(combined_insights) > 300:
                combined_insights = combined_insights[:297] + "..."
            insights_html = f"""
                <div style="background: linear-gradient(135deg, var(--color-primary)10, transparent); 
                           padding: 1.5rem; border-radius: 1rem; margin-top: 1.5rem;">
                    <h4 style="color: var(--color-primary); margin-bottom: 0.5rem;">Creative DNA Analysis</h4>
                    <p style="font-style: italic; line-height: 1.7;">{combined_insights}</p>
                </div>
            """
        
        return f"""
            <div class="section">
                <h2>Brand DNA Synthesis</h2>
                <p class="large-text">
                    Extracted from the semantic analysis of our source inspiration, these elements form the core of our brand identity.
                </p>
                
                <!-- Keywords from source materials -->
                {f'''
                <div style="margin: 2rem 0;">
                    <h3>Core Themes</h3>
                    <div class="trait-badges" style="display: flex; flex-wrap: wrap; gap: 0.75rem;">
                        {"".join(keyword_badges)}
                    </div>
                </div>
                ''' if keywords else ''}
                
                <!-- Visual characteristics -->
                {f'''
                <div style="margin: 2rem 0;">
                    <h3>Visual Character</h3>
                    <p style="font-size: 1.2rem; color: var(--color-primary);">
                        A {' and '.join(tone_desc)} aesthetic that {
                            'energizes and inspires' if visual_tone.get('brightness') == 'bright' else
                            'creates depth and sophistication' if visual_tone.get('brightness') == 'dark' else
                            'balances accessibility with impact'
                        }.
                    </p>
                </div>
                ''' if tone_desc else ''}
                
                <!-- Color meanings -->
                {f'''
                <div style="margin: 2rem 0;">
                    <h3>Emotional Palette</h3>
                    <p>Our colors evoke feelings of <strong>{', '.join(color_meanings).lower()}</strong>, 
                       creating an emotional landscape that resonates with our audience.</p>
                </div>
                ''' if color_meanings else ''}
                
                <!-- Creative insights -->
                {insights_html}
            </div>
        """
    
    def _generate_mood_board_section(self, source_images: List, brand_spec: Dict[str, Any]) -> str:
        """Generate mood board section from source images"""
        if not source_images:
            return f"""
                <div class="section">
                    <h2>Source Inspiration</h2>
                    <div class="story-section">
                        <p class="large-text">Our visual language draws from the intersection of {', '.join(brand_spec.get('personality', {}).get('traits', ['modern', 'authentic'])[:2]).lower()}, creating a distinctive aesthetic that reflects our core values.</p>
                    </div>
                </div>
            """
        
        # Generate mood board with actual source images
        mood_images = []
        for img_data in source_images[:6]:  # Limit to 6 images
            if isinstance(img_data, dict):
                # New format with full data
                path = img_data.get('path', '')
                title = img_data.get('title', 'Source Image')
                img_id = img_data.get('id', '')
                description = img_data.get('description', '')
                
                # Make images clickable to go back to the main dashboard with that image highlighted
                # Truncate description for tooltip
                tooltip_description = description[:120] + "..." if len(description) > 120 else description
                mood_images.append(f'''
                    <a href="/#item-{img_id}" 
                       class="source-image-link"
                       title="{title}: {tooltip_description}">
                        <img src="/{path}" 
                             alt="{title}" 
                             class="mood-image">
                    </a>
                ''')
            else:
                # Old format with just IDs - fallback
                mood_images.append(f'<img src="/content/images/{img_data}" alt="Brand inspiration" class="mood-image">')
        
        return f"""
            <div class="section">
                <h2>Source DNA</h2>
                <p class="large-text">These are the original images that were synthesized to create this brand identity. Click any image to view its full analysis.</p>
                <div class="source-dna-grid">
                    {"".join(mood_images)}
                </div>
            </div>
        """
    
    def _generate_personality_story_cards(self, personality: Dict[str, Any]) -> str:
        """Generate personality cards with storytelling focus"""
        traits = personality.get('traits', ['Innovative', 'Authentic', 'Impactful'])
        
        # Map traits to icons and descriptions
        trait_map = {
            'innovative': {'icon': '🚀', 'description': 'We push boundaries and challenge conventions to create breakthrough solutions.'},
            'authentic': {'icon': '💎', 'description': 'Genuine connection and honest communication are at our core.'},
            'bold': {'icon': '⚡', 'description': 'We take calculated risks to drive meaningful change.'},
            'creative': {'icon': '🎨', 'description': 'Imagination and artistic vision guide everything we create.'},
            'professional': {'icon': '🎯', 'description': 'Excellence and reliability define our approach to every project.'},
            'collaborative': {'icon': '🤝', 'description': 'Great work happens when diverse minds come together.'},
            'sophisticated': {'icon': '✨', 'description': 'Refined elegance meets purposeful design in all we do.'},
            'modern': {'icon': '📱', 'description': 'We embrace contemporary solutions while respecting timeless principles.'},
        }
        
        cards = []
        for trait in traits[:4]:  # Limit to 4 cards
            trait_key = trait.lower()
            trait_data = trait_map.get(trait_key, {'icon': '⭐', 'description': f'{trait} approach guides our decision-making process.'})
            
            cards.append(f"""
                <div class="personality-card">
                    <div class="personality-icon">{trait_data['icon']}</div>
                    <h3>{trait}</h3>
                    <p>{trait_data['description']}</p>
                </div>
            """)
        
        return "".join(cards)
    
    def _generate_color_meanings(self, colors: Dict[str, str], personality: Dict[str, Any]) -> str:
        """Generate color psychology explanations"""
        if not colors:
            return "<p>Color meanings will be generated based on the final palette.</p>"
        
        # Color psychology mapping
        color_psychology = {
            'red': {'emotion': 'Passion & Energy', 'meaning': 'Drives action and creates urgency'},
            'blue': {'emotion': 'Trust & Stability', 'meaning': 'Builds confidence and reliability'},
            'green': {'emotion': 'Growth & Harmony', 'meaning': 'Represents progress and balance'},
            'purple': {'emotion': 'Creativity & Luxury', 'meaning': 'Inspires innovation and sophistication'},
            'orange': {'emotion': 'Optimism & Warmth', 'meaning': 'Encourages enthusiasm and approachability'},
            'yellow': {'emotion': 'Joy & Intelligence', 'meaning': 'Stimulates creativity and positivity'},
            'pink': {'emotion': 'Compassion & Care', 'meaning': 'Evokes nurturing and understanding'},
            'black': {'emotion': 'Sophistication & Power', 'meaning': 'Conveys elegance and authority'},
            'white': {'emotion': 'Purity & Simplicity', 'meaning': 'Creates clarity and spaciousness'},
            'gray': {'emotion': 'Balance & Neutrality', 'meaning': 'Provides stability and timelessness'}
        }
        
        color_meanings = []
        for name, hex_color in list(colors.items())[:4]:  # Limit to 4 colors
            # Determine dominant color from hex
            dominant_color = self._get_dominant_color_name(hex_color)
            psychology = color_psychology.get(dominant_color, {'emotion': 'Distinctive Character', 'meaning': 'Represents our unique brand essence'})
            
            clean_name = name.replace('_', ' ').title()
            color_meanings.append(f"""
                <div class="color-narrative">
                    <div class="color-hero" style="background: {hex_color};">
                        {clean_name}
                    </div>
                    <h4>{psychology['emotion']}</h4>
                    <p>{psychology['meaning']}</p>
                </div>
            """)
        
        return "".join(color_meanings)
    
    def _get_dominant_color_name(self, hex_color: str) -> str:
        """Determine dominant color name from hex value"""
        if not hex_color.startswith('#'):
            return 'gray'
        
        try:
            # Convert hex to RGB
            hex_color = hex_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Simple color classification
            if r > g and r > b:
                if r > 150 and g < 100 and b < 100:
                    return 'red'
                elif r > 200 and g > 150 and b > 150:
                    return 'pink'
            elif g > r and g > b:
                return 'green'
            elif b > r and b > g:
                if r > 100 and b > 150:
                    return 'purple'
                else:
                    return 'blue'
            elif r > 150 and g > 100 and b < 100:
                return 'orange'
            elif r > 200 and g > 200 and b < 100:
                return 'yellow'
            elif r < 50 and g < 50 and b < 50:
                return 'black'
            elif r > 200 and g > 200 and b > 200:
                return 'white'
            else:
                return 'gray'
        except:
            return 'gray'
    
    def _generate_messaging_cards(self, messaging: Dict[str, str]) -> str:
        """Generate messaging framework cards"""
        cards = []
        
        framework_items = [
            ('Core Message', messaging.get('core_message', 'Our purpose-driven approach creates lasting value.')),
            ('Value Proposition', messaging.get('value_proposition', 'We deliver exceptional results through innovative thinking.')),
            ('Brand Pillars', ', '.join(messaging.get('brand_pillars', ['Quality', 'Innovation', 'Impact']))),
            ('Tone & Voice', messaging.get('tone_guidelines', 'Professional yet approachable, confident without being arrogant'))
        ]
        
        for title, content in framework_items:
            cards.append(f"""
                <div class="message-card">
                    <h3>{title}</h3>
                    <p>{content}</p>
                </div>
            """)
        
        return "".join(cards)
    
    def _generate_application_examples(self, brand_spec: Dict[str, Any]) -> str:
        """Generate brand application examples"""
        brand_name = brand_spec.get('name', 'Brand')
        brief = brand_spec.get('brief', {})
        category = brief.get('category', 'Brand')
        
        applications = []
        
        # Generate contextual applications based on category
        if 'technology' in category.lower():
            app_examples = [
                ('Website Hero', f'{brand_name} App Dashboard'),
                ('Mobile Interface', f'{brand_name} Mobile Experience'),
                ('Product Packaging', f'{brand_name} Tech Products')
            ]
        elif 'creative' in category.lower():
            app_examples = [
                ('Portfolio Website', f'{brand_name} Creative Work'),
                ('Business Cards', f'{brand_name} Identity System'),
                ('Project Presentation', f'{brand_name} Client Deck')
            ]
        else:
            app_examples = [
                ('Website Header', f'{brand_name} Digital Presence'),
                ('Marketing Materials', f'{brand_name} Brand Assets'),
                ('Social Media', f'{brand_name} Content Strategy')
            ]
        
        for app_type, app_name in app_examples:
            applications.append(f"""
                <div class="application-example">
                    <div class="application-preview">
                        {app_name}
                    </div>
                    <div class="application-description">
                        <h4>{app_type}</h4>
                        <p>Demonstrates how the brand system translates to {app_type.lower()} with consistent visual language and messaging.</p>
                    </div>
                </div>
            """)
        
        return "".join(applications)


# Try to import PDF generation library
try:
    import weasyprint
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ WeasyPrint not available - PDF generation disabled")


def generate_pdf_from_html(html_content: str) -> bytes:
    """Generate PDF from HTML content using WeasyPrint"""
    if not PDF_AVAILABLE:
        raise ImportError("WeasyPrint is required for PDF generation")
    
    return weasyprint.HTML(string=html_content).write_pdf()