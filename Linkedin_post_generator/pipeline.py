"""
Core LinkedIn post generation pipeline using OpenAI Agents SDK.
"""

import asyncio
from dataclasses import dataclass
from typing import AsyncIterator
from agents import Runner
from app_agents.research_agent import research_agent
from app_agents.tone_agent import tone_agent
from app_agents.formatter_agent import formatter_agent
from app_agents.hashtag_agent import hashtag_agent


@dataclass
class GenerationResult:
    topic: str
    tone: str
    research: str
    toned_content: str
    post: str
    hashtags: str
    char_count: int


async def generate_post(topic: str, tone: str = "professional") -> GenerationResult:
    """
    Full pipeline: Research → Tone → Format → Hashtags
    """

    # Stage 1: Research
    research_result = await Runner.run(
        research_agent,
        input=f"Research this topic thoroughly for a LinkedIn post: {topic}",
    )
    research_content = research_result.final_output

    # Stage 2: Tone adjustment
    tone_result = await Runner.run(
        tone_agent,
        input=f"Rewrite this content in a '{tone}' tone for LinkedIn:\n\n{research_content}",
    )
    toned_content = tone_result.final_output

    # Stage 3: Format final post
    post_result = await Runner.run(
        formatter_agent,
        input=f"""
Topic: {topic}
Tone: {tone}

Research content to format into a LinkedIn post:
{toned_content}
""",
    )
    post = post_result.final_output

    # Stage 4: Optimise hashtags
    hashtag_result = await Runner.run(
        hashtag_agent,
        input=f"Topic: {topic}\n\nPost:\n{post}",
    )
    hashtags = hashtag_result.final_output

    # Merge hashtags into post if not already present
    final_post = post
    if hashtags and not any(tag in post for tag in hashtags.split()[:1]):
        final_post = f"{post}\n\n{hashtags}"

    return GenerationResult(
        topic=topic,
        tone=tone,
        research=research_content,
        toned_content=toned_content,
        post=final_post,
        hashtags=hashtags,
        char_count=len(final_post),
    )


async def generate_variants(
    topic: str, tone: str = "professional", count: int = 3
) -> list[GenerationResult]:
    """Generate multiple post variants in parallel."""
    tasks = [generate_post(topic, tone) for _ in range(count)]
    return await asyncio.gather(*tasks)


async def stream_post(topic: str, tone: str = "professional") -> AsyncIterator[str]:
    """
    Stream the post generation step-by-step, yielding status updates and final post.
    Uses Runner.run_streamed for the formatter stage.
    """
    yield f"🔍 Researching: {topic}...\n"

    research_result = await Runner.run(
        research_agent,
        input=f"Research this topic for LinkedIn: {topic}",
    )
    research_content = research_result.final_output
    yield f"✅ Research complete ({len(research_content)} chars)\n"

    yield f"🎨 Adjusting tone: {tone}...\n"
    tone_result = await Runner.run(
        tone_agent,
        input=f"Rewrite in '{tone}' tone:\n\n{research_content}",
    )
    toned_content = tone_result.final_output
    yield f"✅ Tone adjusted\n"

    yield "✍️ Formatting LinkedIn post...\n"
    post_result = await Runner.run(
        formatter_agent,
        input=f"Topic: {topic}\nTone: {tone}\n\nContent:\n{toned_content}",
    )
    post = post_result.final_output

    hashtag_result = await Runner.run(
        hashtag_agent,
        input=f"Topic: {topic}\nPost:\n{post}",
    )
    hashtags = hashtag_result.final_output
    final_post = f"{post}\n\n{hashtags}"

    yield f"\n---POST---\n{final_post}"