# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-agent AI system built with CrewAI for sex education in the Indian context. The system creates a culturally-sensitive chatbot that provides accurate, age-appropriate sex education content while adhering to Indian legal and cultural norms.

## Core Commands

### Development & Execution
- `crewai run` - Run the full crew execution (equivalent to running all agents and tasks)
- `crewai install` - Install and lock dependencies using UV package manager

### Python Entry Points (via pyproject.toml)
- `sex_educator` or `run_crew` - Execute the main crew workflow
- `chat` - Start the interactive command-line chatbot
- `web` - Start the web interface chatbot (recommended)
- `train <n_iterations> <filename>` - Train the crew for specified iterations
- `replay <task_id>` - Replay crew execution from a specific task
- `test <n_iterations> <model_name>` - Test crew execution with specified parameters

## Architecture

### Multi-Agent System Structure
The system follows CrewAI's decorator-based pattern with 9 specialized agents:

**Core Agents:**
- `researcher` - Data research for sex education and AI developments (uses SerperDevTool)
- `reporting_analyst` - Analysis and report generation
- `curriculum_curator` - Content validation and curation (uses SerperDevTool)
- `conversation_handler` - User interaction management
- `cultural_adapter` - Regional/cultural localization
- `legal_compliance` - Legal and regulatory compliance
- `outreach_engagement` - User engagement and accessibility
- `escalation_agent` - Crisis detection and escalation
- `feedback_analyzer` - Data analysis and improvement insights

### Configuration-Driven Design
- Agents defined in `src/sex_educator/config/agents.yaml`
- Tasks defined in `src/sex_educator/config/tasks.yaml`
- Main crew logic in `src/sex_educator/crew.py` using CrewAI decorators (@agent, @task, @crew)

### Process Flow
The system runs sequential tasks across all agents, with hooks for data manipulation:
- `@before_kickoff` - Pre-execution data preparation
- `@after_kickoff` - Post-execution result processing

## Environment Setup

- Requires Python 3.10-3.13
- Uses UV for dependency management
- Requires `GEMINI_API_KEY` in `.env` file (using Gemini API instead of OpenAI)
- Main dependency: `crewai[tools]>=0.83.0,<1.0.0`

## Key Files

- `src/sex_educator/main.py` - Entry point with run/train/replay/test/chat/web functions
- `src/sex_educator/crew.py` - Core crew definition with all agents and tasks
- `src/sex_educator/chatbot.py` - Interactive chatbot implementation with conversation memory
- `src/sex_educator/web_app.py` - Flask web application with REST API
- `src/sex_educator/templates/index.html` - Modern responsive web interface
- `src/sex_educator/static/` - CSS, JavaScript, and web assets
- `src/sex_educator/tools/SerperDevTool.py` - Web search tool integration
- `config/agents.yaml` - Agent roles, goals, and backstories
- `config/tasks.yaml` - Task descriptions and expected outputs
- `test_chatbot.py` - Command-line chatbot test script
- `test_web_app.py` - Web application test script

## Chatbot Features

The chatbot (`SexEducatorChatbot`) provides:
- **Intent Detection**: Categorizes queries (crisis, anatomy, relationships, health, consent, cultural, general)
- **Crisis Handling**: Detects distress and provides immediate support resources
- **Cultural Sensitivity**: Responses adapted for Indian context
- **Conversation Memory**: Maintains context across conversation
- **Agent Integration**: Uses specialized CrewAI agents based on query type
- **Safety Filters**: Blocks inappropriate requests while maintaining educational value

## Web Interface Features

The web interface (`web_app.py`) includes:
- **Modern UI**: Responsive design with Indian cultural theming ("Aarogya Mitram")
- **Real-time Chat**: Smooth messaging with typing indicators
- **Quick Actions**: Preset buttons for common questions
- **Privacy Focus**: Secure conversations with privacy indicators
- **Mobile-friendly**: Works on all devices
- **Crisis Support**: Emergency helpline numbers for India
- **Accessibility**: Designed for users with disabilities