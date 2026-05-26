"""CLI entry point — run with: python -m edge_tts_minimal"""

import argparse
import asyncio
import sys

from .client import list_voices, synthesize


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="edge-tts-minimal",
        description="Text-to-speech via Microsoft Edge's free TTS service.",
    )
    sub = parser.add_subparsers(dest="command")

    # ---- speak ----
    speak = sub.add_parser("speak", help="Convert text to MP3")
    speak.add_argument("text", help="Text to speak")
    speak.add_argument(
        "-v", "--voice", default="zh-CN-XiaoxiaoNeural",
        help="Voice short name (default: zh-CN-XiaoxiaoNeural)",
    )
    speak.add_argument("-o", "--output", default="output.mp3", help="Output MP3 path")
    speak.add_argument(
        "--ssml", action="store_true",
        help="Treat TEXT as raw SSML instead of plain text",
    )

    # ---- voices ----
    sub.add_parser("voices", help="List available neural voices")

    args = parser.parse_args()

    if args.command == "speak":
        asyncio.run(
            synthesize(
                ssml=args.text if args.ssml else None,
                text=None if args.ssml else args.text,
                voice=args.voice,
                output=args.output,
            )
        )
        print(f"Saved to {args.output}")
    elif args.command == "voices":
        voices = asyncio.run(list_voices())
        for v in voices:
            print(f"{v['ShortName']:40s} {v['Locale']:12s} {v['Gender']}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
