# 🌸 Aarogya Mitram - Sex Education Chatbot

<div align="center">

**A culturally-sensitive, AI-powered chatbot providing accurate sex education for Indian users**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.83+-green.svg)](https://crewai.com)
[![Flask](https://img.shields.io/badge/Flask-2.3+-red.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 🌟 Overview

**Aarogya Mitram** (आरोग्य मित्रम् - "Health Friend" in Sanskrit) is an advanced AI chatbot designed to provide comprehensive, age-appropriate, and culturally-sensitive sex education for users in the Indian context. Built with CrewAI's multi-agent framework, it offers accurate information while respecting cultural values and providing crisis support when needed.

### ✨ Key Features

- 🤖 **Multi-Agent AI System**: Powered by CrewAI with specialized agents for different aspects of sex education
- 🇮🇳 **Cultural Sensitivity**: Responses adapted for Indian cultural context and values
- 🔒 **Privacy-First**: Secure, confidential conversations with no data storage
- 🚨 **Crisis Detection**: Automatic detection of distress with immediate support resources
- 📱 **Multi-Platform**: Both web interface and command-line interface
- 🎯 **Intent Recognition**: Smart categorization of queries for appropriate responses
- 🌐 **Responsive Design**: Mobile-friendly web interface with modern UI

### 🎯 Target Audience

- Teenagers and young adults seeking reliable sex education
- Parents looking for guidance on discussing sensitive topics
- Educators and counselors in need of culturally-appropriate resources
- Healthcare workers providing sexual health education

---

## 🚀 Quick Start

### 📋 Prerequisites

- **Python**: 3.10 or higher (≤ 3.13)
- **Operating System**: Windows, macOS, or Linux
- **Internet Connection**: Required for AI API calls and web search

### 🔧 Installation

#### Option 1: Using UV (Recommended)

```bash
# 1. Clone the repository
git clone <repository-url>
cd sex_educator

# 2. Install UV package manager
pip install uv

# 3. Install dependencies
crewai install

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys (see Configuration section)
```

#### Option 2: Using pip

```bash
# 1. Clone the repository
git clone <repository-url>
cd sex_educator

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys (see Configuration section)
```

---

## ⚙️ Configuration

### 🔑 Required API Keys

Create a `.env` file in the project root with the following:

```env
# Required: Get from https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Required: Get from https://serper.dev/dashboard
SERPER_DEV_API_KEY=your_serper_api_key_here
```

#### Getting API Keys:

1. **Gemini API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Create a new API key
   - Copy the key to your `.env` file

2. **Serper Dev API Key**:
   - Visit [Serper.dev](https://serper.dev/dashboard)
   - Sign up for a free account
   - Get your API key from the dashboard
   - Copy the key to your `.env` file

### 🎛️ Optional Configuration

You can customize additional settings in your `.env` file:

```env
# Application Settings
FLASK_PORT=5000
LOG_LEVEL=INFO
MAX_MESSAGE_LENGTH=500
RATE_LIMIT_PER_MINUTE=30
```

---

## 🖥️ Usage

### 🌐 Web Interface (Recommended)

Start the web interface for the best user experience:

```bash
# Start the web server
web

# Or alternatively:
python src/sex_educator/web_app.py
```

Then open your browser to: **http://localhost:5000**

#### Web Interface Features:
- 🎨 Modern, responsive design with Indian cultural theming
- 💬 Real-time chat with typing indicators
- ⚡ Quick action buttons for common questions
- 🔒 Privacy indicators and security information
- 📞 Emergency helpline numbers for India
- 📱 Mobile-optimized interface

### 💻 Command Line Interface

For terminal-based interaction:

```bash
# Start CLI chatbot
chat

# Or alternatively:
python src/sex_educator/chatbot.py
```

### 🔬 Other Commands

```bash
# Run the full CrewAI workflow
sex_educator

# Train the AI system
train <iterations> <filename>

# Test specific functionality
test <iterations> <model_name>

# Replay previous conversations
replay <task_id>
```

---

## 🏗️ Architecture

### 🤖 Multi-Agent System

The chatbot uses CrewAI's multi-agent architecture with specialized agents:

| Agent | Role | Purpose |
|-------|------|---------|
| **Researcher** | Data Research | Finds latest information on sex education and AI |
| **Curriculum Curator** | Content Validation | Ensures accurate, age-appropriate content |
| **Conversation Handler** | User Interaction | Manages empathetic, culturally-sensitive responses |
| **Cultural Adapter** | Localization | Adapts content for Indian regional contexts |
| **Legal Compliance** | Regulation Check | Ensures compliance with Indian laws |
| **Escalation Agent** | Crisis Management | Detects and handles crisis situations |
| **Outreach Coordinator** | User Engagement | Manages accessibility and feedback |
| **Feedback Analyzer** | Data Analysis | Analyzes user interactions for improvements |

### 📁 Project Structure

```
sex_educator/
├── 📄 README.md                    # This file
├── 📄 .env.example                 # Environment template
├── 📄 .gitignore                   # Git ignore rules
├── 📄 requirements.txt             # pip dependencies
├── 📄 pyproject.toml              # Modern Python project config
├── 📄 CLAUDE.md                   # AI assistant guidance
├── 📂 src/sex_educator/
│   ├── 🐍 __init__.py             # Package initialization
│   ├── 🤖 chatbot.py              # Main chatbot logic
│   ├── 👥 crew.py                 # CrewAI agents and tasks
│   ├── 🚀 main.py                 # Entry points
│   ├── 🌐 web_app.py              # Flask web application
│   ├── 📂 config/
│   │   ├── 👥 agents.yaml         # Agent configurations
│   │   └── 📋 tasks.yaml          # Task definitions
│   ├── 📂 templates/
│   │   └── 🌐 index.html          # Web interface
│   ├── 📂 static/
│   │   ├── 🎨 css/style.css       # Styling
│   │   └── ⚡ js/script.js        # Frontend logic
│   └── 📂 tools/
│       ├── 🔍 SerperDevTool.py    # Web search integration
│       └── 🐍 __init__.py         # Tools package
├── 📂 tests/                      # Test files
├── 🧪 test_chatbot.py            # CLI testing
└── 🧪 test_web_app.py            # Web app testing
```

---

## 🧪 Testing

### 🔍 Quick Tests

```bash
# Test the command-line chatbot
python test_chatbot.py

# Test the web application
python test_web_app.py
```

### 🎯 Sample Test Queries

Try these questions to test the chatbot:

- "What is puberty?"
- "How do I talk to my parents about relationships?"
- "What is consent?"
- "How can I stay safe?"
- "I'm feeling sad and don't want to live" (crisis detection test)

---

## 🛡️ Safety Features

### 🚨 Crisis Detection

The chatbot automatically detects:
- Mental health crises
- Suicidal thoughts
- Abuse situations
- Emergency situations

When detected, it provides:
- Immediate supportive response
- Indian emergency helpline numbers
- Professional support resources
- Escalation to human experts

### 🔒 Privacy Protection

- **No data storage**: Conversations are not permanently stored
- **Encrypted communication**: All API calls are encrypted
- **Anonymous usage**: No personal information required
- **Local processing**: Sensitive filtering happens locally

### 🛑 Content Filtering

- Blocks inappropriate or explicit requests
- Maintains age-appropriate responses
- Respects cultural sensitivities
- Provides educational content only

---

## 🌍 Cultural Adaptation

### 🇮🇳 Indian Context Features

- **Regional Languages**: Support for common Indian languages
- **Cultural Values**: Respects traditional and modern Indian values
- **Family Dynamics**: Considers joint family systems and hierarchies
- **Legal Framework**: Aligned with Indian laws and regulations
- **Healthcare System**: References Indian healthcare resources

### 📞 Emergency Resources (India)

| Service | Number | Purpose |
|---------|---------|---------|
| Emergency Services | 112 | General emergencies |
| Women's Helpline | 1091 | Women in distress |
| Child Helpline | 1098 | Children needing help |
| Mental Health Helpline | 9152987821 | Mental health support |
| NIMHANS Helpline | 080-46110007 | Psychiatric emergencies |

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 🐛 Reporting Issues

1. Check existing issues on GitHub
2. Create a detailed bug report
3. Include steps to reproduce
4. Specify your environment

### 💻 Code Contributions

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### 📝 Content Contributions

- Suggest improvements to responses
- Add new educational content
- Improve cultural sensitivity
- Report inaccuracies

---

## 📚 Documentation

### 🔗 Additional Resources

- **CrewAI Documentation**: [docs.crewai.com](https://docs.crewai.com)
- **Flask Documentation**: [flask.palletsprojects.com](https://flask.palletsprojects.com/)
- **Gemini API**: [ai.google.dev](https://ai.google.dev)

### 📖 Educational Resources

- **Comprehensive Sexuality Education**: [UNESCO Guidelines](https://www.unesco.org/en/health-education/comprehensive-sexuality-education)
- **Indian Government Resources**: [Ministry of Health & Family Welfare](https://www.mohfw.gov.in/)
- **Youth Health Resources**: [Tarshi](https://www.tarshi.net/)

---

## ⚠️ Disclaimer

This chatbot is designed for educational purposes only and should not replace professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers for medical concerns. The chatbot aims to provide accurate information but cannot guarantee the completeness or accuracy of all content.

If you are experiencing a mental health crisis, please contact emergency services immediately or reach out to the helplines provided in the chatbot.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **CrewAI Team** for the powerful multi-agent framework
- **Google** for the Gemini AI API
- **Serper.dev** for web search capabilities
- **Indian healthcare organizations** for guidance on cultural sensitivity
- **Open source community** for various tools and libraries

---

## 📞 Support

If you need help or have questions:

1. 📖 Check this README first
2. 🔍 Search existing issues on GitHub
3. 💬 Create a new issue with details
4. 📧 Contact the maintainers

---

<div align="center">

**🌸 Built with ❤️ for comprehensive sex education in India 🇮🇳**

*"Education is the most powerful weapon which you can use to change the world."* - Nelson Mandela

</div>