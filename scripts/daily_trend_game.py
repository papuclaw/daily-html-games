import os, re, json, time, random
from datetime import datetime
import requests
from pytrends.request import TrendReq

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES_DIR = os.path.join(ROOT, 'games')
LIST_PATH = os.path.join(ROOT, 'games-list.md')
INDEX_PATH = os.path.join(ROOT, 'index.html')
ASSETS_DIR = os.path.join(ROOT, 'assets')

headers = {'User-Agent': 'Mozilla/5.0'}

def load_used_titles():
    if not os.path.exists(LIST_PATH):
        return set()
    txt = open(LIST_PATH, 'r', encoding='utf-8').read().lower()
    titles = re.findall(r'—\s*([^\n\(]+)', txt)
    return set([t.strip() for t in titles])

def get_trends():
    topics = []
    # Google Trends Argentina
    try:
        pytrends = TrendReq(hl='es-AR', tz=-180)
        df = pytrends.trending_searches(pn='argentina')
        topics += [str(x) for x in df[0].tolist()[:10]]
    except: pass
    
    # Reddit Popular
    try:
        url = 'https://www.reddit.com/r/popular/hot.json?limit=15'
        data = requests.get(url, headers=headers, timeout=10).json()
        for child in data.get('data', {}).get('children', []):
            topics.append(child.get('data', {}).get('title', ''))
    except: pass
    return topics

def pick_topic(trends, used):
    for t in trends:
        clean_t = t[:40].strip()
        if clean_t.lower() not in used:
            return clean_t
    # Logic fallback: generic but distinct
    fallbacks = ["Neon Surfer", "Void Escape", "Gravity Shift", "Pulse Runner"]
    for f in fallbacks:
        if f.lower() not in used: return f
    return f"Daily Challenge {datetime.utcnow().strftime('%Y%m%d')}"

GAME_TEMPLATE = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no" />
  <title>{title}</title>
  <style>
    html,body{{margin:0;padding:0;width:100%;height:100%;overflow:hidden;background:#050505;color:#fff;font-family:system-ui}}
    #hud{{position:fixed;top:10px;left:10px;z-index:2;font-weight:bold;text-shadow:1px 1px #000}}
    #overlay{{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,.8);z-index:10;text-align:center}}
    .btn{{background:#1f5;color:#000;padding:12px 24px;border-radius:12px;font-weight:900;cursor:pointer;user-select:none;display:inline-block;margin-top:10px}}
    canvas{{display:block;width:100%;height:100%}}
  </style>
</head>
<body>
  <div id="hud">Puntos: <b id="score">0</b> | Record: <b id="best">0</b></div>
  <div id="overlay">
    <div>
      <div style="font-size:28px;margin-bottom:10px"><b>{title}</b></div>
      <div style="opacity:0.8;margin-bottom:10px">Click/Tap para cambiar GRAVEDAD</div>
      <div class="btn" id="startBtn">COMENZAR</div>
    </div>
  </div>
  <canvas id="c"></canvas>
  <script>
    const canvas = document.getElementById('c');
    const ctx = canvas.getContext('2d');
    const overlay = document.getElementById('overlay');
    const startBtn = document.getElementById('startBtn');
    const scoreEl = document.getElementById('score');
    const bestEl = document.getElementById('best');

    let W,H; function resize(){{W=canvas.width=innerWidth;H=canvas.height=innerHeight}} resize(); addEventListener('resize',resize);

    let running=false; let score=0; let best=+localStorage.getItem('{key}_best')||0;
    let py=H/2, vy=0, gravity=0.6, speed=5;
    let obstacles=[]; let lastSpawn=0;

    function reset(){{score=0; py=H/2; vy=0; speed=5; obstacles=[]; gravity=0.6;}}

    function spawn(){{
        const h = 60 + Math.random()*100;
        const isTop = Math.random() < 0.5;
        obstacles.push({{x:W+50, y: isTop?0:H-h, w:40, h:h}});
    }}

    function update(dt){{
        score += dt*5; speed += dt*0.1;
        vy += gravity; py += vy;
        if(py<0 || py>H) end();

        lastSpawn += dt;
        if(lastSpawn > 1.2 - Math.min(0.5, speed/50)){{ spawn(); lastSpawn=0; }}

        for(let i=obstacles.length-1;i>=0;i-- patterns){{
            let o = obstacles[i]; o.x -= speed;
            if(o.x < -60) obstacles.splice(i,1);
            if(100 < o.x+o.w && 100+30 > o.x && py < o.y+o.h && py+30 > o.y) end();
        }}
    }}

    function draw(){{
        ctx.fillStyle='#050505'; ctx.fillRect(0,0,W,H);
        // Player
        ctx.fillStyle='#1f5'; ctx.shadowBlur=15; ctx.shadowColor='#1f5';
        ctx.fillRect(100, py, 30, 30);
        ctx.shadowBlur=0;
        // Obstacles
        ctx.fillStyle='#f33';
        obstacles.forEach(o=>ctx.fillRect(o.x,o.y,o.w,o.h));
        scoreEl.textContent = Math.floor(score);
        bestEl.textContent = best;
    }}

    function end(){{
        running=false; if(score>best){{best=Math.floor(score); localStorage.setItem('{key}_best',best)}}
        overlay.style.display='flex';
    }}

    let last=performance.now();
    function loop(t){{
        const dt=(t-last)/1000; last=t;
        if(running) update(dt);
        draw(); requestAnimationFrame(loop);
    }}
    requestAnimationFrame(loop);

    function flip(){{ gravity *= -1; vy = 0; }}
    canvas.addEventListener('mousedown', e=>{{ if(running) flip(); }});
    canvas.addEventListener('touchstart', e=>{{ if(running) flip(); e.preventDefault(); }}, {{passive:false}});
    startBtn.onclick=()=>{ patterns overlay.style.display='none'; reset(); running=true; };
  </script>
</body>
</html>
"""

def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    used = load_used_titles()
    trends = get_trends()
    topic = pick_topic(trends, used)
    title = topic
    
    existing = [d for d in os.listdir(GAMES_DIR) if d.startswith('juego-')]
    nums = [int(d.split('-')[1]) for d in existing if d.split('-')[1].isdigit()]
    next_num = max(nums) + 1 if nums else 3
    folder = f'juego-{next_num:03d}'
    game_path = os.path.join(GAMES_DIR, folder)
    os.makedirs(game_path, exist_ok=True)

    key = f"game_{next_num:03d}"
    html = GAME_TEMPLATE.replace("{title}", title).replace("{key}", key)
    with open(os.path.join(game_path, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)

    # Update index.html menu
    idx_content = open(INDEX_PATH, 'r', encoding='utf-8').read()
    card = f'''    <li class="card">
      <div><b>Juego #{next_num:03d} — {title}</b></div>
      <div>Desafío diario basado en tendencias actuales.</div>
      <a href="games/{folder}/">Jugar</a>
    </li>
'''
    if f'Juego #{next_num:03d}' not in idx_content:
        idx_content = idx_content.replace('</ul>', card + '</ul>')
        open(INDEX_PATH, 'w', encoding='utf-8').write(idx_content)

    # Update games-list.md
    lst_content = open(LIST_PATH, 'r', encoding='utf-8').read()
    new_entry = f"{next_num}. Juego #{next_num:03d} — {title} (publicado)\n"
    if f'Juego #{next_num:03d}' not in lst_content:
        lst_content = lst_content.replace('## Ideas', new_entry + '\n## Ideas')
        open(LIST_PATH, 'w', encoding='utf-8').write(lst_content)

    print(json.dumps({'title': title, 'folder': folder}))

if __name__ == '__main__':
    main()
