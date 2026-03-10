"""
Gradio UI for LinkedIn Post Generator
Run: python ui/gradio_app.py
"""

import gradio as gr
import httpx
import json
import time

API_BASE = "http://localhost:8000"

TONES = [
    "professional",
    "storytelling",
    "contrarian",
    "inspirational",
    "educational",
    "humorous",
]

TONE_EMOJIS = {
    "professional": "📊",
    "storytelling": "📖",
    "contrarian": "⚡",
    "inspirational": "🌟",
    "educational": "🎓",
    "humorous": "😄",
}

# ─── API Helpers ──────────────────────────────────────────────────────────────

def call_api(endpoint: str, payload: dict) -> dict:
    try:
        r = httpx.post(f"{API_BASE}{endpoint}", json=payload, timeout=180)
        r.raise_for_status()
        return r.json()
    except httpx.ConnectError:
        raise gr.Error("Cannot connect to API. Start with: uvicorn api.main:app --reload")
    except httpx.HTTPStatusError as e:
        raise gr.Error(f"API error {e.response.status_code}: {e.response.text}")


# ─── Tab 1: Single Post ───────────────────────────────────────────────────────

def generate_single(topic: str, tone: str, show_research: bool):
    if not topic.strip():
        raise gr.Error("Please enter a topic.")

    start = time.time()
    data = call_api("/generate", {"topic": topic, "tone": tone})
    elapsed = time.time() - start

    research_out = data["research"] if show_research else "Enable 'Show Research' to view."

    stats = (
        f"⏱ **Time:** {data['generation_time_seconds']}s  |  "
        f"📝 **Characters:** {data['char_count']}  |  "
        f"🎨 **Tone:** {tone.title()}"
    )

    return data["post"], research_out, stats


# ─── Tab 2: Variants ──────────────────────────────────────────────────────────

def generate_variants_ui(topic: str, tone: str, count: int):
    if not topic.strip():
        raise gr.Error("Please enter a topic.")

    data = call_api("/generate/variants", {"topic": topic, "tone": tone, "count": int(count)})
    variants = data["variants"]

    # Pad to always return 5 outputs
    while len(variants) < 5:
        variants.append("")

    return tuple(variants[:5])


# ─── Tab 3: Batch ─────────────────────────────────────────────────────────────

def generate_batch_ui(topics_text: str, tone: str):
    topics = [t.strip() for t in topics_text.strip().split("\n") if t.strip()]
    if not topics:
        raise gr.Error("Please enter at least one topic.")
    if len(topics) > 10:
        raise gr.Error("Maximum 10 topics per batch.")

    payload = {"posts": [{"topic": t, "tone": tone} for t in topics]}
    data = call_api("/generate/batch", payload)

    output_parts = []
    for i, result in enumerate(data["results"]):
        output_parts.append(
            f"{'='*60}\n"
            f"📌 Topic {i+1}: {result['topic']}\n"
            f"🎨 Tone: {result['tone']} | 📝 Chars: {result['char_count']}\n"
            f"{'='*60}\n\n"
            f"{result['post']}\n"
        )

    summary = f"✅ Generated {data['total_generated']} posts in {data['total_time_seconds']}s"
    return "\n\n".join(output_parts), summary


# ─── Tab 4: Streaming ─────────────────────────────────────────────────────────

def generate_stream_ui(topic: str, tone: str):
    if not topic.strip():
        raise gr.Error("Please enter a topic.")

    output = ""
    try:
        with httpx.stream(
            "GET",
            f"{API_BASE}/generate/stream",
            params={"topic": topic, "tone": tone},
            timeout=180,
        ) as r:
            for line in r.iter_lines():
                if line.startswith("data: "):
                    chunk = line[6:]
                    if chunk == "[DONE]":
                        break
                    output += chunk
                    yield output
    except httpx.ConnectError:
        yield "❌ Cannot connect to API. Make sure it's running."


# ─── Build UI ─────────────────────────────────────────────────────────────────

custom_css = """
#post-output textarea {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    font-size: 0.95rem !important;
    line-height: 1.6 !important;
    border-left: 4px solid #0077b5 !important;
    background: #f8fafc !important;
    padding: 1rem !important;
}
.tab-nav button {
    font-weight: 600 !important;
}
"""

with gr.Blocks(
    title="LinkedIn Post Generator",
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "sans-serif"],
    ),
    css=custom_css,
) as app:

    # Header
    gr.Markdown("""
    # 💼 LinkedIn Post Generator
    **AI-powered multi-agent pipeline** — Research → Tone → Format → Hashtags
    
    Connect your API at `http://localhost:8000` • Built with OpenAI Agents SDK
    """)

    with gr.Tabs():

        # ── Tab 1: Single Post ─────────────────────────────────────────────
        with gr.TabItem("✍️ Single Post"):
            gr.Markdown("Generate one polished LinkedIn post from a topic or idea.")

            with gr.Row():
                with gr.Column(scale=2):
                    topic_1 = gr.Textbox(
                        label="Topic or Idea",
                        placeholder="e.g. Why most developers burn out — and how to avoid it",
                        lines=3,
                    )
                    tone_1 = gr.Dropdown(
                        choices=TONES,
                        value="professional",
                        label="Writing Tone",
                    )
                    show_research = gr.Checkbox(label="Show research notes", value=False)
                    btn_1 = gr.Button("🚀 Generate Post", variant="primary", size="lg")

                with gr.Column(scale=3):
                    stats_1 = gr.Markdown("")
                    post_out_1 = gr.Textbox(
                        label="Generated LinkedIn Post",
                        lines=15,
                        interactive=True,
                        elem_id="post-output",
                    )
                    research_out_1 = gr.Textbox(
                        label="Research Notes",
                        lines=6,
                        visible=True,
                    )

            btn_1.click(
                generate_single,
                inputs=[topic_1, tone_1, show_research],
                outputs=[post_out_1, research_out_1, stats_1],
            )

        # ── Tab 2: Multiple Variants ───────────────────────────────────────
        with gr.TabItem("🔄 Variants"):
            gr.Markdown("Generate multiple versions for A/B testing. All variants generated in parallel.")

            with gr.Row():
                topic_2 = gr.Textbox(
                    label="Topic",
                    placeholder="e.g. The future of remote work",
                    lines=2,
                    scale=3,
                )
                tone_2 = gr.Dropdown(choices=TONES, value="professional", label="Tone", scale=1)
                count_2 = gr.Slider(minimum=2, maximum=5, value=3, step=1, label="Variants", scale=1)

            btn_2 = gr.Button("🚀 Generate Variants", variant="primary")

            with gr.Row():
                variant_boxes = [
                    gr.Textbox(label=f"Variant {i+1}", lines=12, interactive=True)
                    for i in range(5)
                ]

            btn_2.click(
                generate_variants_ui,
                inputs=[topic_2, tone_2, count_2],
                outputs=variant_boxes,
            )

        # ── Tab 3: Batch ───────────────────────────────────────────────────
        with gr.TabItem("📦 Batch"):
            gr.Markdown("Generate posts for multiple topics at once. One topic per line. Max 10.")

            with gr.Row():
                with gr.Column(scale=1):
                    topics_input = gr.Textbox(
                        label="Topics (one per line)",
                        placeholder="AI replacing junior developers\nWhy remote work is failing\nThe future of product management",
                        lines=10,
                    )
                    tone_3 = gr.Dropdown(choices=TONES, value="professional", label="Tone for all posts")
                    btn_3 = gr.Button("🚀 Generate Batch", variant="primary")

                with gr.Column(scale=2):
                    summary_3 = gr.Markdown("")
                    batch_out = gr.Textbox(label="All Generated Posts", lines=25, interactive=True)

            btn_3.click(
                generate_batch_ui,
                inputs=[topics_input, tone_3],
                outputs=[batch_out, summary_3],
            )

        # ── Tab 4: Stream ──────────────────────────────────────────────────
        with gr.TabItem("⚡ Live Stream"):
            gr.Markdown("Watch the agent pipeline run in real-time with live progress updates.")

            with gr.Row():
                topic_4 = gr.Textbox(
                    label="Topic",
                    placeholder="e.g. How to negotiate your first salary",
                    lines=2,
                    scale=3,
                )
                tone_4 = gr.Dropdown(choices=TONES, value="professional", label="Tone", scale=1)

            btn_4 = gr.Button("⚡ Stream Generation", variant="primary")
            stream_out = gr.Textbox(label="Live Output", lines=20, interactive=False)

            btn_4.click(
                generate_stream_ui,
                inputs=[topic_4, tone_4],
                outputs=stream_out,
            )

        # ── Tab 5: API Docs ────────────────────────────────────────────────
        with gr.TabItem("📚 API Docs"):
            gr.Markdown(f"""
            ## API Endpoints

            Base URL: `{API_BASE}`

            | Method | Endpoint | Description |
            |--------|----------|-------------|
            | GET | `/` | Overview & health |
            | GET | `/tones` | List available tones |
            | POST | `/generate` | Single post |
            | POST | `/generate/variants` | Multiple variants (parallel) |
            | POST | `/generate/batch` | Batch posts for multiple topics |
            | GET | `/generate/stream` | Streaming with progress |

            ## Example Request
            ```bash
            curl -X POST http://localhost:8000/generate \\
              -H "Content-Type: application/json" \\
              -d '{{"topic": "Why developers burn out", "tone": "storytelling"}}'
            ```

            ## Pipeline
            ```
            Topic Input
                ↓
            ResearchAgent     → gpt-4o   → Key insights & data
                ↓
            ToneAgent         → gpt-4o   → Voice & style adjustment
                ↓
            FormatterAgent    → gpt-4o   → LinkedIn post structure
                ↓
            HashtagAgent      → gpt-4o-mini → Optimized hashtags
                ↓
            Final LinkedIn Post
            ```
            """)

    gr.Markdown("---\n*Built with OpenAI Agents SDK + FastAPI + Gradio*")


if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_api=True,
    )