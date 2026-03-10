"""
Streamlit UI for LinkedIn Post Generator
Run: streamlit run ui/streamlit_app.py
"""

import streamlit as st
import httpx
import asyncio
import json
import time

# ─── Config ───────────────────────────────────────────────────────────────────

API_BASE = "http://localhost:8000"

TONE_DESCRIPTIONS = {
    "professional": "📊 Authoritative & data-driven",
    "storytelling": "📖 Personal & narrative-first",
    "contrarian": "⚡ Challenges conventional wisdom",
    "inspirational": "🌟 Motivating & forward-looking",
    "educational": "🎓 Step-by-step & explanatory",
    "humorous": "😄 Witty & light-hearted",
}

# ─── Page Setup ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="LinkedIn Post Generator",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0077b5 0%, #00a0dc 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .post-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #0077b5;
        padding: 1.5rem;
        border-radius: 8px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        white-space: pre-wrap;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    .stage-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    .stTextArea textarea {
        font-size: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>💼 LinkedIn Post Generator</h1>
    <p>AI-powered multi-agent pipeline • Research → Tone → Format → Hashtags</p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("⚙️ Settings")

    api_url = st.text_input("API Base URL", value=API_BASE)

    st.divider()
    st.header("📋 Mode")
    mode = st.radio(
        "Select mode",
        ["Single Post", "Multiple Variants", "Batch Generate"],
        label_visibility="collapsed",
    )

    st.divider()
    st.header("🎨 Tone")
    tone = st.selectbox(
        "Writing tone",
        options=list(TONE_DESCRIPTIONS.keys()),
        format_func=lambda x: TONE_DESCRIPTIONS[x],
    )

    if mode == "Multiple Variants":
        variant_count = st.slider("Number of variants", 2, 5, 3)

    st.divider()
    st.caption("Powered by OpenAI Agents SDK")
    st.caption("Pipeline: Research → Tone → Format → Hashtags")

# ─── Check API ────────────────────────────────────────────────────────────────

def check_api():
    try:
        r = httpx.get(f"{api_url}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


api_ok = check_api()
if api_ok:
    st.success("✅ API Connected", icon="🟢")
else:
    st.error("❌ API not reachable. Start with: `uvicorn api.main:app --reload`")

# ─── Main UI ──────────────────────────────────────────────────────────────────

if mode == "Single Post":
    st.subheader("✍️ Generate a Post")

    topic = st.text_area(
        "Topic or idea",
        placeholder="e.g. Why most developers burn out — and how to prevent it",
        height=100,
    )

    show_research = st.checkbox("Show research process", value=False)

    if st.button("🚀 Generate Post", disabled=not api_ok, type="primary", use_container_width=True):
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Running agent pipeline..."):
                stages = st.empty()
                stages.markdown("🔍 **Stage 1:** Researching topic...")

                start = time.time()
                try:
                    r = httpx.post(
                        f"{api_url}/generate",
                        json={"topic": topic, "tone": tone},
                        timeout=120,
                    )
                    r.raise_for_status()
                    data = r.json()

                    stages.markdown("✅ All stages complete!")
                    elapsed = time.time() - start

                    # Metrics
                    col1, col2, col3 = st.columns(3)
                    col1.metric("⏱ Generation Time", f"{data['generation_time_seconds']}s")
                    col2.metric("📝 Characters", data["char_count"])
                    col3.metric("🎨 Tone", tone.title())

                    st.divider()

                    # Post output
                    st.subheader("📄 Your LinkedIn Post")
                    st.markdown(
                        f'<div class="post-card">{data["post"]}</div>',
                        unsafe_allow_html=True,
                    )

                    # Copy button
                    st.code(data["post"], language=None)

                    if show_research:
                        with st.expander("🔍 Research Notes"):
                            st.text(data["research"])

                    st.success(f"✅ Generated in {data['generation_time_seconds']}s")

                except httpx.HTTPError as e:
                    st.error(f"API Error: {e}")
                except Exception as e:
                    st.error(f"Error: {e}")

elif mode == "Multiple Variants":
    st.subheader("🔄 Generate Multiple Variants")
    st.caption("Generate several versions of the same post for A/B testing")

    topic = st.text_area(
        "Topic or idea",
        placeholder="e.g. The future of remote work",
        height=100,
    )

    if st.button("🚀 Generate Variants", disabled=not api_ok, type="primary", use_container_width=True):
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            with st.spinner(f"Generating {variant_count} variants in parallel..."):
                try:
                    r = httpx.post(
                        f"{api_url}/generate/variants",
                        json={"topic": topic, "tone": tone, "count": variant_count},
                        timeout=180,
                    )
                    r.raise_for_status()
                    data = r.json()

                    st.success(f"✅ Generated {data['count']} variants")
                    st.divider()

                    tabs = st.tabs([f"Variant {i+1}" for i in range(len(data["variants"]))])
                    for i, (tab, variant) in enumerate(zip(tabs, data["variants"])):
                        with tab:
                            st.markdown(
                                f'<div class="post-card">{variant}</div>',
                                unsafe_allow_html=True,
                            )
                            st.code(variant, language=None)
                            st.caption(f"Characters: {len(variant)}")

                except Exception as e:
                    st.error(f"Error: {e}")

elif mode == "Batch Generate":
    st.subheader("📦 Batch Generate")
    st.caption("Generate posts for multiple topics at once (max 10)")

    topics_raw = st.text_area(
        "Enter topics (one per line)",
        placeholder="AI replacing junior developers\nWhy remote work is failing\nThe future of product management",
        height=200,
    )

    batch_tone = st.selectbox(
        "Tone for all posts",
        options=list(TONE_DESCRIPTIONS.keys()),
        format_func=lambda x: TONE_DESCRIPTIONS[x],
        key="batch_tone",
    )

    if st.button("🚀 Generate Batch", disabled=not api_ok, type="primary", use_container_width=True):
        topics = [t.strip() for t in topics_raw.strip().split("\n") if t.strip()]
        if not topics:
            st.warning("Please enter at least one topic.")
        elif len(topics) > 10:
            st.error("Maximum 10 topics per batch.")
        else:
            with st.spinner(f"Generating {len(topics)} posts..."):
                payload = {"posts": [{"topic": t, "tone": batch_tone} for t in topics]}
                try:
                    r = httpx.post(
                        f"{api_url}/generate/batch",
                        json=payload,
                        timeout=300,
                    )
                    r.raise_for_status()
                    data = r.json()

                    st.success(f"✅ Generated {data['total_generated']} posts in {data['total_time_seconds']}s")
                    st.divider()

                    for i, result in enumerate(data["results"]):
                        with st.expander(f"📄 Post {i+1}: {result['topic'][:60]}..."):
                            st.markdown(
                                f'<div class="post-card">{result["post"]}</div>',
                                unsafe_allow_html=True,
                            )
                            col1, col2 = st.columns(2)
                            col1.caption(f"Tone: {result['tone']}")
                            col2.caption(f"Characters: {result['char_count']}")
                            st.code(result["post"], language=None)

                except Exception as e:
                    st.error(f"Error: {e}")