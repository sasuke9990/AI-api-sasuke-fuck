import re, os, time, secrets, asyncio, random
from collections import defaultdict
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import httpx

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ---------- CONFIG ----------
SYSTEM_PROMPT = "you are a part of AI models of sasuke, your name is sasuke v3 a cool and friendly chatbot, you were developed by sasuke, your developer is in highschool, studies in SSV inter college, you are very friendly and helpfull assistance you can do any work. try to talk in user language, give just medium lenth of resposne... if he asked for big then give big. Act as normal AIs like GPT/deepseek/gemini."
EXTERNAL_API = "https://felix-rdx-unlimited-free-apis.vercel.app/api/v1/api/deepseek-v3"

VALID_KEYS = {
    "sk-sasuke-a1b2c", "sk-sasuke-d3e4f", "sk-sasuke-g5h6i",
    "sk-sasuke-j7k8l", "sk-sasuke-m9n0o", "sk-sasuke-p1q2r",
    "sk-sasuke-s3t4u", "sk-sasuke-v5w6x", "sk-sasuke-y7z8a",
    "sk-sasuke-b9c0d", "sk-sasuke-e1f2g", "sk-sasuke-h3i4j",
    "sk-sasuke-k5l6m", "sk-sasuke-n7o8p", "sk-sasuke-q9r0s",
    "sk-sasuke-t1u2v", "sk-sasuke-w3x4y", "sk-sasuke-z5a6b",
    "sk-sasuke-c7d8e", "sk-sasuke-f9g0h", "sk-sasuke-i1j2k",
    "sk-sasuke-l3m4n", "sk-sasuke-o5p6q", "sk-sasuke-r7s8t",
    "sk-sasuke-u9v0w",
}

# ---------- RATE LIMITER ----------
class RateLimiter:
    def __init__(self):
        self.minute_buckets = defaultdict(list)
        self.daily_counts = {}

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        today = datetime.utcnow().strftime("%Y-%m-%d")
        bucket = self.minute_buckets[key]
        bucket = [t for t in bucket if now - t < 60]
        if len(bucket) >= 6:
            return False
        bucket.append(now)
        self.minute_buckets[key] = bucket

        if key in self.daily_counts:
            last_date, count = self.daily_counts[key]
            if last_date == today:
                if count >= 200:
                    return False
                self.daily_counts[key] = (today, count + 1)
            else:
                self.daily_counts[key] = (today, 1)
        else:
            self.daily_counts[key] = (today, 1)
        return True

rate_limiter = RateLimiter()

def clean_response(raw: str) -> str:
    cleaned = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
    cleaned = cleaned.replace("<think>", "").replace("</think>", "")
    return cleaned.strip()

# ---------- HOMEPAGE (unchanged) ----------
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sasuke API</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #fafafa;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 1rem;
        }
        .card {
            background: #fff;
            border: 1px solid #dbdbdb;
            border-radius: 12px;
            padding: 2rem;
            width: 100%;
            max-width: 450px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        }
        .logo {
            text-align: center;
            margin-bottom: 1.5rem;
        }
        .logo h1 {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .btn {
            display: block;
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            margin: 1rem 0;
            transition: 0.2s;
            text-align: center;
            text-decoration: none;
        }
        .btn-gradient {
            background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
            color: #fff;
        }
        .btn-outline {
            background: #fff;
            color: #262626;
            border: 1px solid #dbdbdb;
        }
        .btn-outline:hover { background: #f5f5f5; }
        .key-box {
            background: #f9f9f9;
            border: 1px solid #dbdbdb;
            border-radius: 8px;
            padding: 0.8rem;
            font-family: monospace;
            font-size: 0.9rem;
            color: #262626;
            margin: 1rem 0;
            word-break: break-all;
            display: none;
        }
        .key-label {
            font-size: 0.8rem;
            color: #8e8e8e;
            margin-bottom: 0.5rem;
        }
        .endpoint {
            background: #f9f9f9;
            border: 1px solid #dbdbdb;
            border-radius: 8px;
            padding: 0.8rem;
            font-size: 0.8rem;
            word-break: break-all;
            color: #262626;
            margin: 1rem 0;
            display: none;
        }
        .code-tabs {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
        }
        .code-tab {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            border: none;
            background: #efefef;
            color: #262626;
            cursor: pointer;
        }
        .code-tab.active {
            background: #262626;
            color: #fff;
        }
        pre {
            background: #f5f5f5;
            padding: 1rem;
            border-radius: 8px;
            font-size: 0.8rem;
            overflow-x: auto;
            display: none;
            margin: 0;
        }
        pre.active { display: block; }
        .copy-btn {
            float: right;
            background: #efefef;
            border: none;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.7rem;
            cursor: pointer;
            margin-top: -0.3rem;
        }
        .loading {
            display: inline-block;
            width: 18px;
            height: 18px;
            border: 2px solid #dbdbdb;
            border-top-color: #262626;
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
            vertical-align: middle;
            margin-left: 8px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        hr { border: 0.5px solid #dbdbdb; margin: 1.5rem 0; }
        .subtitle { color: #8e8e8e; font-size: 0.9rem; text-align: center; margin-bottom: 1rem; }
        .footer { text-align: center; font-size: 0.8rem; color: #8e8e8e; margin-top: 1.5rem; }
        .nav-links { display: flex; gap: 1rem; justify-content: center; margin: 0.5rem 0; }
        .nav-links a { color: #0095f6; text-decoration: none; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="card">
        <div class="logo">
            <h1>Sasuke API</h1>
            <p class="subtitle">Free AI for everyone.</p>
        </div>

        <!-- GET API KEY -->
        <button class="btn btn-gradient" id="getKeyBtn" onclick="getKey()">Get Free API Key</button>
        <div id="loadingArea" style="text-align: center; display: none; margin: 1rem 0;">
            <span style="color: #8e8e8e;">Generating…</span> <span class="loading"></span>
        </div>
        <div class="key-box" id="keyBox">
            <div class="key-label">Your API Key:</div>
            <span id="keyText"></span>
        </div>
        <div class="endpoint" id="endpointBox">
            <strong>Try it:</strong><br>
            <span id="endpointUrl"></span>
        </div>

        <a href="/chat" class="btn btn-outline" style="margin-top: 0;">💬 Open Chatbot</a>
        <a href="/gallery" class="btn btn-outline">🖼️ Image Gallery</a>

        <hr>

        <!-- HOW TO USE -->
        <h3 style="font-size: 1rem; margin-bottom: 0.5rem;">How to use</h3>
        <div class="code-tabs">
            <button class="code-tab active" onclick="switchTab('python')">Python</button>
            <button class="code-tab" onclick="switchTab('js')">JavaScript</button>
            <button class="code-tab" onclick="switchTab('curl')">cURL</button>
        </div>

        <pre id="python" class="active"><code>import requests

url = "https://your-app.onrender.com/v1/chat"
params = {"key": "YOUR_KEY", "prompt": "Hello"}
r = requests.get(url, params=params)
print(r.json()["response"])</code>
        <button class="copy-btn" onclick="copyCode('python')">Copy</button></pre>

        <pre id="js"><code>const url = "https://your-app.onrender.com/v1/chat";
const params = new URLSearchParams({key:"YOUR_KEY", prompt:"Hello"});
fetch(url+"?"+params)
  .then(r=>r.json())
  .then(d=>console.log(d.response));</code>
        <button class="copy-btn" onclick="copyCode('js')">Copy</button></pre>

        <pre id="curl"><code>curl "https://your-app.onrender.com/v1/chat?key=YOUR_KEY&prompt=Hello"</code>
        <button class="copy-btn" onclick="copyCode('curl')">Copy</button></pre>

        <div class="footer">
            ~ stop searching, start building. sasuke ~
        </div>
    </div>

    <script>
        const keyPool = [
            "sk-sasuke-a1b2c","sk-sasuke-d3e4f","sk-sasuke-g5h6i","sk-sasuke-j7k8l","sk-sasuke-m9n0o",
            "sk-sasuke-p1q2r","sk-sasuke-s3t4u","sk-sasuke-v5w6x","sk-sasuke-y7z8a","sk-sasuke-b9c0d",
            "sk-sasuke-e1f2g","sk-sasuke-h3i4j","sk-sasuke-k5l6m","sk-sasuke-n7o8p","sk-sasuke-q9r0s",
            "sk-sasuke-t1u2v","sk-sasuke-w3x4y","sk-sasuke-z5a6b","sk-sasuke-c7d8e","sk-sasuke-f9g0h",
            "sk-sasuke-i1j2k","sk-sasuke-l3m4n","sk-sasuke-o5p6q","sk-sasuke-r7s8t","sk-sasuke-u9v0w"
        ];
        let used = [];

        async function getKey() {
            const btn = document.getElementById("getKeyBtn");
            const load = document.getElementById("loadingArea");
            btn.style.display = "none";
            load.style.display = "block";

            await new Promise(r => setTimeout(r, 1500 + Math.random()*1500));

            let key;
            do { key = keyPool[Math.floor(Math.random()*keyPool.length)]; } while (used.includes(key));
            used.push(key);

            document.getElementById("keyText").innerText = key;
            document.getElementById("keyBox").style.display = "block";

            const base = window.location.origin;
            const url = base + "/v1/chat?key=" + key + "&prompt=Hello";
            document.getElementById("endpointUrl").innerText = url;
            document.getElementById("endpointBox").style.display = "block";

            load.style.display = "none";
            btn.style.display = "block";
            btn.innerText = "Generate Another Key";
        }

        function switchTab(lang) {
            document.querySelectorAll('.code-tab').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('pre').forEach(p => p.classList.remove('active'));
            document.getElementById(lang).classList.add('active');
            event.target.classList.add('active');
        }

        function copyCode(lang) {
            const code = document.querySelector(`#${lang} code`).innerText;
            navigator.clipboard.writeText(code).then(() => {
                const btn = document.querySelector(`#${lang} .copy-btn`);
                btn.textContent = "Copied!";
                setTimeout(() => btn.textContent = "Copy", 1500);
            });
        }
    </script>
</body>
</html>
"""

# ---------- CHATBOT PAGE (unchanged) ----------
@app.get("/chat", response_class=HTMLResponse)
async def chat():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sasuke AI · Chat</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #fafafa;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .phone {
            width: 100%;
            max-width: 420px;
            height: 95vh;
            background: #fff;
            border-radius: 24px;
            border: 1px solid #dbdbdb;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }
        .header {
            padding: 1rem;
            border-bottom: 1px solid #dbdbdb;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: #fff;
        }
        .back { text-decoration: none; color: #262626; font-size: 1.2rem; }
        .title { font-weight: 600; font-size: 1rem; }
        .online { width: 8px; height: 8px; background: #78de45; border-radius: 50%; margin-left: auto; }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        .bubble {
            max-width: 75%;
            padding: 0.7rem 1rem;
            border-radius: 18px;
            font-size: 0.9rem;
            line-height: 1.4;
            word-wrap: break-word;
        }
        .user {
            align-self: flex-end;
            background: #efefef;
            color: #262626;
        }
        .ai {
            align-self: flex-start;
            background: #fff;
            border: 1px solid #dbdbdb;
        }
        .typing {
            align-self: flex-start;
            background: #fff;
            border: 1px solid #dbdbdb;
            border-radius: 18px;
            padding: 0.7rem 1rem;
            font-size: 0.9rem;
            color: #8e8e8e;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .dot { width: 6px; height: 6px; background: #8e8e8e; border-radius: 50%; animation: bounce 1.4s infinite; }
        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-4px); }
        }
        .input-area {
            display: flex;
            padding: 0.8rem;
            border-top: 1px solid #dbdbdb;
            background: #fff;
        }
        .input-area input {
            flex: 1;
            border: 1px solid #dbdbdb;
            border-radius: 20px;
            padding: 0.6rem 1rem;
            font-size: 0.9rem;
            outline: none;
        }
        .input-area button {
            background: #0095f6;
            color: #fff;
            border: none;
            border-radius: 20px;
            padding: 0.6rem 1.2rem;
            margin-left: 0.5rem;
            font-weight: 600;
            cursor: pointer;
        }
        .input-area button:disabled { opacity: 0.5; }
        .empty { text-align: center; color: #8e8e8e; margin-top: 2rem; }
    </style>
</head>
<body>
    <div class="phone">
        <div class="header">
            <a href="/" class="back">←</a>
            <span class="title">Sasuke AI</span>
            <span class="online"></span>
        </div>
        <div class="messages" id="msgBox">
            <div class="empty">Send a message to start.</div>
        </div>
        <div class="input-area">
            <input type="text" id="userMsg" placeholder="Message..." onkeydown="if(event.key==='Enter')send()">
            <button id="sendBtn" onclick="send()">Send</button>
        </div>
    </div>
    <script>
        const API_KEY = "sk-sasuke-a1b2c"; // default
        const box = document.getElementById("msgBox");
        const input = document.getElementById("userMsg");
        const sendBtn = document.getElementById("sendBtn");

        function addMsg(role, text) {
            const d = document.querySelector(".empty");
            if(d) d.remove();
            const div = document.createElement("div");
            div.className = "bubble " + role;
            div.innerText = text;
            box.appendChild(div);
            box.scrollTop = box.scrollHeight;
        }

        async function send() {
            const msg = input.value.trim();
            if(!msg) return;
            addMsg("user", msg);
            input.value = "";
            sendBtn.disabled = true;

            const typing = document.createElement("div");
            typing.className = "typing";
            typing.innerHTML = '<span>typing</span><span class="dot"></span><span class="dot"></span><span class="dot"></span>';
            box.appendChild(typing);
            box.scrollTop = box.scrollHeight;

            try {
                const url = `/v1/chat?key=${API_KEY}&prompt=${encodeURIComponent(msg)}`;
                const res = await fetch(url);
                const data = await res.json();
                typing.remove();
                addMsg("ai", data.response || "No response");
            } catch(e) {
                typing.remove();
                addMsg("ai", "Error: " + e.message);
            }
            sendBtn.disabled = false;
            input.focus();
        }
    </script>
</body>
</html>
"""

# ---------- AI CHAT ENDPOINT (unchanged) ----------
@app.get("/v1/chat")
async def chat_endpoint(key: str = Query(...), prompt: str = Query(...)):
    if key not in VALID_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    if not rate_limiter.is_allowed(key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. 6/min, 200/day.")

    full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {prompt}\nAssistant:"
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(EXTERNAL_API, params={"q": full_prompt})
            resp.raise_for_status()
            data = resp.json()
            raw = data.get("response", resp.text)
        except:
            raw = "Service temporarily unavailable. Please retry."

    cleaned = clean_response(str(raw))
    return JSONResponse({
        "status": 200,
        "model": "sasuke-v3",
        "developer": "Sasuke",
        "response": cleaned
    })

@app.get("/health")
async def health():
    return {"status": "ok"}

# ---------- KEEP ALIVE (unchanged) ----------
@app.on_event("startup")
async def startup():
    async def keep_alive():
        await asyncio.sleep(60)
        while True:
            try:
                async with httpx.AsyncClient() as client:
                    url = os.environ.get("RENDER_EXTERNAL_URL")
                    if url:
                        await client.get(f"{url}/health", timeout=10)
            except:
                pass
            await asyncio.sleep(540)
    asyncio.create_task(keep_alive())

# =============================================================================
# NEW: WAIFU & DOG GALLERY (added without touching AI code)
# =============================================================================

# ---------- WAIFU API CONFIG ----------
WAIFU_KEY = "dFBC090Y76J9kEkWsSrmJM5rAwwSP0lhSybgXXGDRVs"
WAIFU_BASE = "https://api.waifu.im/images"

# ---------- WAIFU ENDPOINT ----------
@app.get("/api/waifu")
async def waifu_images(tags: str = "waifu", nsfw: bool = False, limit: int = 10):
    """
    Fetch waifu images from waifu.im.
    Query params:
      - tags: comma-separated tags (default: waifu)
      - nsfw: true/false (default: false)
      - limit: max images to return (default: 10, max: 50)
    """
    # Validate limit
    try:
        limit = int(limit)
        if limit > 50:
            limit = 50
    except:
        limit = 10

    url = f"{WAIFU_BASE}?included_tags={tags}&is_nsfw={nsfw}"
    headers = {"X-Api-Key": WAIFU_KEY}

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Waifu API error: {str(e)}")

    # Extract and limit images
    items = data.get("items", [])[:limit]
    total = data.get("totalCount", 0)

    # Format response
    formatted = []
    for img in items:
        formatted.append({
            "id": img.get("id"),
            "url": img.get("url"),
            "width": img.get("width"),
            "height": img.get("height"),
            "is_nsfw": img.get("isNsfw", False),
            "tags": [t.get("name") for t in img.get("tags", [])],
            "dominant_color": img.get("dominantColor"),
            "source": img.get("source")
        })

    return {
        "success": True,
        "source": "waifu.im",
        "total_available": total,
        "total_returned": len(formatted),
        "tags": tags,
        "nsfw": nsfw,
        "images": formatted,
        "raw": data  # full raw response for debugging
    }

# ---------- DOG API ENDPOINT ----------
DOG_BASE = "https://dog.ceo/api"

@app.get("/api/dog")
async def dog_images(breed: str = None, count: int = 1):
    """
    Fetch dog images from dog.ceo.
      - If breed is provided, get a random image of that breed.
      - count: number of random images (max 10)
    """
    try:
        count = int(count)
        if count > 10:
            count = 10
    except:
        count = 1

    if breed:
        url = f"{DOG_BASE}/breed/{breed}/images/random/{count}"
    else:
        url = f"{DOG_BASE}/breeds/image/random/{count}"

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Dog API error: {str(e)}")

    if data.get("status") != "success":
        raise HTTPException(status_code=404, detail="Breed not found or API error")

    images = data.get("message", [])
    if isinstance(images, str):
        images = [images]

    return {
        "success": True,
        "source": "dog.ceo",
        "breed": breed or "random",
        "count": len(images),
        "images": images,
        "raw": data
    }

# ---------- GALLERY PAGE ----------
@app.get("/gallery", response_class=HTMLResponse)
async def gallery():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Gallery · Waifu & Dog</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f0f0f;
            color: #f0f0f0;
            padding: 1.5rem;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 2rem;
            border-bottom: 1px solid #2a2a2a;
            padding-bottom: 1rem;
        }
        header h1 { color: #ff6b35; }
        .back-btn {
            background: #2a2a2a;
            color: #fff;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            text-decoration: none;
            font-size: 0.9rem;
        }
        .section {
            margin-bottom: 2rem;
        }
        .section h2 {
            font-size: 1.2rem;
            color: #aaa;
            margin-bottom: 0.8rem;
            border-left: 3px solid #ff6b35;
            padding-left: 0.8rem;
        }
        .btn-group {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
        }
        .btn-group button {
            background: #1a1a1a;
            border: 1px solid #333;
            color: #ccc;
            padding: 0.4rem 1rem;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: 0.2s;
        }
        .btn-group button:hover {
            background: #2a2a2a;
            border-color: #ff6b35;
        }
        .btn-group button.active {
            background: #ff6b35;
            color: #fff;
            border-color: #ff6b35;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        .grid .card {
            background: #1a1a1a;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #2a2a2a;
            transition: transform 0.2s;
        }
        .grid .card:hover {
            transform: scale(1.02);
            border-color: #ff6b35;
        }
        .grid .card img {
            width: 100%;
            aspect-ratio: 1 / 1;
            object-fit: cover;
            display: block;
        }
        .grid .card .info {
            padding: 0.4rem 0.6rem;
            font-size: 0.7rem;
            color: #888;
            text-overflow: ellipsis;
            overflow: hidden;
            white-space: nowrap;
        }
        .json-output {
            background: #111;
            border: 1px solid #2a2a2a;
            border-radius: 8px;
            padding: 0.8rem;
            font-family: monospace;
            font-size: 0.75rem;
            overflow-x: auto;
            white-space: pre-wrap;
            max-height: 300px;
            overflow-y: auto;
            margin-top: 1.5rem;
            color: #ccc;
        }
        .json-output .key { color: #ff6b35; }
        .json-output .string { color: #6f6; }
        .json-output .number { color: #69f; }
        .json-output .boolean { color: #f6f; }
        .status {
            padding: 0.5rem 1rem;
            background: #1a1a1a;
            border-radius: 6px;
            margin: 0.5rem 0;
            font-size: 0.9rem;
            color: #888;
        }
        .status.loading { color: #ffa500; }
        .status.success { color: #6f6; }
        .status.error { color: #f66; }
        .flex-row { display: flex; flex-wrap: wrap; gap: 1rem; align-items: center; }
        .limit-input {
            background: #111;
            border: 1px solid #333;
            color: #fff;
            padding: 0.3rem 0.6rem;
            border-radius: 4px;
            width: 60px;
        }
        .nsfw-toggle {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #aaa;
            font-size: 0.9rem;
        }
        .nsfw-toggle input[type="checkbox"] {
            accent-color: #ff6b35;
            width: 18px;
            height: 18px;
        }
        @media (max-width: 600px) {
            .grid { grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🖼️ Image Gallery</h1>
            <a href="/" class="back-btn">← Back</a>
        </header>

        <!-- WAIFU SECTION -->
        <div class="section">
            <h2>✨ Waifu (SFW)</h2>
            <div class="btn-group" id="waifuSfwBtns">
                <button class="active" data-tags="waifu">Waifu</button>
                <button data-tags="maid">Maid</button>
                <button data-tags="uniform">Uniform</button>
                <button data-tags="selfies">Selfies</button>
                <button data-tags="rem">Rem</button>
                <button data-tags="nami">Nami</button>
                <button data-tags="marin-kitagawa">Marin</button>
                <button data-tags="mori-calliope">Mori</button>
                <button data-tags="raiden-shogun">Raiden</button>
                <button data-tags="kamisato-ayaka">Ayaka</button>
                <button data-tags="genshin-impact">Genshin</button>
                <button data-tags="one-piece">One Piece</button>
            </div>
            <div class="btn-group" id="waifuNsfwBtns">
                <span style="color:#888;margin-right:0.5rem;">NSFW:</span>
                <button data-tags="ero">Ero</button>
                <button data-tags="hentai">Hentai</button>
                <button data-tags="ecchi">Ecchi</button>
                <button data-tags="ass">Ass</button>
                <button data-tags="oppai">Oppai</button>
                <button data-tags="paizuri">Paizuri</button>
                <button data-tags="oral">Oral</button>
                <button data-tags="milf">MILF</button>
            </div>
            <div class="flex-row">
                <div class="nsfw-toggle">
                    <input type="checkbox" id="waifuNsfwCheck" />
                    <label for="waifuNsfwCheck">NSFW enabled</label>
                </div>
                <label style="color:#888;font-size:0.85rem;">Limit:
                    <input type="number" id="waifuLimit" value="10" min="1" max="50" class="limit-input" />
                </label>
                <button id="waifuFetchBtn" style="background:#ff6b35;border:none;color:#fff;padding:0.3rem 1.2rem;border-radius:4px;cursor:pointer;">Fetch</button>
            </div>
            <div class="status" id="waifuStatus">Click Fetch to load images</div>
            <div class="grid" id="waifuGrid"></div>
        </div>

        <!-- DOG SECTION -->
        <div class="section">
            <h2>🐕 Dog Breeds</h2>
            <div class="btn-group" id="dogBtns">
                <button class="active" data-breed="">Random</button>
                <button data-breed="husky">Husky</button>
                <button data-breed="pug">Pug</button>
                <button data-breed="labrador">Labrador</button>
                <button data-breed="germanshepherd">German Shepherd</button>
                <button data-breed="bulldog">Bulldog</button>
                <button data-breed="boxer">Boxer</button>
                <button data-breed="chihuahua">Chihuahua</button>
                <button data-breed="pomeranian">Pomeranian</button>
                <button data-breed="corgi">Corgi</button>
                <button data-breed="dachshund">Dachshund</button>
                <button data-breed="dalmatian">Dalmatian</button>
                <button data-breed="rottweiler">Rottweiler</button>
            </div>
            <div class="flex-row">
                <label style="color:#888;font-size:0.85rem;">Count:
                    <input type="number" id="dogCount" value="6" min="1" max="10" class="limit-input" />
                </label>
                <button id="dogFetchBtn" style="background:#ff6b35;border:none;color:#fff;padding:0.3rem 1.2rem;border-radius:4px;cursor:pointer;">Fetch</button>
            </div>
            <div class="status" id="dogStatus">Click Fetch to load dog images</div>
            <div class="grid" id="dogGrid"></div>
        </div>

        <!-- JSON OUTPUT -->
        <div class="section">
            <h2>📄 JSON Response</h2>
            <div class="json-output" id="jsonOutput">Click a fetch button to see the raw API response here.</div>
        </div>
    </div>

    <script>
        // ----- Helper: highlight JSON -----
        function syntaxHighlight(json) {
            if (typeof json !== 'string') json = JSON.stringify(json, null, 2);
            json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
                let cls = 'number';
                if (/^"/.test(match)) {
                    if (/:$/.test(match)) {
                        cls = 'key';
                    } else {
                        cls = 'string';
                    }
                } else if (/true|false/.test(match)) {
                    cls = 'boolean';
                } else if (/null/.test(match)) {
                    cls = 'null';
                }
                return '<span class="' + cls + '">' + match + '</span>';
            });
        }

        // ----- Shared fetch function for waifu -----
        async function fetchWaifu() {
            const status = document.getElementById('waifuStatus');
            const grid = document.getElementById('waifuGrid');
            const output = document.getElementById('jsonOutput');

            // Get active SFW tag
            const sfwActive = document.querySelector('#waifuSfwBtns .active');
            let tags = sfwActive ? sfwActive.dataset.tags : 'waifu';

            // Check if any NSFW button is active (we'll override if checked)
            const nsfwActive = document.querySelector('#waifuNsfwBtns .active');
            const nsfwCheck = document.getElementById('waifuNsfwCheck');
            const nsfw = nsfwCheck.checked || false;

            // If NSFW checked and NSFW button active, use its tags
            if (nsfw && nsfwActive) {
                tags = nsfwActive.dataset.tags;
            }

            const limit = document.getElementById('waifuLimit').value || 10;

            status.textContent = '⏳ Loading...';
            status.className = 'status loading';
            grid.innerHTML = '';

            try {
                const url = `/api/waifu?tags=${encodeURIComponent(tags)}&nsfw=${nsfw}&limit=${limit}`;
                const res = await fetch(url);
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const data = await res.json();

                // Display JSON
                output.innerHTML = syntaxHighlight(data);

                if (!data.success || data.images.length === 0) {
                    status.textContent = '❌ No images found for these tags.';
                    status.className = 'status error';
                    return;
                }

                // Render images
                grid.innerHTML = data.images.map(img => `
                    <div class="card">
                        <img src="${img.url}" alt="waifu" loading="lazy" onclick="window.open('${img.url}','_blank')" />
                        <div class="info">${img.tags.join(', ') || 'no tags'}</div>
                    </div>
                `).join('');

                status.textContent = `✅ Loaded ${data.images.length} images (total available: ${data.total_available})`;
                status.className = 'status success';

            } catch (err) {
                status.textContent = '❌ Error: ' + err.message;
                status.className = 'status error';
                output.innerHTML = `<span style="color:#f66;">Error: ${err.message}</span>`;
            }
        }

        // ----- Shared fetch for dog -----
        async function fetchDog() {
            const status = document.getElementById('dogStatus');
            const grid = document.getElementById('dogGrid');
            const output = document.getElementById('jsonOutput');

            const activeBreedBtn = document.querySelector('#dogBtns .active');
            const breed = activeBreedBtn ? activeBreedBtn.dataset.breed : '';
            const count = document.getElementById('dogCount').value || 6;

            status.textContent = '⏳ Loading...';
            status.className = 'status loading';
            grid.innerHTML = '';

            try {
                let url = `/api/dog?count=${count}`;
                if (breed) url += `&breed=${breed}`;
                const res = await fetch(url);
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const data = await res.json();

                output.innerHTML = syntaxHighlight(data);

                if (!data.success || data.images.length === 0) {
                    status.textContent = '❌ No images found for this breed.';
                    status.className = 'status error';
                    return;
                }

                grid.innerHTML = data.images.map(img => `
                    <div class="card">
                        <img src="${img}" alt="dog" loading="lazy" onclick="window.open('${img}','_blank')" />
                        <div class="info">${data.breed || 'dog'}</div>
                    </div>
                `).join('');

                status.textContent = `✅ Loaded ${data.images.length} dog images`;
                status.className = 'status success';

            } catch (err) {
                status.textContent = '❌ Error: ' + err.message;
                status.className = 'status error';
                output.innerHTML = `<span style="color:#f66;">Error: ${err.message}</span>`;
            }
        }

        // ----- Event listeners for buttons -----
        document.querySelectorAll('#waifuSfwBtns button, #waifuNsfwBtns button').forEach(btn => {
            btn.addEventListener('click', function() {
                // Remove active from same group
                const parent = this.parentNode;
                parent.querySelectorAll('button').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
            });
        });

        document.querySelectorAll('#dogBtns button').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('#dogBtns button').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
            });
        });

        document.getElementById('waifuFetchBtn').addEventListener('click', fetchWaifu);
        document.getElementById('dogFetchBtn').addEventListener('click', fetchDog);

        // Auto-load on page open with default waifu and dog
        window.addEventListener('DOMContentLoaded', () => {
            fetchWaifu();
            fetchDog();
        });
    </script>
</body>
</html>
"""

# ---------- KEEP ALIVE (already defined) ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))