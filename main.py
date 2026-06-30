"""
╔═══════════════════════════════════════════════════════════════════╗
║                    SASUKE WAIFU GALLERY                          ║
║                    100% HUMAN MADE · BRUTALIST                  ║
║                    DEV: SASUKE                                  ║
╚═══════════════════════════════════════════════════════════════════╝
"""

from flask import Flask, request, jsonify, render_template_string
import requests
import random
from datetime import datetime

app = Flask(__name__)

# ============================================================
# CONFIG
# ============================================================
WAIFU_KEY = 'dFBC090Y76J9kEkWsSrmJM5rAwwSP0lhSybgXXGDRVs'
WAIFU_BASE = 'https://api.waifu.im/images'

# ============================================================
# WAIFU TAGS - HAR TYPE KA
# ============================================================
TAGS = {
    'sfw': ['waifu', 'maid', 'uniform', 'selfies', 'rem', 'nami', 
            'marin-kitagawa', 'mori-calliope', 'raiden-shogun', 
            'kamisato-ayaka', 'genshin-impact', 'one-piece'],
    'nsfw': ['ero', 'hentai', 'ecchi', 'ass', 'oppai', 'paizuri', 'oral', 'milf'],
    'special': ['pussy', 'boobs', 'ass', 'tits', 'dick', 'fuck', 'anal', 'blowjob', 
                'cum', 'creampie', 'gangbang', 'lesbian', 'threesome', 'bdsm']
}

# ============================================================
# WAIFU API - FETCH IMAGES
# ============================================================
def fetch_waifu(tags, nsfw=False, limit=20):
    """Fetch images from waifu.im API"""
    url = f"{WAIFU_BASE}?included_tags={tags}&is_nsfw={nsfw}"
    headers = {"X-Api-Key": WAIFU_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None, f"API Error: {response.status_code}"
        
        data = response.json()
        items = data.get('items', [])
        
        # Limit results
        if limit and len(items) > limit:
            items = items[:limit]
        
        # Format images
        formatted = []
        for img in items:
            formatted.append({
                'id': img.get('id'),
                'url': img.get('url'),
                'width': img.get('width'),
                'height': img.get('height'),
                'is_nsfw': img.get('isNsfw', False),
                'tags': [t.get('name') for t in img.get('tags', [])],
                'dominant_color': img.get('dominantColor', '#333'),
                'source': img.get('source', '')
            })
        
        return {
            'images': formatted,
            'total': data.get('totalCount', 0),
            'tags': tags,
            'nsfw': nsfw
        }, None
        
    except Exception as e:
        return None, str(e)

# ============================================================
# ROUTES - HAR TYPE KA
# ============================================================

@app.route('/')
@app.route('/waifu')
def waifu_page():
    """Main waifu gallery page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/waifu')
def waifu_api():
    """API endpoint for waifu images"""
    tags = request.args.get('tags', 'waifu')
    nsfw = request.args.get('nsfw', 'false').lower() == 'true'
    limit = request.args.get('limit', 20)
    
    try:
        limit = int(limit)
        if limit > 50:
            limit = 50
    except:
        limit = 20
    
    data, error = fetch_waifu(tags, nsfw, limit)
    
    if error:
        return jsonify({
            'success': False,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }), 500
    
    return jsonify({
        'success': True,
        'source': 'waifu.im',
        'dev': 'sasuke',
        'data': data,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/waifu/random')
def waifu_random():
    """Get random waifu image"""
    nsfw = request.args.get('nsfw', 'false').lower() == 'true'
    data, error = fetch_waifu('waifu', nsfw, 1)
    
    if error or not data or not data.get('images'):
        return jsonify({
            'success': False,
            'error': 'No images found',
            'dev': 'sasuke'
        }), 404
    
    return jsonify({
        'success': True,
        'dev': 'sasuke',
        'image': data['images'][0],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/waifu/tags')
def waifu_tags():
    """Get all available tags"""
    return jsonify({
        'success': True,
        'dev': 'sasuke',
        'tags': TAGS,
        'timestamp': datetime.now().isoformat()
    })

# ============================================================
# HTML TEMPLATE - PURE HUMAN MADE BRUTALIST
# ============================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WAIFU · SASUKE</title>
    <style>
        /* ============================================================
           BRUTALIST · RAW · HUMAN MADE
           ============================================================ */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: #0a0a0a;
            font-family: 'Courier New', monospace;
            color: #d0d0d0;
            padding: 16px;
            min-height: 100vh;
        }

        .container {
            max-width: 1440px;
            margin: 0 auto;
        }

        /* ----- HEADER — BRUTAL ----- */
        header {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            border-bottom: 4px solid #ff2d2d;
            padding: 0 0 14px 0;
            margin-bottom: 28px;
            flex-wrap: wrap;
            gap: 12px;
        }

        .title h1 {
            font-size: 54px;
            font-weight: 900;
            letter-spacing: -3px;
            color: #ff2d2d;
            text-transform: uppercase;
            line-height: 0.9;
            text-shadow: 6px 6px 0 #0f0f0f;
        }

        .title .sub {
            font-size: 13px;
            color: #555;
            letter-spacing: 5px;
            text-transform: uppercase;
            border-left: 3px solid #ff2d2d;
            padding-left: 14px;
            margin-top: 6px;
        }

        .credit {
            text-align: right;
            font-size: 12px;
            color: #333;
            border: 1px solid #1a1a1a;
            padding: 6px 14px;
            background: #0d0d0d;
            letter-spacing: 1px;
        }

        .credit span {
            color: #ff2d2d;
            font-weight: 700;
            font-size: 14px;
        }

        /* ----- TAG NAV — RAW AS FUCK ----- */
        .tag-nav {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            margin-bottom: 24px;
            padding: 10px 0;
            border-top: 2px solid #111;
            border-bottom: 2px solid #111;
        }

        .tag-btn {
            background: #0f0f0f;
            border: 1px solid #222;
            color: #777;
            padding: 5px 16px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            cursor: pointer;
            transition: 0.15s;
            border-radius: 0;
        }

        .tag-btn:hover {
            background: #1a1a1a;
            color: #fff;
            border-color: #ff2d2d;
        }

        .tag-btn.active {
            background: #ff2d2d;
            color: #fff;
            border-color: #ff2d2d;
        }

        .tag-btn.nsfw-tag {
            border-color: #4a1a1a;
            color: #883333;
        }

        .tag-btn.nsfw-tag:hover {
            border-color: #ff2d2d;
            color: #ff2d2d;
        }

        .tag-btn.nsfw-tag.active {
            background: #2d0a0a;
            color: #ff2d2d;
            border-color: #ff2d2d;
        }

        .tag-divider {
            color: #1a1a1a;
            padding: 0 6px;
            display: flex;
            align-items: center;
            font-size: 18px;
        }

        /* ----- CONTROLS — MINIMAL ----- */
        .controls {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
            margin-bottom: 24px;
        }

        .controls label {
            font-size: 12px;
            color: #555;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .controls select,
        .controls input {
            background: #0f0f0f;
            border: 1px solid #1a1a1a;
            color: #d0d0d0;
            padding: 6px 12px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            border-radius: 0;
        }

        .controls select:focus,
        .controls input:focus {
            border-color: #ff2d2d;
            outline: none;
        }

        .fetch-btn {
            background: #ff2d2d;
            border: none;
            color: #fff;
            padding: 8px 32px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            cursor: pointer;
            transition: 0.15s;
        }

        .fetch-btn:hover {
            background: #cc0000;
            transform: scale(0.98);
        }

        .fetch-btn:disabled {
            opacity: 0.4;
            cursor: not-allowed;
            transform: none;
        }

        .nsfw-toggle {
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            color: #555;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .nsfw-toggle input {
            width: 18px;
            height: 18px;
            accent-color: #ff2d2d;
            cursor: pointer;
        }

        /* ----- STATUS — RAW ----- */
        .status {
            font-size: 13px;
            color: #444;
            padding: 8px 0;
            border-bottom: 1px solid #111;
            margin-bottom: 20px;
            letter-spacing: 0.5px;
        }

        .status .count {
            color: #ff2d2d;
            font-weight: 700;
        }

        .status .error {
            color: #ff2d2d;
        }

        /* ----- IMAGE GRID — BIG ----- */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
            margin-top: 8px;
        }

        .card {
            background: #0d0d0d;
            border: 1px solid #151515;
            overflow: hidden;
            transition: 0.2s;
            cursor: pointer;
            position: relative;
        }

        .card:hover {
            border-color: #ff2d2d;
            transform: translateY(-4px);
        }

        .card img {
            width: 100%;
            aspect-ratio: 3/4;
            object-fit: cover;
            display: block;
            background: #0a0a0a;
        }

        .card .info {
            padding: 8px 12px 10px 12px;
            font-size: 11px;
            color: #555;
            display: flex;
            justify-content: space-between;
            align-items: center;
            letter-spacing: 0.5px;
            background: #0a0a0a;
        }

        .card .info .tags {
            color: #777;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            max-width: 70%;
        }

        .card .info .id {
            color: #2a2a2a;
            font-size: 10px;
        }

        /* ----- LOADING SKELETON ----- */
        .skeleton {
            background: #0d0d0d;
            aspect-ratio: 3/4;
            border: 1px solid #111;
            animation: pulse 1.8s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 0.7; }
        }

        /* ----- MODAL — BIG VIEW ----- */
        .modal {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.95);
            z-index: 999;
            align-items: center;
            justify-content: center;
            padding: 20px;
            cursor: pointer;
        }

        .modal.active {
            display: flex;
        }

        .modal img {
            max-width: 92vw;
            max-height: 92vh;
            object-fit: contain;
            border: 2px solid #1a1a1a;
            cursor: default;
        }

        .modal .close {
            position: fixed;
            top: 20px;
            right: 30px;
            font-size: 40px;
            color: #555;
            cursor: pointer;
            background: none;
            border: none;
            font-family: 'Courier New', monospace;
            transition: 0.2s;
        }

        .modal .close:hover {
            color: #ff2d2d;
            transform: rotate(90deg);
        }

        .modal .modal-info {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            color: #333;
            font-size: 12px;
            letter-spacing: 1px;
            text-align: center;
            pointer-events: none;
        }

        /* ----- FOOTER ----- */
        footer {
            margin-top: 40px;
            padding: 20px 0;
            border-top: 2px solid #111;
            text-align: center;
            font-size: 11px;
            color: #1f1f1f;
            letter-spacing: 2px;
        }

        footer span {
            color: #ff2d2d;
        }

        /* ----- RESPONSIVE ----- */
        @media (max-width: 768px) {
            .title h1 {
                font-size: 34px;
                text-shadow: 4px 4px 0 #0f0f0f;
            }

            .grid {
                grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
                gap: 10px;
            }

            .card img {
                aspect-ratio: 2/3;
            }

            header {
                flex-direction: column;
                align-items: flex-start;
            }

            .credit {
                text-align: left;
                width: 100%;
            }

            .tag-btn {
                font-size: 10px;
                padding: 4px 10px;
            }

            .modal img {
                max-width: 98vw;
                max-height: 80vh;
            }
        }

        @media (max-width: 480px) {
            .grid {
                grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
                gap: 8px;
            }

            .title h1 {
                font-size: 26px;
            }

            .controls {
                flex-direction: column;
                align-items: stretch;
            }

            .fetch-btn {
                padding: 10px;
            }
        }
    </style>
</head>
<body>

    <div class="container">

        <!-- ===== HEADER ===== -->
        <header>
            <div class="title">
                <h1>WAIFU</h1>
                <div class="sub">gallery · sasuke</div>
            </div>
            <div class="credit">
                DEV · <span>SASUKE</span><br>
                <span style="color:#1f1f1f;font-size:9px;">100% HUMAN MADE</span>
            </div>
        </header>

        <!-- ===== TAG NAV ===== -->
        <div class="tag-nav" id="tagNav">
            <!-- SFW Tags -->
            <button class="tag-btn active" data-tag="waifu">waifu</button>
            <button class="tag-btn" data-tag="maid">maid</button>
            <button class="tag-btn" data-tag="uniform">uniform</button>
            <button class="tag-btn" data-tag="selfies">selfies</button>
            <button class="tag-btn" data-tag="rem">rem</button>
            <button class="tag-btn" data-tag="nami">nami</button>
            <button class="tag-btn" data-tag="marin-kitagawa">marin</button>
            <button class="tag-btn" data-tag="mori-calliope">mori</button>
            <button class="tag-btn" data-tag="raiden-shogun">raiden</button>
            <button class="tag-btn" data-tag="kamisato-ayaka">ayaka</button>
            <button class="tag-btn" data-tag="genshin-impact">genshin</button>
            <button class="tag-btn" data-tag="one-piece">one piece</button>

            <span class="tag-divider">|</span>

            <!-- NSFW Tags -->
            <button class="tag-btn nsfw-tag" data-tag="ero">ero</button>
            <button class="tag-btn nsfw-tag" data-tag="hentai">hentai</button>
            <button class="tag-btn nsfw-tag" data-tag="ecchi">ecchi</button>
            <button class="tag-btn nsfw-tag" data-tag="ass">ass</button>
            <button class="tag-btn nsfw-tag" data-tag="oppai">oppai</button>
            <button class="tag-btn nsfw-tag" data-tag="paizuri">paizuri</button>
            <button class="tag-btn nsfw-tag" data-tag="oral">oral</button>
            <button class="tag-btn nsfw-tag" data-tag="milf">milf</button>
        </div>

        <!-- ===== CONTROLS ===== -->
        <div class="controls">
            <label class="nsfw-toggle">
                <input type="checkbox" id="nsfwToggle">
                NSFW
            </label>

            <label>
                LIMIT
                <input type="number" id="limitInput" value="20" min="1" max="50" style="width:60px;">
            </label>

            <button class="fetch-btn" id="fetchBtn">⟳ FETCH</button>
        </div>

        <!-- ===== STATUS ===== -->
        <div class="status" id="status">
            <span class="count">●</span> ready · click fetch or choose a tag
        </div>

        <!-- ===== GRID ===== -->
        <div class="grid" id="grid">
            <!-- Skeleton loaders -->
            <div class="skeleton"></div>
            <div class="skeleton"></div>
            <div class="skeleton"></div>
            <div class="skeleton"></div>
            <div class="skeleton"></div>
            <div class="skeleton"></div>
        </div>

        <!-- ===== FOOTER ===== -->
        <footer>
            <span>✦</span> DEV · SASUKE  <span>✦</span><br>
            <span style="color:#111;font-size:9px;">brutalist · human made · 2026</span>
        </footer>

    </div>

    <!-- ===== MODAL ===== -->
    <div class="modal" id="modal">
        <button class="close" id="modalClose">✕</button>
        <img id="modalImg" src="" alt="">
        <div class="modal-info" id="modalInfo">click anywhere to close</div>
    </div>

    <!-- ============================================================ -->
    <!-- JAVASCRIPT · RAW · HUMAN MADE                               -->
    <!-- ============================================================ -->
    <script>
        // ============================================================
        // CONFIG
        // ============================================================
        const BASE = window.location.origin;

        // ============================================================
        // DOM REFS
        // ============================================================
        const grid = document.getElementById('grid');
        const status = document.getElementById('status');
        const fetchBtn = document.getElementById('fetchBtn');
        const nsfwToggle = document.getElementById('nsfwToggle');
        const limitInput = document.getElementById('limitInput');
        const tagNav = document.getElementById('tagNav');
        const modal = document.getElementById('modal');
        const modalImg = document.getElementById('modalImg');
        const modalClose = document.getElementById('modalClose');
        const modalInfo = document.getElementById('modalInfo');

        let currentTag = 'waifu';
        let isLoading = false;

        // ============================================================
        // FETCH IMAGES
        // ============================================================
        async function fetchImages() {
            if (isLoading) return;
            isLoading = true;
            fetchBtn.disabled = true;

            const tag = currentTag;
            const nsfw = nsfwToggle.checked;
            const limit = parseInt(limitInput.value) || 20;

            status.innerHTML = `<span class="count">⏳</span> loading · ${tag} · nsfw:${nsfw ? 'ON' : 'OFF'}`;

            // Show skeletons
            grid.innerHTML = '';
            for (let i = 0; i < 6; i++) {
                const sk = document.createElement('div');
                sk.className = 'skeleton';
                grid.appendChild(sk);
            }

            try {
                const url = `${BASE}/api/waifu?tags=${encodeURIComponent(tag)}&nsfw=${nsfw}&limit=${limit}`;
                const response = await fetch(url);

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }

                const data = await response.json();

                if (!data.success || !data.data || data.data.images.length === 0) {
                    grid.innerHTML = `
                        <div style="grid-column:1/-1;text-align:center;color:#333;padding:60px 20px;font-size:18px;letter-spacing:2px;">
                            ⚡ NO IMAGES · TRY ANOTHER TAG<br>
                            <span style="font-size:12px;color:#1a1a1a;">dev · sasuke</span>
                        </div>
                    `;
                    status.innerHTML = `<span class="error">✕</span> no images found for "${tag}"`;
                    isLoading = false;
                    fetchBtn.disabled = false;
                    return;
                }

                renderImages(data.data.images);
                status.innerHTML = `<span class="count">●</span> ${data.data.images.length} images · ${data.data.total || '?'} total · ${tag}`;

            } catch (err) {
                grid.innerHTML = `
                    <div style="grid-column:1/-1;text-align:center;color:#ff2d2d;padding:60px 20px;font-size:16px;letter-spacing:1px;">
                        ⚡ ERROR · ${err.message}<br>
                        <span style="font-size:11px;color:#1a1a1a;">check console · dev: sasuke</span>
                    </div>
                `;
                status.innerHTML = `<span class="error">✕</span> ${err.message}`;
                console.error('Fetch error:', err);
            }

            isLoading = false;
            fetchBtn.disabled = false;
        }

        // ============================================================
        // RENDER IMAGES
        // ============================================================
        function renderImages(images) {
            grid.innerHTML = '';

            images.forEach(img => {
                const card = document.createElement('div');
                card.className = 'card';

                const imgEl = document.createElement('img');
                imgEl.src = img.url;
                imgEl.alt = 'waifu';
                imgEl.loading = 'lazy';
                imgEl.onerror = function() {
                    this.style.display = 'none';
                };

                const info = document.createElement('div');
                info.className = 'info';

                const tagsSpan = document.createElement('span');
                tagsSpan.className = 'tags';
                tagsSpan.textContent = img.tags.slice(0, 3).join(', ') || 'no tags';

                const idSpan = document.createElement('span');
                idSpan.className = 'id';
                idSpan.textContent = '#' + (img.id || '?');

                info.appendChild(tagsSpan);
                info.appendChild(idSpan);

                card.appendChild(imgEl);
                card.appendChild(info);

                // Click to open modal
                card.addEventListener('click', () => {
                    modalImg.src = img.url;
                    modalInfo.textContent = `id:${img.id || '?'} · ${img.width||'?'}x${img.height||'?'} · ${img.tags.slice(0,4).join(', ')}`;
                    modal.classList.add('active');
                    document.body.style.overflow = 'hidden';
                });

                grid.appendChild(card);
            });
        }

        // ============================================================
        // MODAL CONTROLS
        // ============================================================
        function closeModal() {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }

        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });

        modalClose.addEventListener('click', closeModal);

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeModal();
        });

        // ============================================================
        // TAG SELECTION
        // ============================================================
        tagNav.addEventListener('click', (e) => {
            const btn = e.target.closest('.tag-btn');
            if (!btn) return;

            // Remove active from all
            tagNav.querySelectorAll('.tag-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            currentTag = btn.dataset.tag;

            // Auto-fetch on tag change
            fetchImages();
        });

        // ============================================================
        // EVENT LISTENERS
        // ============================================================
        fetchBtn.addEventListener('click', fetchImages);

        nsfwToggle.addEventListener('change', fetchImages);

        limitInput.addEventListener('change', fetchImages);

        // ============================================================
        // AUTO-LOAD ON START
        // ============================================================
        window.addEventListener('DOMContentLoaded', () => {
            fetchImages();
        });

        // ============================================================
        // KEYBOARD SHORTCUT: R for refresh
        // ============================================================
        document.addEventListener('keydown', (e) => {
            if (e.key === 'r' && !e.ctrlKey && !e.metaKey) {
                if (!modal.classList.contains('active')) {
                    e.preventDefault();
                    fetchImages();
                }
            }
        });

        console.log('🔥 SASUKE WAIFU GALLERY');
        console.log('📡 DEV: SASUKE');
        console.log('💡 Press "R" to refresh');
        console.log('💡 Click image to enlarge');
    </script>

</body>
</html>
"""

# ============================================================
# RUN SERVER
# ============================================================
if __name__ == '__main__':
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              🔥 SASUKE WAIFU GALLERY 🔥                      ║
║                                                               ║
║              DEV: SASUKE                                      ║
║              100% HUMAN MADE · BRUTALIST                    ║
║                                                               ║
║  http://localhost:5000                                       ║
║  http://localhost:5000/waifu                                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=True)