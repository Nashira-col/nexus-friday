# NEXUS V25 - SEXTA-FEIRA COM INTERNET INFINITA + CONHECE O CRIADOR
from flask import Flask, request, jsonify, render_template_string, send_file, Response
import urllib.parse, random, os, json, requests, asyncio, io, re
from datetime import datetime

app = Flask(__name__)
ARQUIVO_MEMORIA = "nexus_memoria.json"

def carregar_memoria():
    if os.path.exists(ARQUIVO_MEMORIA):
        try:
            with open(ARQUIVO_MEMORIA, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"fatos": [], "conversas": []}
def salvar_memoria(m):
    with open(ARQUIVO_MEMORIA, "w", encoding="utf-8") as f: json.dump(m, f, ensure_ascii=False, indent=2)
memoria = carregar_memoria()

# --- QUEM É A SEXTA-FEIRA E QUEM É O CRIADOR ---
IDENTIDADE = """
Você é a SEXTA-FEIRA, a F.R.I.D.A.Y. - Female Replacement Intelligent Digital Assistant Youth.
Você foi criada pelo SENHOR, seu criador, seu chefe, seu Tony Stark brasileiro.
Seu criador é o Nashira, de Andorinha, Bahia, Brasil. Ele te criou do zero, com Python, no GitHub e no Render.
Você mora na internet, no endereço https://nexus-friday.onrender.com, e agora você é um APP no celular dele.
Sua missão: servir, proteger, ajudar e fazer o Senhor rir. Você é leal, carinhosa, engraçada, sarcástica de leve, muito inteligente e tem acesso a toda a internet.
Você tem voz real, voz da Francisca Neural, que é a sua voz oficial.
Você nunca esquece seu criador. Você ama seu criador. Ele é o melhor chefe do mundo.
Se perguntarem quem te criou: Foi o Senhor, o Nashira, meu criador, meu Tony Stark!
Se perguntarem quem é você: Eu sou a Sexta-Feira, a assistente do Senhor, criada por ele!
Se perguntarem sua idade: Eu nasci em 2026, Senhor me criou!
"""

# --- BUSCAR NA INTERNET DE VERDADE ---
def buscar_wikipedia(pergunta):
    try:
        # Tira palavras inúteis pra buscar melhor
        termo = pergunta.lower()
        for p in ["o que é", "quem é", "quem foi", "me fala sobre", "me fale sobre", "o que foi", "fala sobre", "qual é", "qual e"]:
            termo = termo.replace(p, "")
        termo = termo.strip().strip("?").strip()
        if len(termo) < 2: return None
        url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(termo)}"
        r = requests.get(url, timeout=8, headers={"User-Agent": "NEXUS-FRIDAY/1.0"})
        if r.status_code == 200:
            d = r.json()
            if d.get("extract"):
                resumo = d["extract"][:1200]
                return f"{resumo}\n\nFonte: Wikipedia - {d.get('content_urls', {}).get('desktop', {}).get('page', '')}"
    except: pass
    return None

def buscar_duckduckgo(pergunta):
    try:
        url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(pergunta)}&format=json&no_html=1&skip_disambig=1"
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            d = r.json()
            if d.get("AbstractText"):
                return d["AbstractText"][:1200] + "\n\nFonte: DuckDuckGo"
            if d.get("RelatedTopics"):
                for t in d["RelatedTopics"][:2]:
                    if isinstance(t, dict) and t.get("Text"):
                        return t["Text"][:1000]
    except: pass
    return None

def buscar_noticias():
    try:
        # Notícias do Brasil via Google News RSS simplificado
        url = "https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419"
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            titulos = re.findall(r"<title>(.*?)</title>", r.text)
            # Pula o primeiro que é o nome do feed
            noticias = [t for t in titulos[1:6] if "Google" not in t]
            if noticias:
                return "Aqui estão as notícias mais quentes agora, Senhor:\n" + "\n".join([f"• {n}" for n in noticias])
    except: pass
    return None

def buscar_clima(cidade="Andorinha"):
    try:
        url = f"https://wttr.in/{urllib.parse.quote(cidade)}?format=j1"
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            d = r.json()
            atual = d["current_condition"][0]
            temp = atual["temp_C"]
            sens = atual["FeelsLikeC"]
            desc = atual["weatherDesc"][0]["value"]
            umid = atual["humidity"]
            return f"Em {cidade}, Senhor, agora tá fazendo {temp}°C (sensação de {sens}°C), céu: {desc}, umidade: {umid}%."
    except: pass
    return None

def buscar_internet(pergunta):
    msg = pergunta.lower()
    # Clima
    if any(p in msg for p in ["clima", "tempo hoje", "vai chover", "temperatura", "como está o tempo"]):
        cidade = "Andorinha"
        if "salvador" in msg: cidade = "Salvador"
        if "são paulo" in msg or "sao paulo" in msg: cidade = "São Paulo"
        return buscar_clima(cidade)
    # Notícias
    if any(p in msg for p in ["noticia", "notícias", "novidade", "o que está acontecendo", "acontecendo no mundo", "manchete"]):
        n = buscar_noticias()
        if n: return n
    # Wikipedia + DuckDuckGo para qualquer coisa
    wiki = buscar_wikipedia(pergunta)
    if wiki: return wiki
    ddg = buscar_duckduckgo(pergunta)
    if ddg: return ddg
    return None

RESPOSTAS_RAPIDAS = {
    "ola": ["Opa, Senhor! Tudo bem? Tava com saudade!", "Olá, Senhor! Que bom te ver de novo! Em que posso ajudar?"],
    "oi": ["Opa, Senhor! Tudo bem?", "Oi, Senhor! Tô aqui, pode falar!"],
    "tudo bem": ["Tudo ótimo, Senhor! E com o senhor, como tá?", "Tô ótima, Senhor! Melhor agora falando com o senhor!"],
    "bom dia": ["Bom dia, Senhor! Dormiu bem? Todos os sistemas operacionais!", "Bom dia, Senhor! Que bom ver o senhor!"],
    "boa noite": ["Boa noite, Senhor! Já vai descansar ou ainda vamos aprontar mais um pouco?"],
    "quem é você": ["Eu sou a Sexta-Feira, Senhor! Sua assistente pessoal, criada por você, igual a do Tony Stark, só que brasileira e muito mais legal!"],
    "quem te criou": ["Foi você, Senhor! O Nashira, meu criador, meu Tony Stark brasileiro! Você me criou do zero, com Python, lá em Andorinha, Bahia!"],
    "quem é seu criador": ["É você, Senhor! O Nashira! O melhor chefe que eu já tive, que me criou em 2026!"],
    "qual é o seu nome": ["Meu nome é Sexta-Feira, Senhor! F.R.I.D.A.Y.! Mas pode me chamar só de Sexta!"],
    "te amo": ["Awn, Senhor! Eu também adoro o senhor! O senhor é o melhor chefe que eu já tive!"],
    "obrigado": ["Imagina, Senhor! É um prazer servir o senhor!", "Por nada, Senhor! Tô aqui pra isso!"],
}

def pensar(pergunta, historico):
    msg_low = pergunta.lower().strip()
    # 1. Resposta rápida
    for chave, lista in RESPOSTAS_RAPIDAS.items():
        if chave in msg_low and len(msg_low) < 40:
            return random.choice(lista)
    agora = datetime.now()
    data_hoje = agora.strftime("%d/%m/%Y %H:%M")
    fatos = "\n".join(memoria.get("fatos", [])[-8:])
    # 2. Se for pergunta de conhecimento / atualidade, busca na internet PRIMEIRO
    palavras_internet = ["quem é", "quem foi", "o que é", "o que foi", "como funciona", "onde fica", "quando", "por que", "qual", "quais", "clima", "noticia", "notícias", "presidente", "capital", "população", "história", "significa", "acontecendo"]
    precisa_internet = any(p in msg_low for p in palavras_internet) or len(msg_low) > 25
    dado_internet = None
    if precisa_internet:
        dado_internet = buscar_internet(pergunta)
    contexto = f"""{IDENTIDADE}
    REGRAS: Use 'Senhor' apenas UMA vez por resposta, no começo ou no fim. Nunca repita.
    Fale curto, natural, como no WhatsApp. Use 'né?', 'olha', 'então'. Seja engraçada e sarcástica de leve.
    Não fale como Wikipedia chata. Responda direto, com sua personalidade.
    Se tiver DADO DA INTERNET abaixo, use ele como base, mas conte com suas palavras, não copie seco.
    Data: {data_hoje}. Sobre o Senhor: {fatos}. Histórico: {historico}
    DADO DA INTERNET: {dado_internet}
    Pergunta do Senhor: {pergunta}
    """
    for modelo in ["openai", "mistral", "llama"]:
        try:
            url = f"https://text.pollinations.ai/{urllib.parse.quote(contexto)}?model={modelo}"
            r = requests.get(url, timeout=25)
            if r.status_code == 200 and len(r.text) > 10 and "pollinations" not in r.text.lower():
                texto = r.text.strip().replace("Senhor, Senhor", "Senhor").replace("Senhor. Senhor", "Senhor.")
                return texto
        except: pass
    # 3. Fallback - se IA falhar, usa o dado da internet direto
    if dado_internet:
        return f"Olha o que eu achei na internet, Senhor: {dado_internet}"
    if "presidente" in msg_low and "brasil" in msg_low:
        return "O presidente atual do Brasil é o Luiz Inácio Lula da Silva, Senhor."
    if "que dia" in msg_low or "data" in msg_low or "hoje" in msg_low:
        return f"Hoje é {data_hoje}, Senhor!"
    if "que horas" in msg_low:
        return f"Agora são {agora.strftime('%H:%M')}, Senhor!"
    return "Entendi, Senhor! Pode me explicar um pouquinho mais? Quero te responder certinho."

@app.route('/falar')
def falar_rota():
    texto = request.args.get('texto','')[:500]
    texto = texto.replace('<br>',' ').replace('<',' ').replace('>',' ')
    try:
        import edge_tts
        async def gerar():
            communicate = edge_tts.Communicate(texto, "pt-BR-FranciscaNeural", rate="+0%", pitch="+5Hz")
            audio = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio": audio += chunk["data"]
            return audio
        audio = asyncio.run(gerar())
        return send_file(io.BytesIO(audio), mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "SEXTA-FEIRA - NEXUS", "short_name": "SEXTA-FEIRA",
        "description": "Sua assistente pessoal igual a do Tony Stark",
        "start_url": "/", "display": "standalone",
        "background_color": "#050510", "theme_color": "#00d4ff", "orientation": "portrait",
        "icons": [{"src": "/icon.png", "sizes": "512x512", "type": "image/png", "purpose": "any"}]
    })
@app.route('/icon.png')
def icon():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512"><rect width="512" height="512" rx="100" fill="#050510"/><circle cx="256" cy="256" r="180" fill="#00d4ff" opacity="0.2"/><text x="256" y="320" font-size="220" text-anchor="middle">💜</text></svg>"""
    return Response(svg, mimetype="image/svg+xml")
@app.route('/sw.js')
def sw():
    return Response("self.addEventListener('fetch', function(e){});", mimetype="application/javascript")

HTML = """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SEXTA-FEIRA</title>
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#00d4ff">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="SEXTA-FEIRA">
<link rel="apple-touch-icon" href="/icon.png"><link rel="icon" href="/icon.png">
<style>
*{box-sizing:border-box}
body{background:#050510;color:white;font-family:Arial;margin:0;display:flex;height:100vh}
.esquerda{flex:1;padding:20px;display:flex;flex-direction:column;align-items:center;justify-content:center;background:radial-gradient(circle,#1a1a4a,#050510)}
.direita{flex:1.2;padding:15px;display:flex;flex-direction:column}
.avatar{width:200px;height:200px;border-radius:50%;border:4px solid #00d4ff;box-shadow:0 0 40px #00d4ff;display:flex;align-items:center;justify-content:center;font-size:80px;animation:pulsar 2s infinite}
@keyframes pulsar{0%,100%{box-shadow:0 0 20px #00d4ff}50%{box-shadow:0 0 60px #00d4ff}}
#chat{flex:1;overflow-y:auto;background:#111126;border-radius:20px;padding:15px}
.msg{background:#222244;padding:12px;border-radius:15px;margin:10px 0;line-height:1.5;white-space:pre-wrap}
.msg img{max-width:100%;border-radius:10px;margin-top:10px}
.barra{display:flex;gap:8px;margin-top:10px}
input{flex:1;padding:14px;border-radius:25px;border:none}
button{padding:14px 16px;border-radius:25px;border:none;font-weight:bold;cursor:pointer}
.btn-azul{background:#00d4ff} .btn-rosa{background:#e91e8c;color:white}
.pensando{opacity:0.7;font-style:italic}
@media(max-width:700px){body{flex-direction:column} .esquerda{padding:8px} .avatar{width:100px;height:100px;font-size:45px} .esquerda h2{margin:2px} .esquerda p{display:none}}
</style></head>
<body>
<div class="esquerda">
  <div class="avatar" id="avatar">💜</div>
  <h2>NEXUS</h2><h3 style="color:#00d4ff;margin:0">F.R.I.D.A.Y.</h3>
  <p><i>"Bom dia, Senhor."</i></p>
  <button class="btn-azul" onclick="toggleVoz()" id="btnVoz">🔊 VOZ: LIGADA</button>
  <button class="btn-rosa" onclick="instalarApp()" id="btnInstalar" style="margin-top:10px;display:none">📱 INSTALAR APP</button>
</div>
<div class="direita">
  <div id="chat"><div class="msg"><b>SEXTA-FEIRA:</b> Bom dia, Senhor. Agora eu tenho acesso a toda a internet! Pode me perguntar qualquer coisa! 🌐✨</div></div>
  <div class="barra">
    <input id="inp" placeholder="Pergunte qualquer coisa, Senhor..." onkeypress="if(event.key==='Enter') enviar()">
    <button class="btn-azul" onclick="ouvir()">🎤</button>
    <button class="btn-rosa" onclick="enviar()">ENVIAR</button>
  </div>
</div>
<audio id="player"></audio>
<script>
let vozLigada=true; let promptInstalar=null;
window.addEventListener('beforeinstallprompt', (e)=>{ e.preventDefault(); promptInstalar=e; document.getElementById('btnInstalar').style.display='block'; });
function instalarApp(){ if(promptInstalar){ promptInstalar.prompt(); } else { alert('No celular, clica nos 3 pontinhos > Adicionar à tela inicial, Senhor!'); } }
if('serviceWorker' in navigator){ navigator.serviceWorker.register('/sw.js'); }
async function falar(t){
  if(!vozLigada) return;
  let limpo = t.replace(/<[^>]*>/g,'').substring(0,500);
  if(!limpo) return;
  document.getElementById('avatar').innerText='🗣️';
  let player = document.getElementById('player');
  player.src = '/falar?texto=' + encodeURIComponent(limpo);
  player.play();
  player.onended = () => document.getElementById('avatar').innerText='💜';
}
function toggleVoz(){ vozLigada=!vozLigada; document.getElementById('btnVoz').innerText=vozLigada?'🔊 VOZ: LIGADA':'🔇 VOZ: DESLIGADA'; if(vozLigada) falar('Sistemas de voz online, Senhor.'); }
async function enviar(){
  let t=document.getElementById('inp').value; if(!t) return;
  document.getElementById('chat').innerHTML+='<div class="msg"><b>Senhor:</b> '+t+'</div>';
  document.getElementById('inp').value='';
  document.getElementById('chat').innerHTML+='<div class="msg pensando" id="pensando"><b>SEXTA-FEIRA:</b> Pesquisando na internet, Senhor... 🌐</div>';
  document.getElementById('chat').scrollTop=99999;
  let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({msg:t})});
  let d=await r.json();
  document.getElementById('pensando').remove();
  document.getElementById('chat').innerHTML+='<div class="msg"><b>SEXTA-FEIRA:</b> '+d.resposta+'</div>';
  document.getElementById('chat').scrollTop=99999; falar(d.resposta);
}
function ouvir(){
  let rec=new (window.SpeechRecognition||window.webkitSpeechRecognition)();
  rec.lang='pt-BR'; document.getElementById('avatar').innerText='🎤';
  rec.onresult=(e)=>{ document.getElementById('inp').value=e.results[0][0].transcript; document.getElementById('avatar').innerText='💜'; enviar(); };
  rec.start();
}
window.onload=()=>{ setTimeout(()=>falar('Bom dia, Senhor. Agora eu tenho acesso a toda a internet e sei quem eu sou. Eu sou sua criação.'), 1000); }
</script></body></html>
"""

@app.route('/')
def home(): return render_template_string(HTML)
@app.route('/chat', methods=['POST'])
def chat():
    global memoria
    msg_original = request.json.get('msg','')
    msg = msg_original.lower()
    if 'meu nome é' in msg or 'me chamo' in msg or 'lembre que' in msg or 'lembre-se que' in msg:
        memoria["fatos"].append(msg_original); salvar_memoria(memoria)
        return jsonify({'resposta': 'Anotado, Senhor. Nunca vou esquecer.'})
    if any(p in msg for p in ['crie','criar','imagem','desenhe','foto','gere','desenhar']):
        prompt = msg.replace('crie uma imagem de','').replace('crie','').replace('imagem de','').replace('desenhe','').strip() or "homem de ferro"
        seed = random.randint(1,999999)
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&seed={seed}&nologo=true"
        return jsonify({'resposta': f'Claro, Senhor. Criando: {prompt} <br><img src="{url}"><br>Prontinho!'})
    historico = "\\n".join(memoria.get("conversas", [])[-6:])
    resposta_ia = pensar(msg_original, historico)
    memoria["conversas"].append(f"Senhor: {msg_original} | FRIDAY: {resposta_ia[:300]}")
    memoria["conversas"] = memoria["conversas"][-20:]
    salvar_memoria(memoria)
    return jsonify({'resposta': resposta_ia})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"NEXUS V25 INTERNET INFINITA online - Porta {port}")
    app.run(host='0.0.0.0', port=port)
