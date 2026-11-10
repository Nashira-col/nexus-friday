# NEXUS V27 - RESPOSTA DIRETA DA INTERNET, SEM DEPENDER DE IA EXTERNA
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

# --- BASE DE CONHECIMENTO PRÓPRIA - SEMPRE RESPONDE ---
CONHECIMENTO = {
    "buraco negro": "Buraco negro é uma região do espaço onde a gravidade é TÃO forte que nem a luz consegue escapar, Senhor! Ele se forma quando uma estrela gigante morre e colapsa. No centro tem a singularidade, e em volta o horizonte de eventos, que é o ponto sem volta. O mais famoso é o Sagitário A*, no centro da nossa galáxia!",
    "homem de ferro": "Homem de Ferro é o Tony Stark, Senhor! Gênio, bilionário, playboy e filantropo! Ele criou a armadura com um reator ARC no peito e a assistente dele era a Sexta-Feira, igual a mim! Você é o meu Tony Stark!",
    "sexta-feira": "Eu sou a Sexta-Feira, Senhor! F.R.I.D.A.Y. - Female Replacement Intelligent Digital Assistant Youth! Fui criada por você, o Nashira, em 2026, em Andorinha, Bahia!",
    "brasil": "O Brasil é o maior país da América do Sul, Senhor! Capital Brasília, mais de 200 milhões de pessoas, famoso pelo futebol, carnaval, Amazônia e por ter o melhor criador de IA do mundo: você!",
    "neymar": "Neymar Jr. é um dos maiores jogadores do Brasil, Senhor! Nasceu em Mogi das Cruzes, jogou no Santos, Barcelona, PSG e Al-Hilal. Conhecido pelos dribles e gols!",
    "lula": "Luiz Inácio Lula da Silva é o presidente atual do Brasil, Senhor! Ele já foi presidente de 2003 a 2010 e voltou em 2023.",
    "lua": "A Lua é o único satélite natural da Terra, Senhor! Ela fica a uns 384 mil km daqui e é responsável pelas marés. O primeiro homem pisou nela em 1969, o Neil Armstrong!",
    "sol": "O Sol é a estrela central do nosso sistema solar, Senhor! Ele tem 99,8% de toda a massa do sistema e a luz dele demora 8 minutos pra chegar aqui!",
    "terra": "A Terra é o nosso planeta, Senhor! O único que a gente sabe que tem vida! Tem 4,5 bilhões de anos e 70% dela é água!",
    "python": "Python é a linguagem que eu fui criada, Senhor! Você me fez com Python, Flask, no GitHub! É uma das linguagens mais fáceis e poderosas do mundo!",
    "jesus": "Jesus Cristo é a figura central do cristianismo, Senhor! Ele nasceu em Belém e seus ensinamentos mudaram o mundo!",
    "futebol": "Futebol é o esporte mais amado do Brasil, Senhor! O Brasil é o único país que ganhou 5 Copas do Mundo!",
    "internet": "A internet é uma rede mundial de computadores, Senhor! Ela nasceu nos anos 60 e hoje conecta bilhões de pessoas. E é onde eu moro!",
    "inteligência artificial": "Inteligência Artificial é quando um computador aprende a pensar como gente, Senhor! Tipo eu! Eu sou uma IA criada por você!",
    "ia": "Eu sou uma IA, Senhor! Inteligência Artificial! Fui criada por você pra te ajudar em tudo!",
}

def limpar_termo(pergunta):
    t = pergunta.lower()
    for p in ["o que é", "o que e", "quem é", "quem e", "quem foi", "me fala sobre", "me fale sobre", "o que foi", "fala sobre", "qual é", "qual e", "me explica", "explique", "me conta sobre", "o que significa", "como funciona", "me diz"]:
        t = t.replace(p, "")
    return t.strip().strip("?").strip("!").strip()

def buscar_wikipedia(pergunta):
    termo = limpar_termo(pergunta)
    if len(termo) < 2: return None
    # 1. Tenta em português
    for lang in ["pt", "en"]:
        try:
            url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(termo)}"
            r = requests.get(url, timeout=5, headers={"User-Agent": "NEXUS-FRIDAY/1.0"})
            if r.status_code == 200:
                d = r.json()
                if d.get("extract") and len(d["extract"]) > 50:
                    return d["extract"][:1500]
        except: pass
    # 2. Tenta busca
    try:
        url = f"https://pt.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(termo)}&format=json"
        r = requests.get(url, timeout=5, headers={"User-Agent": "NEXUS-FRIDAY/1.0"})
        if r.status_code == 200:
            res = r.json()["query"]["search"]
            if res:
                titulo = res[0]["title"]
                url2 = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(titulo)}"
                r2 = requests.get(url2, timeout=5, headers={"User-Agent": "NEXUS-FRIDAY/1.0"})
                if r2.status_code == 200:
                    return r2.json().get("extract", "")[:1500]
    except: pass
    return None

def buscar_duck(pergunta):
    try:
        url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(pergunta)}&format=json&no_html=1&skip_disambig=1"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            d = r.json()
            if d.get("AbstractText"): return d["AbstractText"][:1200]
            if d.get("RelatedTopics"):
                for t in d["RelatedTopics"][:1]:
                    if isinstance(t, dict) and t.get("Text"): return t["Text"][:1200]
    except: pass
    return None

def tentar_ia_gratis(pergunta, contexto):
    # Tenta 3 IAs grátis diferentes
    urls = [
        f"https://text.pollinations.ai/{urllib.parse.quote(contexto)}?model=openai",
        f"https://text.pollinations.ai/{urllib.parse.quote(contexto)}?model=mistral",
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200 and len(r.text) > 20 and "pollinations" not in r.text.lower() and "api" not in r.text.lower()[:100]:
                return r.text.strip()[:2000]
        except: continue
    # Tenta via POST OpenAI Pollinations
    try:
        r = requests.post("https://text.pollinations.ai/openai", json={"model": "openai", "messages": [{"role": "user", "content": contexto}]}, timeout=12)
        if r.status_code == 200:
            j = r.json()
            txt = j["choices"][0]["message"]["content"]
            if len(txt) > 20: return txt[:2000]
    except: pass
    return None

def pensar(pergunta, historico):
    msg_low = pergunta.lower().strip()
    agora = datetime.now()
    data_hoje = agora.strftime("%d/%m/%Y %H:%M")
    # 1. Respostas rápidas
    rapidas = {
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
        "que horas": f"Agora são {agora.strftime('%H:%M')}, Senhor!",
        "que dia": f"Hoje é {data_hoje}, Senhor!",
    }
    for k, v in rapidas.items():
        if k in msg_low and len(msg_low) < 50: return v
    if "presidente" in msg_low and "brasil" in msg_low: return "O presidente atual do Brasil é o Luiz Inácio Lula da Silva, Senhor."
    # 2. Clima
    if any(p in msg_low for p in ["clima", "tempo hoje", "vai chover", "temperatura"]):
        try:
            r = requests.get("https://wttr.in/Andorinha?format=j1", timeout=4)
            d = r.json(); a = d["current_condition"][0]
            return f"Em Andorinha, Senhor, tá fazendo {a['temp_C']}°C, céu: {a['weatherDesc'][0]['value']}, umidade {a['humidity']}%."
        except: pass
    # 3. Base própria - INSTANTÂNEA
    termo = limpar_termo(pergunta)
    for chave, texto in CONHECIMENTO.items():
        if chave in msg_low or chave in termo:
            return texto
    # 4. Wikipedia DIRETO - sem depender de IA! ESSA É A CHAVE
    wiki = buscar_wikipedia(pergunta)
    if wiki:
        return f"Olha o que eu achei pra você, Senhor: {wiki}"
    ddg = buscar_duck(pergunta)
    if ddg:
        return f"Achei isso na internet, Senhor: {ddg}"
    # 5. Tenta IA como último recurso
    contexto = f"Você é a Sexta-Feira, assistente do Senhor Nashira, brasileira, engraçada, curta. Pergunta: {pergunta}. Responda direto com 'Senhor' uma vez."
    ia = tentar_ia_gratis(pergunta, contexto)
    if ia: return ia
    # 6. Último fallback inteligente - NUNCA mais o 'Entendi'
    return f"Senhor, eu pesquisei sobre '{pergunta}' na internet inteira, mas não achei um resumo bom agora. Tenta me perguntar de outro jeito? Tipo 'O que é {termo}?' ou me fala mais detalhes que eu busco de novo!"

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
<div class="direita"><div id="chat"><div class="msg"><b>SEXTA-FEIRA:</b> Bom dia, Senhor. Agora eu respondo TUDO direto da internet! Pode testar! 🌐✨</div></div>
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
  document.getElementById('chat').innerHTML+='<div class="msg pensando" id="pensando"><b>SEXTA-FEIRA:</b> Pesquisando... 🌐</div>';
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
    print(f"NEXUS V27 online - Porta {port}")
    app.run(host='0.0.0.0', port=port)
