# Edge TTS Minimal

Free, unlimited text-to-speech via Microsoft Edge's TTS service. No API key, no quota, no browser required.

## How it works

This library mimics the WebSocket protocol that Microsoft Edge browser uses for its "Read Aloud" feature. Microsoft provides the service as a free consumer offering — this project connects to the same public endpoint.

| Feature | Details |
|---|---|
| Voices | 500+ neural voices across 100+ locales |
| Formats | MP3, OGG, WAV (24 kHz) |
| Auth | No API key — uses Edge's public trust token |
| Dependencies | Python 3.10+, `websockets`, `aiohttp` |

## Install

```bash
pip install -e .
```

Or just install the dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### CLI

```bash
# Generate speech
python -m edge_tts_minimal speak "Hello world" -v en-US-AriaNeural -o output.mp3

# List available voices
python -m edge_tts_minimal voices
```

### Python API

```python
import asyncio
from edge_tts_minimal import synthesize

async def main():
    audio = await synthesize(
        text="Hello, this is a test.",
        voice="en-US-AriaNeural",
        output="test.mp3",
    )

asyncio.run(main())
```

### Advanced — raw SSML

```python
ssml = """
<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis'>
    <voice name='en-US-AriaNeural'>
        <prosody rate="slow">Hello</prosody>
        <break time="500ms"/>
        <prosody rate="fast">world!</prosody>
    </voice>
</speak>
"""
audio = await synthesize(ssml=ssml, output="styled.mp3")
```

## Popular voices

| Voice | Locale | Gender |
|---|---|---|
| `en-US-AriaNeural` | English (US) | Female |
| `en-US-GuyNeural` | English (US) | Male |
| `en-GB-SoniaNeural` | English (UK) | Female |
| `zh-CN-XiaoxiaoNeural` | Chinese (CN) | Female |
| `zh-CN-YunxiNeural` | Chinese (CN) | Male |
| `ja-JP-NanamiNeural` | Japanese | Female |
| `ko-KR-SunHiNeural` | Korean | Female |

Run `python -m edge_tts_minimal voices` for the full catalogue.

## Disclaimer

This project is for educational purposes. The Edge TTS service is a public endpoint used by Microsoft Edge browser — this library does not circumvent any authentication or encryption. Use responsibly and respect Microsoft's terms of service.

## License

MIT
