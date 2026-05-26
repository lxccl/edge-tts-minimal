# Edge TTS Minimal

Free, unlimited text-to-speech via Microsoft Edge's TTS service. No API key, no quota, no browser required.

## How it works

This library mimics the WebSocket protocol that Microsoft Edge browser uses for its "Read Aloud" feature. Microsoft provides the service as a free consumer offering — this project connects to the same public endpoint.

| Feature | Details |
|---|---|
| Voices | 322 neural voices across 100+ locales |
| Formats | MP3 (24 kHz, 48 kbps) |
| Auth | No API key — uses Edge's public trust token + dynamic DRM token |
| Dependencies | Python 3.10+, `aiohttp`, `certifi` |

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
# 直接合成（默认英文女声）
edge-tts-minimal "Hello world"

# 从文件读取
edge-tts-minimal -f input.txt

# 指定发音人和输出
edge-tts-minimal "你好世界" -v zh-CN-XiaoxiaoNeural -o output.mp3

# 列出 322 位发音人
edge-tts-minimal voices
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
| `en-US-GuyNeural` | English (US) | Male |
| `en-GB-SoniaNeural` | English (UK) | Female |
| `ja-JP-NanamiNeural` | Japanese | Female |
| `ko-KR-SunHiNeural` | Korean | Female |

Run `python -m edge_tts_minimal voices` for the full catalogue.

## Disclaimer

This project is for educational purposes. The Edge TTS service is a public endpoint used by Microsoft Edge browser — this library does not circumvent any authentication or encryption. Use responsibly and respect Microsoft's terms of service.

## License

MIT
