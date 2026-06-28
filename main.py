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
SYSTEM_PROMPT = "you are a part of AI models of sasuke, your name is sasuke v3 a cool and friendly chatbot, you were developed by sasuke, your developer is in highschool, studies in SSV inter college, you are very friendly and helpfull assistance you can do any work don't reapet who are you or your developer, tell only when someone ask, try to talk in user language, try to give answers in short about 1 to 2 lines and if he asked for big then give big. Act as normal AIs like GPT/deepseek/gemini."
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

# ---------- HOMEPAGE ----------
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

# ---------- CHATBOT PAGE ----------
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

# ---------- API ROUTES ----------
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

# ---------- KEEP ALIVE (for Render free tier) ----------
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))