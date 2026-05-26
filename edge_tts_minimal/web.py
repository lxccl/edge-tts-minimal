"""Web UI for Edge TTS — run with: edge-tts-minimal web"""

import base64

import aiohttp
from aiohttp import web

from .client import list_voices, synthesize

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Edge TTS</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body {
    font:14px/1.6 -apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;
    background:#0d1117; color:#c9d1d9;
    max-width:720px; margin:40px auto; padding:0 16px;
  }
  h1 { font-size:20px; margin-bottom:8px; color:#58a6ff; }
  .sub { color:#8b949e; margin-bottom:24px; font-size:13px; }
  label { display:block; margin:16px 0 4px; font-weight:600; }
  textarea {
    width:100%; height:160px; resize:vertical;
    background:#161b22; color:#c9d1d9; border:1px solid #30363d;
    border-radius:6px; padding:12px; font:inherit;
  }
  textarea:focus, select:focus {
    outline:none; border-color:#58a6ff; box-shadow:0 0 0 3px rgba(88,166,255,.15);
  }
  .row { display:flex; gap:12px; }
  .row > * { flex:1; }
  select, input {
    width:100%; background:#161b22; color:#c9d1d9;
    border:1px solid #30363d; border-radius:6px;
    padding:8px 12px; font:inherit;
  }
  button {
    margin-top:20px; padding:10px 24px;
    background:#238636; color:#fff; border:none; border-radius:6px;
    font-size:15px; cursor:pointer; width:100%;
  }
  button:hover { background:#2ea043; }
  button:disabled { background:#21262d; color:#484f58; cursor:default; }
  #status { margin-top:12px; font-size:13px; color:#8b949e; min-height:20px; }
  audio { width:100%; margin-top:12px; }
  .hidden { display:none; }
  #file-name { font-size:12px; color:#8b949e; margin-left:8px; }
  input[type="file"] { display:none; }
  .file-btn {
    display:inline-block; padding:6px 14px; margin-top:6px;
    background:#21262d; border:1px solid #30363d; border-radius:6px;
    cursor:pointer; font-size:13px;
  }
  .file-btn:hover { background:#30363d; }
</style>
</head>
<body>

<h1>Edge TTS</h1>
<div class="sub">Free text-to-speech, no API key needed &mdash; <span id="voice-count">loading voices...</span></div>

<label for="text">Text</label>
<textarea id="text" placeholder="Type or paste text here..."></textarea>
<label class="file-btn" for="file-upload" onclick="">Upload file</label>
<input type="file" id="file-upload" accept=".txt,.md,.html,.json,.csv">
<span id="file-name"></span>

<label for="voice">Voice</label>
<select id="voice"></select>

<button id="btn" onclick="speak()">Synthesize</button>
<div id="status"></div>
<audio id="player" class="hidden" controls></audio>

<script>
const $ = id => document.getElementById(id);
let voices = [];

async function init() {
  const res = await fetch('/api/voices');
  voices = await res.json();
  $('voice-count').textContent = voices.length + ' voices available';
  const sel = $('voice');
  voices.forEach(v => {
    const opt = document.createElement('option');
    // default to en-US-AriaNeural
    if (v.ShortName === 'en-US-AriaNeural') opt.selected = true;
    opt.value = v.ShortName;
    opt.textContent = `${v.ShortName} (${v.Locale} ${v.Gender})`;
    sel.appendChild(opt);
  });
}

$('file-upload').addEventListener('change', async e => {
  const f = e.target.files[0];
  if (!f) return;
  $('file-name').textContent = f.name;
  $('text').value = await f.text();
});

async function speak() {
  const text = $('text').value.trim();
  if (!text) { $('status').textContent = 'Please enter some text.'; return; }

  const btn = $('btn');
  btn.disabled = true;
  btn.textContent = 'Synthesizing...';
  $('status').textContent = '';

  try {
    const res = await fetch('/api/synthesize', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ text, voice: $('voice').value }),
    });
    if (!res.ok) {
      const err = await res.json();
      $('status').textContent = 'Error: ' + (err.detail || res.statusText);
      return;
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const player = $('player');
    player.src = url;
    player.classList.remove('hidden');
    player.play();
    $('status').textContent = `Done — ${(blob.size/1024).toFixed(1)} KB`;
  } catch(e) {
    $('status').textContent = 'Network error: ' + e.message;
  } finally {
    btn.disabled = false;
    btn.textContent = 'Synthesize';
  }
}

init();
</script>
</body>
</html>"""


async def api_list_voices(_request: web.Request) -> web.Response:
    voices = await list_voices()
    return web.json_response(voices)


async def api_synthesize(request: web.Request) -> web.Response:
    try:
        body = await request.json()
    except Exception:
        raise web.HTTPBadRequest(text="Invalid JSON")

    text = body.get("text", "").strip()
    voice = body.get("voice", "en-US-AriaNeural")

    if not text:
        raise web.HTTPBadRequest(text="Text is required")

    try:
        audio = await synthesize(text=text, voice=voice)
    except Exception as e:
        raise web.HTTPInternalServerError(text=str(e))

    return web.Response(body=audio, content_type="audio/mpeg")


async def index(_request: web.Request) -> web.Response:
    return web.Response(body=HTML, content_type="text/html")


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/api/voices", api_list_voices)
    app.router.add_post("/api/synthesize", api_synthesize)
    return app


def run_server(port: int = 8100) -> None:
    import asyncio
    app = create_app()
    print(f"Edge TTS Web UI → http://127.0.0.1:{port}")
    try:
        web.run_app(app, host="127.0.0.1", port=port)
    except OSError as e:
        if "10048" in str(e) or "address already in use" in str(e).lower():
            print(f"Port {port} is already in use.", file=__import__("sys").stderr)
            print(f"Try: edge-tts-minimal web -p {port + 1}", file=__import__("sys").stderr)
        else:
            raise
