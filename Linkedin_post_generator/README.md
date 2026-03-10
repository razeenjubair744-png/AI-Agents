# 💼 LinkedIn Post Generator

> AI-powered multi-agent pipeline using **OpenAI Agents SDK** + **FastAPI** + **Streamlit** + **Gradio**

---

## 🏗️ Architecture

```
User Input
    │
    ▼
┌─────────────────────────────────┐
│         FastAPI Backend         │
│  POST /generate                 │
│  POST /generate/variants        │
│  POST /generate/batch           │
│  GET  /generate/stream          │
└────────────┬────────────────────┘
             │
    ┌────────▼────────┐
    │ Agent Pipeline  │
    │                 │
    │ 1. ResearchAgent│  ← gpt-4o
    │       ↓         │
    │ 2. ToneAgent    │  ← gpt-4o
    │       ↓         │
    │ 3. FormatterAgent│ ← gpt-4o
    │       ↓         │
    │ 4. HashtagAgent │  ← gpt-4o-mini
    └────────┬────────┘
             │
    ┌────────▼──────────┐
    │    UI Clients     │
    │  • Streamlit :8501│
    │  • Gradio    :7860│
    │  • CLI            │
    └───────────────────┘
```

---

## 📁 Project Structure

```
linkedin-generator/
├── .env.example              # Environment variables template
├── requirements.txt          # Python dependencies
├── cli.py                    # Command-line interface
├── pipeline.py               # Core agent pipeline
│
├── agents/
│   ├── __init__.py
│   ├── research_agent.py     # Researches and expands topic
│   ├── tone_agent.py         # Adjusts content voice/style
│   ├── formatter_agent.py    # Formats final LinkedIn post
│   └── hashtag_agent.py      # Generates optimized hashtags
│
├── api/
│   ├── __init__.py
│   └── main.py               # FastAPI app with 5 endpoints
│
└── ui/
    ├── streamlit_app.py      # Streamlit interface
    └── gradio_app.py         # Gradio interface
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone <your-repo>
cd linkedin-generator

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Start the API

```bash
uvicorn api.main:app --reload --port 8000
```

### 4. Launch a UI

**Streamlit:**
```bash
streamlit run ui/streamlit_app.py
# Opens at http://localhost:8501
```

**Gradio:**
```bash
python ui/gradio_app.py
# Opens at http://localhost:7860
```

**CLI:**
```bash
python cli.py --topic "Why developers burn out" --tone storytelling
python cli.py --topic "AI in hiring" --tone contrarian --variants 3
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Overview & available endpoints |
| GET | `/health` | Health check |
| GET | `/tones` | List all available tones |
| POST | `/generate` | Generate a single post |
| POST | `/generate/variants` | Generate N variants in parallel |
| POST | `/generate/batch` | Batch posts for multiple topics |
| GET | `/generate/stream` | Streaming with real-time progress |

### Interactive Docs
Visit `http://localhost:8000/docs` for Swagger UI.

### Example Requests

**Single Post:**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Why most developers burn out", "tone": "storytelling"}'
```

**Multiple Variants:**
```bash
curl -X POST http://localhost:8000/generate/variants \
  -H "Content-Type: application/json" \
  -d '{"topic": "Remote work future", "tone": "contrarian", "count": 3}'
```

**Batch:**
```bash
curl -X POST http://localhost:8000/generate/batch \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [
      {"topic": "AI in hiring", "tone": "professional"},
      {"topic": "Developer burnout", "tone": "storytelling"},
      {"topic": "Remote work myths", "tone": "contrarian"}
    ]
  }'
```

**Streaming:**
```bash
curl "http://localhost:8000/generate/stream?topic=AI+replacing+jobs&tone=contrarian"
```

---

## 🎨 Available Tones

| Tone | Style |
|------|-------|
| `professional` | Authoritative, data-driven, executive-level |
| `storytelling` | Personal, narrative-first, human |
| `contrarian` | Challenges conventional wisdom |
| `inspirational` | Motivating, forward-looking |
| `educational` | Step-by-step, explains the "why" |
| `humorous` | Witty, light-hearted, unexpected |

---

## 🤖 Agent Details

### ResearchAgent (`gpt-4o`)
Expands the topic with key insights, trends, statistics, examples, and actionable takeaways.

### ToneAgent (`gpt-4o`)
Rewrites research content to match the desired tone while preserving all facts and data.

### FormatterAgent (`gpt-4o`)
Structures everything into a viral LinkedIn post with hook, context, bullets, CTA, and hashtags.

### HashtagAgent (`gpt-4o-mini`)
Generates 5 optimized hashtags mixing broad, niche, trending, and topic-specific tags.

---

## 🔧 Advanced Usage

### Generate Variants Programmatically

```python
import asyncio
from pipeline import generate_post, generate_variants

async def main():
    # Single post
    result = await generate_post("AI in education", "inspirational")
    print(result.post)

    # 3 variants in parallel
    variants = await generate_variants("Remote work", "contrarian", count=3)
    for v in variants:
        print(v.post)

asyncio.run(main())
```

### Custom Agent Configuration

```python
from agents import Agent

my_agent = Agent(
    name="CustomAgent",
    instructions="Your custom system prompt...",
    model="gpt-4o",
)
```

---

## 📈 Performance Tips

- **Batch mode** generates all posts in parallel — 5 posts take ~same time as 1
- **Variants** also run in parallel
- Use `gpt-4o-mini` for HashtagAgent to reduce cost
- Cache research results if generating variants on the same topic

---

## 📄 License

MIT