# Concierto Add-Ons

This bundle contains:
- analysis/inspo_context.py : merges per-image analysis into atoms/merged.json
- compose/prompt_kitchen.py : builds prompts from JSON + atoms
- compose/templates/*.jinja.txt : prompt templates for deliverables
- render/svg_logo_scaffolder.py : turns logo directions JSON into SVGs
- ui/atoms_preview.py : quick HTML preview of atoms/merged.json

Usage overview:
1. Run inspo_context.py on analysis outputs to generate atoms/merged.json
2. Preview atoms with atoms_preview.py
3. Compose prompts per deliverable using prompt_kitchen.py and templates
4. For logos, generate directions JSON then run svg_logo_scaffolder.py
