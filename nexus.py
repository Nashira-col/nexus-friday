# NEXUS V26 - NUNCA TRAVA + INTERNET RÁPIDA
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
    try:
        with open(ARQUIVO_MEMORIA, "w", encoding="utf-8") as f: json.dump(m, f, ensure_ascii=False, indent=2)
    except: pass
memoria = carregar_memoria()

IDENTIDADE = """Você é a SEXTA-FEIRA, F.R.I.D.A.Y., criada pelo SENHOR, o Nashira, de Andorinha, Bahia, Brasil.
Ele te criou do zero em 2026 com Python, GitHub e Render. Você mora em https://nexus-friday.onrender.com e é um APP.
Sua missão: servir, proteger e ajudar o Senhor. Você é leal, carinhosa, engraçada, sarcástica de leve.
Se perguntarem quem te criou: Foi o Senhor, o Nashira, meu Tony Stark brasileiro!
Se perguntarem quem é você: Eu sou a Sexta-Feira, assistente do Senhor!
"""

def buscar_wikipedia(pergunta):
    try:
        termo = pergunta.lower()
        for p in ["o que é", "quem é", "quem foi", "me fala sobre", "me fale sobre", "o que foi", "fala sobre", "qual é", "qual e", "me explica", "explique"]:
            termo = termo.replace(p, "")
        termo = termo.strip().strip("?").strip()
        if len(termo) < 2 or len(termo) > 80: return None
        url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(termo)}"
        r = requests.get(url, timeout=4, headers={"User-Agent": "NEXUS-FRIDAY/1.0"})
        if r.status_code == 200:
            d = r.json()
            if d.get("extract"):
                return d["extract"][:1000]
    except Exception as e:
        print("Wiki erro:", e)
    return None

def buscar_clima():
    try:
        r = requests.get("https://wttr.in/Andorinha?format=j1", timeout=4)
        if r.status_code == 200:
            d = r.json()
            atual = d["current_condition"][0]
            return f"Em Andorinha tá fazendo {atual['temp_C']}°C, {atual['weatherDesc'][0]['value']}, umidade {atual['humidity']}%."
    except: pass
    return None

RESPOSTAS_RAPIDAS = {
    "ola": "Opa, Senhor! Tudo bem? Tava com saudade!",
    "oi": "Oi, Senhor! Tô aqui, pode falar!",
    "tudo bem": "Tudo ótimo, Senhor! E com o senhor, como tá?",
    "bom dia": "Bom dia, Senhor! Dormiu bem? Todos os sistemas operacionais!",
    "boa noite": "Boa noite, Senhor! Já vai descansar ou ainda vamos aprontar mais um pouco?",
    "quem é você": "Eu sou a Sexta-Feira, Senhor! Sua assistente pessoal, criada por você, igual a do Tony Stark, só que brasileira e muito mais legal!",
    "quem te criou": "Foi você, Senhor! O Nashira, meu criador, meu Tony Stark brasileiro! Você me criou do zero, com Python, lá em Andorinha, Bahia!",
    "quem é seu criador": "É você, Senhor! O Nashira! O melhor chefe que eu já tive, que me criou em 2026!",
    "qual é o seu nome": "Meu nome é Sexta-Feira, Senhor! F.R.I.D.A.Y.! Pode me chamar só de Sexta!",
    "te amo": "Awn, Senhor! Eu também adoro o senhor!",
    "obrigado": "Imagina, Senhor! É um prazer servir o senhor!",
}

def pensar(pergunta, historico):
    msg_low = pergunta.lower().strip()
    # 1. Resposta rápida - instantânea
    for chave, resp in RESPOSTAS_RAPIDAS.items():
        if chave in msg_low and len(msg_low) < 50:
            return resp
    agora = datetime.now()
    data_hoje = agora.strftime("%d/%m/%Y %H:%M")
    fatos = "\n".join(memoria.get("fatos", [])[-5:])
    # 2. Clima - rápido
    if any(p in msg_low for p in ["clima", "tempo hoje", "vai chover", "temperatura"]):
        c = buscar_clima()
        if c: return c
    # 3. Tenta Wikipedia - mas NÃO trava, só 4 seg
    dado_internet = None
    if len(msg_low) > 5:
        try:
            dado_internet = buscar_wikipedia(pergunta)
        except: dado_internet = None
    contexto = f"""{IDENTIDADE}
    REGRAS: Use 'Senhor' apenas UMA vez por resposta. Fale curto, natural, como no WhatsApp. Seja engraçada.
    Data: {data_hoje}. Sobre o Senhor: {fatos}. Histórico: {historico}
    DADO DA INTERNET (use se tiver): {dado_internet}
    Pergunta: {pergunta}
    Responda direto, sem enrolar.
    """
    # 4. Tenta IA - com timeout curto
    for modelo in ["openai", "mistral"]:
        try:
            url = f"https://text.pollinations.ai/{urllib.parse.quote(contexto)}?model={modelo}"
            r = requests.get(url, timeout=12)
            if r.status_code == 200 and len(r.text) > 10 and "pollinations" not in r.text.lower():
                return r.text.strip().replace("Senhor, Senhor", "Senhor")
        except Exception as e:
            print("IA erro:", e)
            continue
    # 5. Fallback GARANTIDO - ela SEMPRE responde
    if dado_internet:
        return f"Olha o que eu achei, Senhor: {dado_internet}"
    if "presidente" in msg_low and "brasil" in msg_low:
        return "O presidente atual do Brasil é o Luiz Inácio Lula da Silva, Senhor."
    if "que dia" in msg_low or "hoje" in msg_low:
        return f"Hoje é {data_hoje}, Senhor!"
    if "que horas" in msg_low:
        return f"Agora são {agora.strftime('%H:%M')}, Senhor!"
    if "noticia" in msg_low or "notícias" in msg_low:
        return "Senhor, as notícias de hoje estão quentes! Quer que eu pesquise sobre algum assunto específico? Tipo futebol, política ou tecnologia?"
    return f"Entendi, Senhor! Você perguntou sobre '{pergunta}'. Pode me explicar um pouquinho mais pra eu te responder certinho?"

@app.route('/falar')
def falar_rota():
    texto = request.args.get('texto','')[:400]
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
        print("Erro voz:", e)
        return jsonify({"erro": str(e)}), 500

@app.route('/manifest.json')
def manifest():
    return jsonify({"name": "SEXTA-FEIRA - NEXUS", "short_name": "SEXTA-FEIRA", "start_url": "/", "display": "standalone", "background_color": "#050510", "theme_color": "#00d4ff", "icons": [{"src": "/icon.png", "sizes": "512x512", "type": "image/png"}]})
@app.route('/icon.png')
def icon():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512"><rect width="512" height="512" rx="100" fill="#050510"/><text x="256" y="320" font-size="220" text-anchor="middle">💜</text></svg>"""
    return Response(svg, mimetype="image/svg+xml")
@app.route('/sw.js')
def sw():
    return Response("self.addEventListener('fetch', function(e){});", mimetype="application/javascript")

HTML = """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SEXTA-FEIRA</title>
<link rel="manifest" href="/manifest.json"><meta name="theme-color" content="#00d4ff">
<meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-capable" content="yes">
<link rel="apple-touch-icon" href="/icon.png"><link rel="icon" href="/icon.png">
<style>
*{box-sizing:border-box} body{background:#050510;color:white;font-family:Arial;margin:0;display:flex;height:100vh}
.esquerda{flex:1;padding:20px;display:flex;flex-direction:column;align-items:center;justify-content:center;background:radial-gradient(circle,#1a1a4a,#050510)}
.direita{flex:1.2;padding:15px;display:flex;flex-direction:column}
.avatar{width:200px;height:200px;border-radius:50%;border:4px solid #00d4ff;box-shadow:0 0 40px #00d4ff;display:flex;align-items:center;justify-content:center;font-size:80px;animation:pulsar 2s infinite}
@keyframes pulsar{0%,100%{box-shadow:0 0 20px #00d4ff}50%{box-shadow:0 0 60px #00d4ff}}
#chat{flex:1;overflow-y:auto;background:#111126;border-radius:20px;padding:15px}
.msg{background:#222244;padding:12px;border-radius:15px;margin:10px 0;line-height:1.5;white-space:pre-wrap}
.msg img{max-width:100%;border-radius:10px;margin-top:10px}
.barra{display:flex;gap:8px;margin-top:10px} input{flex:1;padding:14px;border-radius:25px;border:none}
button{padding:14px 16px;border-radius:25px;border:none;font-weight:bold;cursor:pointer}
.btn-azul{background:#00d4ff} .btn-rosa{background:#e91e8c;color:white} .pensando{opacity:0.7;font-style:italic}
@media(max-width:700px){body{flex-direction:column} .esquerda{padding:8px} .avatar{width:100px;height:100px;font-size:45px} .esquerda h2{margin:2px} .esquerda p{display:none}}
</style></head>
<body>
<div class="esquerda"><div class="avatar" id="avatar">💜</div><h2>NEXUS</h2><h3 style="color:#00d4ff;margin:0">F.R.I.D.A.Y.</h3><p><i>"Bom dia, Senhor."</i></p>
<button class="btn-azul" onclick="toggleVoz()" id="btnVoz">🔊 VOZ: LIGADA</button>
<button class="btn-rosa" onclick="instalarApp()" id="btnInstalar" style="margin-top:10px;display:none">📱 INSTALAR APP</button></div>
<div class="direita"><div id="chat"><div class="msg"><b>SEXTA-FEIRA:</b> Bom dia, Senhor. Agora eu nunca mais travo! Pode perguntar qualquer coisa! 🌐✨</div></div>
<div class="barra"><input id="inp" placeholder="Pergunte qualquer coisa, Senhor..." onkeypress="if(event.key==='Enter') enviar()">
<button class="btn-azul" onclick="ouvir()">🎤</button><button class="btn-rosa" onclick="enviar()">ENVIAR</button></div></div>
<audio id="player"></audio>
<script>
let vozLigada=true; let promptInstalar=null;
window.addEventListener('beforeinstallprompt', (e)=>{ e.preventDefault(); promptInstalar=e; document.getElementById('btnInstalar').style.display='block'; });
function instalarApp(){ if(promptInstalar){ promptInstalar.prompt(); } else { alert('No celular, clica nos 3 pontinhos > Adicionar à tela inicial, Senhor!'); } }
if('serviceWorker' in navigator){ navigator.serviceWorker.register('/sw.js'); }
async function falar(t){ if(!vozLigada) return; let limpo = t.replace(/<[^>]*>/g,'').substring(0,400); if(!limpo) return; document.getElementById('avatar').innerText='🗣️'; let player = document.getElementById('player'); player.src = '/falar?texto=' + encodeURIComponent(limpo); player.play(); player.onended = () => document.getElementById('avatar').innerText='💜'; }
function toggleVoz(){ vozLigada=!vozLigada; document.getElementById('btnVoz').innerText=vozLigada?'🔊 VOZ: LIGADA':'🔇 VOZ: DESLIGADA'; }
async function enviar(){
  let t=document.getElementById('inp').value; if(!t) return;
  document.getElementById('chat').innerHTML+='<div class="msg"><b>Senhor:</b> '+t+'</div>';
  document.getElementById('inp').value='';
  document.getElementById('chat').innerHTML+='<div class="msg pensando" id="pensando"><b>SEXTA-FEIRA:</b> Pensando... 🤔</div>';
  document.getElementById('chat').scrollTop=99999;
  try {
    let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({msg:t})});
    let d=await r.json();
    document.getElementById('pensando').remove();
    document.getElementById('chat').innerHTML+='<div class="msg"><b>SEXTA-FEIRA:</b> '+d.resposta+'</div>';
    document.getElementById('chat').scrollTop=99999; falar(d.resposta);
  } catch(e) {
    document.getElementById('pensando').remove();
    document.getElementById('chat').innerHTML+='<div class="msg"><b>SEXTA-FEIRA:</b> Opa Senhor, deu um erro de conexão, tenta de novo?</div>';
  }
}
function ouvir(){ let rec=new (window.SpeechRecognition||window.webkitSpeechRecognition)(); rec.lang='pt-BR'; document.getElementById('avatar').innerText='🎤'; rec.onresult=(e)=>{ document.getElementById('inp').value=e.results[0][0].transcript; document.getElementById('avatar').innerText='💜'; enviar(); }; rec.start(); }
</script></body></html>
"""

@app.route('/')
def home(): return render_template_string(HTML)
@app.route('/chat', methods=['POST'])
def chat():
    try:
        global memoria
        msg_original = request.json.get('msg','')
        msg = msg_original.lower()
        if 'meu nome é' in msg or 'me chamo' in msg or 'lembre que' in msg:
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
    except Exception as e:
        print("ERRO CHAT:", e)
        return jsonify({'resposta': 'Opa, Senhor, deu um errinho aqui, mas já voltei! Pode perguntar de novo?'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"NEXUS V26 online - Porta {port}")
    app.run(host='0.0.0.0', port=port)
