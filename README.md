# 🤖 AI Agents

A comprehensive collection of production-ready AI agents built using cutting-edge frameworks including **CrewAI**, **LangChain**, **LangGraph**, and **OpenAI Agents SDK**. This repository showcases various multi-agent architectures solving real-world problems.

---

## 📚 Table of Contents

- [Overview](#overview)
- [Projects](#projects)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Projects In Detail](#projects-in-detail)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This repository contains a diverse collection of AI agent implementations demonstrating:

- **Multi-Agent Orchestration**: Coordinating multiple specialized agents
- **RAG (Retrieval-Augmented Generation)**: Grounding AI responses in documents
- **Structured Outputs**: Using Pydantic models for reliable data structures
- **Tool Integration**: Leveraging APIs and search tools
- **Modern Frameworks**: CrewAI, LangGraph, OpenAI Agents SDK
- **Full Stack Development**: Backend (FastAPI, Flask) + Frontend (Streamlit, Gradio, React)

**Repository Stats:**
- 📊 Language Composition: Python (60.1%) • Jupyter Notebook (33.8%) • JavaScript (6.1%)
- 📅 Created: March 10, 2026
- 🔧 Framework: Multi-framework AI agent implementation

---

## 🚀 Projects

### 1. **📋 Automated Project Planning Agent**
**Framework**: CrewAI | **Language**: Python

An intelligent multi-agent system for automated project planning, estimation, and resource allocation.

**Key Features:**
- 🎯 Task Breakdown: Decomposes project requirements into actionable tasks
- ⏱️ Time & Resource Estimation: Calculates effort and resource needs
- 👥 Resource Allocation: Optimally assigns resources to tasks
- 📊 Structured Output: Returns ProjectPlan with tasks and milestones (Pydantic)

**Files:**
- `main.py` - Main orchestration script
- `helper.py` - Utility functions
- `config/agents.yaml` - Agent configurations
- `config/tasks.yaml` - Task definitions

**Use Case:** Planning website development with multiple team members, estimating timelines, and resource allocation.

---

### 2. **🎬 Content Planner Agent (YouTube Shorts)**
**Framework**: CrewAI | **Language**: Python

AI-powered content planning agent for YouTube Shorts focusing on micro-history videos.

**Key Features:**
- 📱 Platform-Optimized: Tailored for YouTube Shorts (9:16 vertical, 30-45s)
- 🎣 Hook Generation: Creates attention-grabbing opening sequences
- 🎨 Visual Planning: Suggests filmable concepts with minimal props
- 🏷️ SEO Optimization: Generates searchable titles and hashtags
- 💬 Engagement: Creates comment-baiting CTAs

**Files:**
- `main.py` - Content planning pipeline
- `utils.py` - Helper utilities
- `pyproject.toml` - Dependencies

**Output Format:**
```json
{
  "videos": [
    {
      "title": "searchable title",
      "hook_main": "12-word hook",
      "hook_alt": "variant hook",
      "visuals": ["prop ideas"],
      "tags": ["#microhistory"],
      "cta": "engagement question"
    }
  ]
}
```

---

### 3. **📊 LangGraph RAG Agent**
**Framework**: LangGraph | **Language**: Python

Retrieval-Augmented Generation system for querying PDF documents using vector stores.

**Key Features:**
- 📄 PDF Loading: Processes documents with PyPDFLoader
- 🔍 Vector Search: ChromaDB for semantic similarity search
- 🤖 Agentic Loop: Conditional execution with tool calling
- 💬 Multi-turn Conversations: Maintains context across queries
- 📚 Citation Support: References source documents

**Architecture:**
```
User Query
    ↓
LLM Agent (with tool binding)
    ↓
Retriever Tool (ChromaDB)
    ↓
Formatted Response
```

**Files:**
- `main.py` - RAG implementation with LangGraph
- `Stock_Market_Performance_2024.pdf` - Sample document
- `chroma_db/` - Vector store persistence

**Usage Example:**
```python
# Query the RAG system interactively
# "What was the stock market performance in Q3 2024?"
```

---

### 4. **💼 LinkedIn Post Generator**
**Framework**: OpenAI Agents SDK | **Language**: Python + JavaScript

Full-stack multi-agent system for generating engaging LinkedIn posts with multiple UI options.

**Key Features:**
- 🎯 Multi-Agent Pipeline: 4 specialized agents working in sequence
- 🎨 Tone Variants: Professional, Storytelling, Contrarian, Educational, Humorous, Inspirational
- ⚡ Batch Processing: Generate multiple posts in parallel
- 🔄 Variants Generation: Create N variations of the same topic
- 📡 Multiple UIs: Streamlit, Gradio, CLI interfaces
- 🔌 REST API: FastAPI backend with Swagger documentation

**Agent Pipeline:**
1. **ResearchAgent** (gpt-4o): Expands topic with insights and trends
2. **ToneAgent** (gpt-4o): Rewrites content in target tone
3. **FormatterAgent** (gpt-4o): Structures into viral LinkedIn format
4. **HashtagAgent** (gpt-4o-mini): Generates optimized hashtags

**Project Structure:**
```
Linkedin_post_generator/
├── api/
│   └── main.py              # FastAPI endpoints
├── app_agents/
│   ├── research_agent.py
│   ├── tone_agent.py
│   ├── formatter_agent.py
│   └── hashtag_agent.py
├── ui/
│   ├── streamlit_app.py     # Web interface
│   └── gradio_app.py        # Alternative UI
├── cli.py                   # Command-line interface
├── pipeline.py              # Core orchestration
└── requirements.txt
```

**API Endpoints:**
- `POST /generate` - Generate single post
- `POST /generate/variants` - Generate N variants
- `POST /generate/batch` - Batch process multiple topics
- `GET /generate/stream` - Streaming with progress

**Example CLI Usage:**
```bash
python cli.py --topic "Why developers burn out" --tone storytelling
python cli.py --topic "AI in hiring" --tone contrarian --variants 3
```

---

### 5. **🔬 Research Agent (Jupyter Notebooks)**
**Framework**: LangChain | **Language**: Python

Educational collection of Jupyter notebooks demonstrating research agent patterns and unit testing.

**Files:**
- `C1M5_Assignment.ipynb` - Core research agent implementation
- `research_tools.ipynb` - Tool creation and integration examples
- `unittests.ipynb` - Testing frameworks for agents

**Topics Covered:**
- Custom tool creation
- Agent tool selection
- Error handling and validation
- Unit testing patterns

---

### 6. **🔍 CrewAI Deep Research Agent**
**Framework**: CrewAI | **Language**: Python

Comprehensive multi-agent research system with fact-checking and report generation.

**Key Features:**
- 📋 Research Planning: Breaking down complex queries into research components
- 🌐 Web Search: Integrated with EXA Search API
- 🔗 Web Scraping: Gathering content from identified sources
- ✅ Fact Checking: Verifying data accuracy and flagging misinformation
- 📝 Report Generation: Creating structured Markdown reports

**Agent Roles:**
1. **Research Planner**: Breaks down queries into research objectives
2. **Internet Researcher**: Conducts searches and scraping (tools: EXA, Scraper)
3. **Fact Checker**: Verifies accuracy and identifies inconsistencies
4. **Report Writer**: Generates comprehensive, well-structured reports

**Files:**
- `main.py` - Main orchestration
- `utils.py` - API key management

**Sample Query:**
```python
user_query = "Conduct deep research about recent news on [topic]"
```

---

### 7. **⚙️ Deep Research Flow (LangGraph)**
**Framework**: LangGraph | **Language**: Python

Advanced LangGraph implementation for complex research workflows.

**Project Structure:**
```
deep_research_flow/
├── src/          # Source code
├── knowledge/    # Knowledge base
└── pyproject.toml
```

**Capabilities:**
- Advanced state management
- Complex workflow orchestration
- Multi-step research pipelines

---

### 8. **🌐 Deep Research Agent (Full Stack)**
**Framework**: LangChain + FastAPI + React | **Language**: Python + JavaScript

Full-stack web application combining backend AI and modern frontend.

**Components:**
- **Backend** (`agent.py`, `main.py`): FastAPI server with agent logic
- **Frontend** (`app.jsx`): React application for user interaction

**Files:**
- Backend: `/backend/`
  - `agent.py` - Agent implementation
  - `main.py` - FastAPI server
  - `requirements.txt` - Python dependencies
- Frontend: `/frontend/`
  - `app.jsx` - React application

---

## 🛠️ Tech Stack

### Frameworks & Libraries
- **CrewAI**: Multi-agent orchestration framework
- **LangChain**: LLM application framework
- **LangGraph**: Stateful graph-based agent workflows
- **OpenAI Agents SDK**: Official OpenAI agent framework
- **FastAPI**: Modern Python web framework
- **Streamlit**: Rapid prototyping UI framework
- **Gradio**: ML model interface builder
- **React/JSX**: Frontend development

### AI/ML
- **LLMs**: GPT-4o, GPT-4o-mini, Claude Sonnet
- **Embeddings**: OpenAI Embedding models
- **Vector Stores**: ChromaDB
- **Search APIs**: EXA Search API
- **PDF Processing**: PyPDF

### Data & Storage
- **ChromaDB**: Vector database for RAG
- **Pydantic**: Data validation and serialization

---

## 📁 Repository Structure

```
AI-Agents/
├── Automated _project_planning/      # CrewAI project planning
│   ├── main.py
│   ├── helper.py
│   ├── config/
│   │   ├── agents.yaml
│   │   └── tasks.yaml
│   └── pyproject.toml
│
├── Content_Planner_Agent/            # YouTube content planning
│   ├── main.py
│   ├── utils.py
│   └── pyproject.toml
│
├── Langgraph_RAG_Agent/              # Vector RAG with LangGraph
│   ├── main.py
│   ├── Stock_Market_Performance_2024.pdf
│   ├── chroma_db/
│   └── pyproject.toml
│
├── Linkedin_post_generator/          # Full-stack LinkedIn automation
│   ├── api/
│   │   └── main.py
│   ├── app_agents/
│   │   ├── research_agent.py
│   │   ├── tone_agent.py
│   │   ├── formatter_agent.py
│   │   └── hashtag_agent.py
│   ├── ui/
│   │   ├── streamlit_app.py
│   │   └── gradio_app.py
│   ├── cli.py
│   ├── pipeline.py
│   └── requirements.txt
│
├── Research Agent/                   # Educational notebooks
│   ├── C1M5_Assignment.ipynb
│   ├── research_tools.ipynb
│   └── unittests.ipynb
│
├── crew_ai_deep_research/            # Multi-agent research system
│   ├── main.py
│   ├── utils.py
│   └── pyproject.toml
│
├── deep_research_flow/               # LangGraph workflow
│   ├── src/
│   ├── knowledge/
│   └── pyproject.toml
│
├── Deep Research Agent/              # Full-stack application
│   ├── backend/
│   │   ├── agent.py
│   │   ├── main.py
│   │   └── requirements.txt
│   └── frontend/
│       └── app.jsx
│
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+ (for frontend projects)
- OpenAI API key
- (Optional) EXA API key for search functionality

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/razeenjubair744-png/AI-Agents.git
cd AI-Agents
```

2. **Set up environment variables**
```bash
# Create .env file in each project directory
OPENAI_API_KEY=your_openai_key_here
EXA_API_KEY=your_exa_key_here  # For search-enabled projects
```

3. **Install project dependencies**

Each project has its own `requirements.txt` or `pyproject.toml`:

```bash
# For specific project
cd Linkedin_post_generator
pip install -r requirements.txt

# Or using uv (if available)
uv sync
```

### Running Projects

**Automated Project Planning:**
```bash
cd Automated\ _project_planning
python main.py
```

**Content Planner Agent:**
```bash
cd Content_Planner_Agent
python main.py
```

**LangGraph RAG Agent:**
```bash
cd Langgraph_RAG_Agent
python main.py  # Interactive mode
```

**LinkedIn Post Generator:**
```bash
cd Linkedin_post_generator

# Start FastAPI server
uvicorn api.main:app --reload --port 8000

# In another terminal, launch UI
streamlit run ui/streamlit_app.py
# OR
python ui/gradio_app.py
# OR
python cli.py --topic "Your topic" --tone professional
```

**CrewAI Deep Research:**
```bash
cd crew_ai_deep_research
python main.py
```

**Deep Research Agent (Full Stack):**
```bash
# Backend
cd Deep\ Research\ Agent/backend
pip install -r requirements.txt
python main.py

# Frontend (in another terminal)
cd Deep\ Research\ Agent/frontend
npm install
npm start
```

---

## 📖 Projects In Detail

### Architectural Patterns

1. **Sequential Multi-Agent**: Project Planning, Content Planner
   - Agents work in sequence, passing outputs as inputs
   - Structured output validation with Pydantic

2. **Agentic Loop with Tools**: RAG Agent, Deep Research
   - Agents decide when to use tools
   - Conditional graph execution
   - Tool result feedback loops

3. **Parallel Processing**: LinkedIn Post Generator
   - Multiple agents or tasks run concurrently
   - Batch and variant generation optimization

4. **Full Stack**: Deep Research Agent, LinkedIn Generator
   - REST APIs for backend integration
   - Web/CLI/Programmatic interfaces
   - Real-time streaming capabilities

### Best Practices Demonstrated

✅ **Configuration Management**: YAML-based agent configs
✅ **Environment Variables**: Secure API key handling
✅ **Type Safety**: Pydantic models for structured outputs
✅ **Tool Integration**: Custom tool creation and binding
✅ **Error Handling**: Graceful degradation and fallbacks
✅ **Testing**: Unit test notebooks and validation
✅ **API Design**: RESTful endpoints with FastAPI
✅ **User Interfaces**: Multiple UI options (CLI, Web, API)

---

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:
- Additional agent implementations
- New framework integrations
- Performance optimizations
- Documentation improvements
- Test coverage expansion

---

## 📄 License

This project is available for educational and commercial use.

---

## 📞 Contact & Support

For questions, issues, or suggestions, please:
- Open an issue on GitHub
- Check existing project READMEs for detailed documentation
- Review notebook examples in Research Agent folder

---

## 🎓 Learning Resources

- **CrewAI**: Multi-agent framework fundamentals
- **LangChain**: LLM application patterns
- **LangGraph**: Stateful agent workflows
- **OpenAI Agents SDK**: Official agent patterns
- **RAG Patterns**: Document retrieval and grounding
- **Full Stack Development**: FastAPI + React integration

---

Built with ❤️ by **Quazi Razeen Jubair**

Last Updated: June 2026
