# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Concierto is a comprehensive AI agent orchestration system designed for managing design, marketing, innovation, and brand consulting projects. It contains 38 specialized sub-agents organized across 8 departments that work together to accelerate rapid development and creative processes.

## Common Development Tasks

### Installing Agents
```bash
# Copy agents to Claude Code directory
cp -r agents/* ~/.claude/agents/

# Restart Claude Code to load new agents
```

### Using Agents
- Agents activate automatically based on task context
- Can explicitly request agents by name
- Multiple agents can collaborate on complex tasks

## Project Structure

```
Concierto/
├── agents/                    # All specialized sub-agents
│   ├── design/               # Brand, UI/UX, visual storytelling (5 agents)
│   ├── engineering/          # Development and architecture (7 agents)
│   ├── marketing/            # Growth and platform-specific (7 agents)
│   ├── product/              # Strategy and research (3 agents)
│   ├── project-management/   # Coordination and shipping (3 agents)
│   ├── studio-operations/    # Business operations (5 agents)
│   ├── testing/              # Quality and performance (5 agents)
│   ├── bonus/                # Special purpose (2 agents)
│   └── README.md             # Comprehensive documentation
└── CLAUDE.md                 # This file
```

## Key Commands

### Agent Management
- Review available agents: Check `agents/README.md`
- Install agents: Copy to `~/.claude/agents/`
- Test agent activation: Describe tasks matching agent expertise

### Development Workflow
- Agents follow 6-day sprint methodology
- Proactive agents trigger automatically in specific contexts
- Agents have specific tool access (Write, Read, MultiEdit, Bash, etc.)

## Architecture Notes

### Agent Structure
Each agent includes:
- **YAML frontmatter**: Name, description with examples, color, tools
- **System prompt**: Detailed expertise and instructions (500+ words)
- **Specific responsibilities**: 5-8 primary duties per agent
- **Integration patterns**: How agents work within 6-day sprints

### Key Design Principles
1. **Specialization**: Each agent is an expert in their specific domain
2. **Collaboration**: Agents work together on complex multi-faceted projects
3. **Speed**: Optimized for rapid development and iteration
4. **Quality**: Maintains high standards while moving fast
5. **Proactivity**: Some agents trigger automatically when appropriate

### Agent Categories
- **Engineering**: Technical implementation and architecture
- **Design**: Visual and user experience
- **Marketing**: Growth and user acquisition
- **Product**: Strategy and user research
- **Project Management**: Coordination and delivery
- **Studio Operations**: Business and infrastructure
- **Testing**: Quality assurance and optimization
- **Bonus**: Special purpose agents for morale and coaching

### Proactive Agents
These agents activate automatically:
- `studio-coach`: Complex multi-agent tasks
- `test-writer-fixer`: After code implementation
- `whimsy-injector`: After UI/UX changes
- `experiment-tracker`: When feature flags are added