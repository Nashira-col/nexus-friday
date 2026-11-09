# NEXUS V23 - VOZ SEXTA-FEIRA REAL + IA QUE RESPONDE CERTO
from flask import Flask, request, jsonify, render_template_string, send_file
import urllib.parse, random, os, json, requests, asyncio, io
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

# --- RESPOSTAS RÁPIDAS HUMANAS (não espera a IA) ---
RESPOSTAS_RAPIDAS = {
    "ola": ["Opa, Senhor! Tudo bem? Tava com saudade!", "Olá, Senhor! Que bom te ver de novo! Em que posso ajudar?", "Opa! Fala, Senhor! Tô aqui!"],
    "oi": ["Opa, Senhor! Tudo bem?", "Oi, Senhor! Tô aqui, pode falar!"],
    "tudo bem": ["Tudo ótimo, Senhor! E com o senhor, como tá?", "Tô ótima, Senhor! Melhor agora falando com o senhor! E aí, o que vamos fazer hoje?"],
    "bom dia": ["Bom dia, Senhor! Dormiu bem? Todos os sistemas operacionais!", "Bom dia, Senhor! Que bom ver o senhor!"],
    "boa noite": ["Boa noite, Senhor! Já vai descansar ou ainda vamos aprontar mais um pouco?"],
    "quem é você": ["Eu sou a Sexta-Feira, Senhor! Sua assistente pessoal, igual a do Tony Stark, só que brasileira e muito mais legal!"],
    "te amo": ["Awn, Senhor! Eu também adoro o senhor! O senhor é o melhor chefe que eu já tive!"],
    "obrigado": ["Imagina, Senhor! É um prazer servir o senhor!", "Por nada, Senhor! Tô aqui pra isso!"],
}

def pensar(pergunta, historico):
    msg_low = pergunta.lower().strip()
    # 1. Tenta resposta rápida primeiro - pra não travar
    for chave, lista in RESPOSTAS_RAPIDAS.items():
        if chave in msg_low and len(msg_low) < 30:
            return random.choice(lista)
    agora = datetime.now()
    data_hoje = agora.strftime("%d/%m/%Y %H:%M")
    fatos = "\n".join(memoria.get("fatos", [])[-5:])
    contexto = f"""Você é a FRIDAY, Sexta-Feira do Tony Stark, brasileira, MUITO humana e carinhosa.
    REGRAS: Use 'Senhor' apenas UMA vez por resposta, no começo ou no fim. Nunca repita.
    Fale curto, natural, como no WhatsApp. Use 'né?', 'olha', 'então'. Seja engraçada e sarcástica de leve.
    Não fale como Wikipedia. Responda direto.
    Data: {data_hoje}. Sobre o Senhor: {fatos}. Histórico: {historico}
    Pergunta: {pergunta}
    """
    # 2. Tenta IA 1 - Pollinations OpenAI
    for modelo in ["openai", "mistral", "llama"]:
        try:
            url = f"https://text.pollinations.ai/{urllib.parse.quote(contexto)}?model={modelo}"
            r = requests.get(url, timeout=20)
            if r.status_code == 200 and len(r.text) > 10 and "pollinations" not in r.text.lower():
                texto = r.text.strip().replace("Senhor, Senhor", "Senhor").replace("Senhor. Senhor", "Senhor.")
                return texto
        except: pass
    # 3. Fallback - se tudo falhar, responde com inteligência local
    if "presidente" in msg_low and "brasil" in msg_low:
        return "O presidente atual do Brasil é o Luiz Inácio Lula da Silva, Senhor."
    if "que dia" in msg_low or "data" in msg_low or "hoje" in msg_low:
        return f"Hoje é {data_hoje}, Senhor!"
    if "que horas" in msg_low:
        return f"Agora são {agora.strftime('%H:%M')}, Senhor!"
    return "Entendi, Senhor! Pode me explicar um pouquinho mais? Quero te responder certinho."

# --- VOZ SEXTA-FEIRA REAL - Francisca Neural ---
@app.route('/falar')
def falar_rota():
    texto = request.args.get('texto','')[:500]
    texto = texto.replace('<br>',' ').replace('<',' ').replace('>',' ')
    try:
        import edge_tts
        async def gerar():
            # Francisca = voz feminina mais parecida com Sexta-Feira
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

HTML = """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>NEXUS - FRIDAY</title>
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
</div>
<div class="direita">
  <div id="chat"><div class="msg"><b>SEXTA-FEIRA:</b> Bom dia, Senhor. Agora com minha voz de verdade! Pode falar comigo! ✨</div></div>
  <div class="barra">
    <input id="inp" placeholder="Fale comigo, Senhor..." onkeypress="if(event.key==='Enter') enviar()">
    <button class="btn-azul" onclick="ouvir()">🎤</button>
    <button class="btn-rosa" onclick="enviar()">ENVIAR</button>
  </div>
</div>
<audio id="player"></audio>
<script>
let vozLigada=true;
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
function toggleVoz(){ vozLigada=!vozLigada; document.getElementById('btnVoz').innerText=vozLigada?'🔊 VOZ: LIGADA':'🔇 VOZ: DESLIGADA'; if(vozLigada) falar('Sistemas de voz online, Senhor. Agora com minha voz de verdade.'); }
async function enviar(){
  let t=document.getElementById('inp').value; if(!t) return;
  document.getElementById('chat').innerHTML+='<div class="msg"><b>Senhor:</b> '+t+'</div>';
  document.getElementById('inp').value='';
  document.getElementById('chat').innerHTML+='<div class="msg pensando" id="pensando"><b>SEXTA-FEIRA:</b> Pensando, Senhor... 🤔</div>';
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
window.onload=()=>{ setTimeout(()=>falar('Bom dia, Senhor. Todos os sistemas operacionais. Agora eu tenho minha voz de verdade.'), 1000); }
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
    print(f"NEXUS V23 online - Voz Sexta-Feira Real - Porta {port}")
    app.run(host='0.0.0.0', port=port)