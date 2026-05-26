"""CLI entry point — run with: python -m edge_tts_minimal"""

import argparse
import asyncio
import sys
from pathlib import Path

from .client import list_voices, synthesize


def main() -> None:
    # "voices" subcommand handled manually to keep the default speak path
    # free of subparser interference with positional text.
    if len(sys.argv) > 1 and sys.argv[1] == "voices":
        voices = asyncio.run(list_voices())
        for v in voices:
            print(f"{v['ShortName']:40s} {v['Locale']:12s} {v['Gender']}")
        return

    if len(sys.argv) > 1 and sys.argv[1] == "web":
        port = 8100
        for i, arg in enumerate(sys.argv):
            if arg in ("-p", "--port") and i + 1 < len(sys.argv):
                port = int(sys.argv[i + 1])
        from .web import run_server
        run_server(port=port)
        return

    parser = argparse.ArgumentParser(
        prog="edge-tts-minimal",
        description="Text-to-speech via Microsoft Edge's free TTS service.",
    )
    src = parser.add_mutually_exclusive_group()
    src.add_argument("text", nargs="?", help="Text to speak")
    src.add_argument("-f", "--file", help="Read text from file")
    parser.add_argument(
        "-v", "--voice", default="en-US-AriaNeural",
        help="Voice short name (default: en-US-AriaNeural)",
    )
    parser.add_argument("-o", "--output", default="output.mp3", help="Output MP3 path")
    parser.add_argument(
        "--ssml", action="store_true",
        help="Treat input as raw SSML instead of plain text",
    )

    args = parser.parse_args(sys.argv[1:])

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        parser.error("Either TEXT or --file is required")

    asyncio.run(
        synthesize(
            ssml=text if args.ssml else None,
            text=None if args.ssml else text,
            voice=args.voice,
            output=args.output,
        )
    )
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
