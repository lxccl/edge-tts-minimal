import asyncio
from edge_tts_minimal import synthesize, list_voices

async def main():
    # Simple text-to-speech
    audio = await synthesize(
        text="Hello world! This is a free text to speech demo.",
        voice="en-US-AriaNeural",
        output="hello.mp3",
    )
    print(f"Generated {len(audio)} bytes of audio")

    # List available voices (first 10)
    voices = await list_voices()
    neural = [v for v in voices if v.get("VoiceType") == "Neural"]
    print(f"\n{len(neural)} neural voices available. First 10:")
    for v in neural[:10]:
        print(f"  {v['ShortName']:40s} {v['Locale']:12s} {v['Gender']}")

if __name__ == "__main__":
    asyncio.run(main())
