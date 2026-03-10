"""
CLI for LinkedIn Post Generator
Usage: python cli.py --topic "Your topic" --tone professional
"""

import asyncio
import argparse
import sys
import os

# Allow running from project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline import generate_post, generate_variants


def print_banner():
    print("\n" + "=" * 60)
    print("  💼  LinkedIn Post Generator  —  OpenAI Agents SDK")
    print("=" * 60)


async def main():
    parser = argparse.ArgumentParser(
        description="Generate LinkedIn posts using AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py --topic "AI in hiring" --tone professional
  python cli.py --topic "Developer burnout" --tone storytelling
  python cli.py --topic "Remote work future" --tone contrarian --variants 3
        """,
    )
    parser.add_argument("--topic", required=True, help="Topic or idea for the post")
    parser.add_argument(
        "--tone",
        default="professional",
        choices=["professional", "storytelling", "contrarian", "inspirational", "educational", "humorous"],
        help="Writing tone (default: professional)",
    )
    parser.add_argument("--variants", type=int, default=1, help="Number of variants to generate (default: 1)")
    parser.add_argument("--show-research", action="store_true", help="Print research notes")

    args = parser.parse_args()
    print_banner()

    print(f"\n📌 Topic:   {args.topic}")
    print(f"🎨 Tone:    {args.tone}")
    print(f"🔢 Variants: {args.variants}")
    print("\n⏳ Running agent pipeline...\n")

    if args.variants == 1:
        result = await generate_post(args.topic, args.tone)

        if args.show_research:
            print("─" * 60)
            print("🔍 RESEARCH NOTES")
            print("─" * 60)
            print(result.research)

        print("\n" + "─" * 60)
        print("📄 GENERATED LINKEDIN POST")
        print("─" * 60)
        print(result.post)
        print("\n" + "─" * 60)
        print(f"📊 Characters: {result.char_count} | Tone: {result.tone}")

    else:
        results = await generate_variants(args.topic, args.tone, args.variants)
        for i, result in enumerate(results):
            print(f"\n{'=' * 60}")
            print(f"📄 VARIANT {i + 1}")
            print("=" * 60)
            print(result.post)
            print(f"\n📊 Characters: {result.char_count}")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(main())