"""Edge TTS WebSocket client — mimics Edge browser's Read Aloud feature."""

import hashlib
import secrets
import ssl
import time
import uuid

import aiohttp
import certifi

# Token extracted from Microsoft Edge browser.
_TRUSTED_CLIENT_TOKEN = "6A5AA1D4EAFF4E9FB37E23D68491D6F4"
_CHROMIUM_FULL_VERSION = "143.0.3650.75"
_CHROMIUM_MAJOR_VERSION = _CHROMIUM_FULL_VERSION.split(".", maxsplit=1)[0]
_SEC_MS_GEC_VERSION = f"1-{_CHROMIUM_FULL_VERSION}"

_BASE_URL = (
    "speech.platform.bing.com/consumer/speech/synthesize/readaloud"
)
_WSS_URL = (
    f"wss://{_BASE_URL}/edge/v1"
    f"?TrustedClientToken={_TRUSTED_CLIENT_TOKEN}"
)
_VOICE_LIST_URL = (
    f"https://{_BASE_URL}/voices/list"
    f"?trustedclienttoken={_TRUSTED_CLIENT_TOKEN}"
)

_BASE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        f" (KHTML, like Gecko) Chrome/{_CHROMIUM_MAJOR_VERSION}.0.0.0"
        f" Safari/537.36 Edg/{_CHROMIUM_MAJOR_VERSION}.0.0.0"
    ),
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
}

_WSS_HEADERS = {
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "Origin": "chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold",
    "Sec-WebSocket-Version": "13",
}
_WSS_HEADERS.update(_BASE_HEADERS)

_VOICE_HEADERS = {
    "Authority": "speech.platform.bing.com",
    "Sec-CH-UA": (
        f'" Not;A Brand";v="99", "Microsoft Edge";v="{_CHROMIUM_MAJOR_VERSION}",'
        f' "Chromium";v="{_CHROMIUM_MAJOR_VERSION}"'
    ),
    "Sec-CH-UA-Mobile": "?0",
    "Accept": "*/*",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
}
_VOICE_HEADERS.update(_BASE_HEADERS)

_SSL_CTX = ssl.create_default_context(cafile=certifi.where())

# Windows file time epoch offset (1601-01-01 in Unix seconds).
_WIN_EPOCH = 11644473600


def _generate_sec_ms_gec() -> str:
    """Generate the Sec-MS-GEC token used for DRM verification.

    Based on the current time rounded to the nearest 5-minute window,
    converted to Windows file-time ticks, and SHA-256 hashed with the
    trusted client token.
    """
    ticks = time.time()
    ticks += _WIN_EPOCH
    ticks -= ticks % 300  # round down to 5 min
    ticks *= 1e9 / 100    # convert to 100-ns intervals
    payload = f"{ticks:.0f}{_TRUSTED_CLIENT_TOKEN}"
    return hashlib.sha256(payload.encode("ascii")).hexdigest().upper()


def _generate_muid() -> str:
    """Generate a random MUID for the Cookie header."""
    return secrets.token_hex(16).upper()


def _date_to_string() -> str:
    """JavaScript-style date string (matching Edge's format)."""
    return time.strftime(
        "%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)",
        time.gmtime(),
    )


def _build_wss_url() -> str:
    return (
        f"{_WSS_URL}"
        f"&ConnectionId={uuid.uuid4().hex}"
        f"&Sec-MS-GEC={_generate_sec_ms_gec()}"
        f"&Sec-MS-GEC-Version={_SEC_MS_GEC_VERSION}"
    )


def _get_headers_and_data(data: bytes, header_length: int) -> tuple:
    """Split binary frame into headers dict and body."""
    headers = {}
    for line in data[:header_length].split(b"\r\n"):
        key, value = line.split(b":", 1)
        headers[key] = value
    return headers, data[header_length + 2:]


def _escape_xml(text: str) -> str:
    """Escape text for safe embedding in SSML."""
    return (
        text.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _clean_text(text: str) -> str:
    """Remove control characters the service rejects, then XML-escape."""
    chars = list(text)
    for i, ch in enumerate(chars):
        code = ord(ch)
        if (0 <= code <= 8) or (11 <= code <= 12) or (14 <= code <= 31):
            chars[i] = " "
    return _escape_xml("".join(chars))


def _split_text(text: str, max_bytes: int = 3000) -> list[str]:
    """Split text so each chunk stays within *max_bytes* UTF-8 bytes."""
    chunks: list[str] = []
    while len(text.encode("utf-8")) > max_bytes:
        # find natural split point near max_bytes
        segment = text[:max_bytes + 1]
        split_at = -1
        for sep in ("\n", "。", ".", "，", ",", " "):
            idx = segment.rfind(sep)
            if idx > max_bytes // 2:
                split_at = idx + 1
                break
        if split_at < 0:
            # force-split at byte boundary
            raw = text.encode("utf-8")[:max_bytes]
            split_at = len(raw.decode("utf-8", errors="ignore"))
        chunks.append(text[:split_at].strip())
        text = text[split_at:].strip()
    if text:
        chunks.append(text)
    return chunks


def build_ssml(text: str, voice: str = "en-US-AriaNeural") -> str:
    """Wrap plain text in a minimal SSML document. Text is auto-escaped."""
    return (
        f"<speak version='1.0'"
        f" xmlns='http://www.w3.org/2001/10/synthesis'"
        f" xmlns:mstts='https://www.w3.org/2001/mstts'"
        f" xml:lang='en-US'>"
        f"<voice name='{voice}'>{_escape_xml(text)}</voice>"
        f"</speak>"
    )


async def synthesize(
    text: str | None = None,
    ssml: str | None = None,
    voice: str = "en-US-AriaNeural",
    output: str | None = None,
) -> bytes:
    """Synthesize speech and return MP3 bytes.

    Long *text* is automatically split into chunks, each sent as a
    separate SSML frame in a single WebSocket session.  Raw *ssml* is
    sent as-is (no escaping / chunking).

    Args:
        text:   Plain text to speak (mutually exclusive with *ssml*).
        ssml:   Raw SSML string. When provided, *voice* is ignored.
        voice:  Short name of the neural voice.
        output: Optional file path to write the MP3 to.

    Returns:
        Raw MP3 audio bytes.
    """
    if ssml:
        ssml_chunks = [ssml]
    elif text:
        clean = _clean_text(text)
        ssml_chunks = [build_ssml(chunk, voice) for chunk in _split_text(clean)]
    else:
        raise ValueError("Either 'text' or 'ssml' must be provided.")

    timestamp = _date_to_string()
    headers = dict(_WSS_HEADERS)
    headers["Cookie"] = f"muid={_generate_muid()};"

    audio = b""

    async with aiohttp.ClientSession(
        trust_env=True,
        timeout=aiohttp.ClientTimeout(total=None, sock_connect=10, sock_read=60),
    ) as session, session.ws_connect(
        _build_wss_url(),
        headers=headers,
        compress=15,
        ssl=_SSL_CTX,
    ) as ws:
        # 1. Config (once)
        await ws.send_str(
            f"X-Timestamp:{timestamp}\r\n"
            f"Content-Type:application/json; charset=utf-8\r\n"
            f"Path:speech.config\r\n\r\n"
            f'{{"context":{{"synthesis":{{"audio":{{"metadataoptions":{{'
            f'"sentenceBoundaryEnabled":false,"wordBoundaryEnabled":true}},'
            f'"outputFormat":"audio-24khz-48kbitrate-mono-mp3"}}}}}}}}'
        )

        # 2. Send each SSML chunk, collect audio until turn.end
        for ssml_text in ssml_chunks:
            request_id = uuid.uuid4().hex
            await ws.send_str(
                f"X-RequestId:{request_id}\r\n"
                f"Content-Type:application/ssml+xml\r\n"
                f"X-Timestamp:{timestamp}Z\r\n"
                f"Path:ssml\r\n\r\n"
                f"{ssml_text}"
            )

            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.BINARY:
                    if len(msg.data) < 2:
                        continue
                    header_len = int.from_bytes(msg.data[:2], "big")
                    if header_len > len(msg.data):
                        continue
                    params, data = _get_headers_and_data(msg.data, header_len)
                    if params.get(b"Path") == b"audio":
                        audio += data
                elif msg.type == aiohttp.WSMsgType.TEXT:
                    if b"Path:turn.end" in msg.data.encode():
                        break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    raise RuntimeError(f"WebSocket error: {msg.data}")

    if not audio:
        raise RuntimeError(
            "No audio received. Check your voice name and network connectivity."
        )

    if output:
        with open(output, "wb") as f:
            f.write(audio)

    return audio


async def list_voices() -> list[dict]:
    """Fetch the live voice catalogue from Microsoft.

    Returns a list of dicts with keys like ``ShortName``, ``Locale``,
    ``Gender``, ``FriendlyName``, ``VoiceTag``, etc.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(_VOICE_LIST_URL, headers=_VOICE_HEADERS) as resp:
            return await resp.json()
