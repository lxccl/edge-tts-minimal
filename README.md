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
# 生成语音（默认中文女声）
python -m edge_tts_minimal speak "你好世界"

# 指定发音人和输出文件
python -m edge_tts_minimal speak "你好世界" -v zh-CN-XiaoxiaoNeural -o output.mp3

# 英文
python -m edge_tts_minimal speak "Hello world" -v en-US-AriaNeural

# 列出所有 322 位发音人
python -m edge_tts_minimal voices
```

### Python API

```python
import asyncio
from edge_tts_minimal import synthesize

async def main():
    audio = await synthesize(
        text="你好，这是一个测试。",
        voice="zh-CN-XiaoxiaoNeural",
        output="test.mp3",
    )

asyncio.run(main())
```

### Advanced — raw SSML

```python
ssml = """
<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis'>
    <voice name='zh-CN-XiaoxiaoNeural'>
        <prosody rate="slow">你好</prosody>
        <break time="500ms"/>
        <prosody rate="fast">世界！</prosody>
    </voice>
</speak>
"""
audio = await synthesize(ssml=ssml, output="styled.mp3")
```

## Popular voices

| Voice | Locale | Gender |
|---|---|---|
| `zh-CN-XiaoxiaoNeural` | Chinese (CN) | Female |
| `zh-CN-YunxiNeural` | Chinese (CN) | Male |
| `zh-CN-XiaoyiNeural` | Chinese (CN) | Female |
| `en-US-AriaNeural` | English (US) | Female |
| `en-US-GuyNeural` | English (US) | Male |
| `en-GB-SoniaNeural` | English (UK) | Female |
| `ja-JP-NanamiNeural` | Japanese | Female |
| `ko-KR-SunHiNeural` | Korean | Female |

Run `python -m edge_tts_minimal voices` for the full catalogue.

## Disclaimer

This project is for educational purposes. The Edge TTS service is a public endpoint used by Microsoft Edge browser — this library does not circumvent any authentication or encryption. Use responsibly and respect Microsoft's terms of service.

## License

MIT
