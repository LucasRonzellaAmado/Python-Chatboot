import streamlit as st
from google import genai
from google.genai import types
import uuid
import os
import logging
import base64
from dotenv import load_dotenv
import random
from PIL import Image
import io
import json

BOT_NOME = "StudyBot"
BOT_DESCRICAO = "Seu assistente de estudos com IA — explica, debate e te testa para fixar o conteúdo."

MENSAGEM_BOAS_VINDAS = """Olá! Sou o **StudyBot** 🎓

Fui criado para te ajudar a **realmente aprender** — não só receber respostas, mas fixar o conteúdo de verdade.

**Como funciona:**
- Pergunte qualquer coisa e eu explico de forma clara
- Após a explicação, posso te **testar com perguntas** para fixar o conteúdo
- Use `/quizme` a qualquer momento para gerar um quiz sobre o que conversamos
- Os **tópicos que você estudou** ficam salvos na barra lateral

**Dica:** depois de qualquer explicação, tente responder: _"me faz 3 perguntas sobre isso"_ — você vai aprender muito mais rápido! 🚀"""

SUGESTOES = [
    "📐  Explique o Teorema de Pitágoras com exemplos",
    "⚗️  Como funciona uma reação química de oxirredução?",
    "🧬  O que é DNA e como ele guarda informação?",
    "📜  Me explique a Revolução Francesa resumidamente",
    "💻  O que é recursão em programação?",
    "🌍  Como funciona o efeito estufa?",
    "📊  Explique média, mediana e moda",
    "🔋  Como funciona uma bateria de íon-lítio?",
]

COMANDOS_AJUDA = """
<div style="
    background: linear-gradient(135deg, #0f2027, #1a2a1a);
    border: 1px solid rgba(34,197,94,0.3);
    border-radius: 16px;
    padding: 24px;
    margin: 8px 0;
">
    <div style="font-size:18px;font-weight:600;color:#86efac;margin-bottom:6px;">⚡ Comandos do StudyBot</div>
    <div style="font-size:12px;color:#94a3b8;margin-bottom:18px;">Digite qualquer um desses comandos no chat</div>
    <div style="display:flex;flex-direction:column;gap:10px;">
        <div style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);border-radius:12px;padding:12px 16px;display:flex;align-items:center;gap:12px;">
            <span style="background:rgba(34,197,94,0.2);color:#86efac;font-family:monospace;font-size:13px;padding:4px 10px;border-radius:8px;min-width:90px;text-align:center;">/quizme</span>
            <span style="color:#cbd5e1;font-size:13px;">Gera um quiz com 3 perguntas sobre o que conversamos</span>
        </div>
        <div style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);border-radius:12px;padding:12px 16px;display:flex;align-items:center;gap:12px;">
            <span style="background:rgba(34,197,94,0.2);color:#86efac;font-family:monospace;font-size:13px;padding:4px 10px;border-radius:8px;min-width:90px;text-align:center;">/resumir</span>
            <span style="color:#cbd5e1;font-size:13px;">Resume os pontos principais estudados nesta conversa</span>
        </div>
        <div style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);border-radius:12px;padding:12px 16px;display:flex;align-items:center;gap:12px;">
            <span style="background:rgba(34,197,94,0.2);color:#86efac;font-family:monospace;font-size:13px;padding:4px 10px;border-radius:8px;min-width:90px;text-align:center;">/simplificar</span>
            <span style="color:#cbd5e1;font-size:13px;">Reexplica o último conteúdo de forma mais simples</span>
        </div>
        <div style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);border-radius:12px;padding:12px 16px;display:flex;align-items:center;gap:12px;">
            <span style="background:rgba(34,197,94,0.2);color:#86efac;font-family:monospace;font-size:13px;padding:4px 10px;border-radius:8px;min-width:90px;text-align:center;">/aprofundar</span>
            <span style="color:#cbd5e1;font-size:13px;">Vai mais fundo no último assunto explicado</span>
        </div>
        <div style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);border-radius:12px;padding:12px 16px;display:flex;align-items:center;gap:12px;">
            <span style="background:rgba(34,197,94,0.2);color:#86efac;font-family:monospace;font-size:13px;padding:4px 10px;border-radius:8px;min-width:90px;text-align:center;">/exemplo</span>
            <span style="color:#cbd5e1;font-size:13px;">Pede mais exemplos práticos sobre o último assunto</span>
        </div>
        <div style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);border-radius:12px;padding:12px 16px;display:flex;align-items:center;gap:12px;">
            <span style="background:rgba(34,197,94,0.2);color:#86efac;font-family:monospace;font-size:13px;padding:4px 10px;border-radius:8px;min-width:90px;text-align:center;">/limpar</span>
            <span style="color:#cbd5e1;font-size:13px;">Apaga as mensagens da conversa atual</span>
        </div>
        <div style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);border-radius:12px;padding:12px 16px;display:flex;align-items:center;gap:12px;">
            <span style="background:rgba(34,197,94,0.2);color:#86efac;font-family:monospace;font-size:13px;padding:4px 10px;border-radius:8px;min-width:90px;text-align:center;">/ajuda</span>
            <span style="color:#cbd5e1;font-size:13px;">Mostra esta lista de comandos</span>
        </div>
    </div>
</div>
"""

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)
load_dotenv()

st.set_page_config(page_title=BOT_NOME, page_icon="🎓", layout="wide")

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)
MODELOS_DISPONIVEIS = ["models/gemini-2.5-flash", "models/gemini-2.0-flash"]

for key, default in {
    "chats": {},
    "current_chat_id": None,
    "user_profile": {"nome": "", "nivel": "Intermediário"},
    "edit_profile": False,
    "delete_confirm": None,
    "pending_image": None,
    "show_uploader": False,
    "sugestao_clicada": None,
    "show_search": False,
    "quiz_ativo": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

def criar_chat(is_first=False):
    chat_id = str(uuid.uuid4())
    st.session_state.chats[chat_id] = {
        "name": "Nova conversa",
        "messages": [],
        "topicos": [],
        "updated_at": uuid.uuid4().hex,
        "is_first": is_first,
    }
    st.session_state.current_chat_id = chat_id
    st.session_state.quiz_ativo = None
    return chat_id


def deletar_chat(chat_id):
    del st.session_state.chats[chat_id]
    if st.session_state.current_chat_id == chat_id:
        st.session_state.current_chat_id = None
        st.session_state.quiz_ativo = None


def auto_rename(chat, primeira_msg):
    chat["name"] = primeira_msg[:32].strip() + ("..." if len(primeira_msg) > 32 else "")


def image_to_base64(b):
    return base64.b64encode(b).decode("utf-8")


def get_last_assistant(messages):
    for m in reversed(messages):
        if m["role"] == "assistant":
            return m["content"]
    return None


def build_system_instruction() -> str:
    perfil = st.session_state.user_profile
    nivel = perfil.get("nivel", "Intermediário")
    nome = perfil.get("nome", "")

    nivel_map = {
        "Iniciante": "Use linguagem muito simples, evite jargões e use muitas analogias do dia a dia.",
        "Intermediário": "Use linguagem clara e acessível, com exemplos práticos. Pode usar termos técnicos com breve explicação.",
        "Avançado": "Use linguagem técnica e aprofundada. Assuma que o usuário tem base sólida no assunto.",
    }

    partes = [
        f"Você é o {BOT_NOME}, um assistente especializado em ensino e aprendizado.",
        "Seu objetivo é explicar conteúdos de forma didática e depois SEMPRE incentivar o usuário a fixar o conhecimento.",
        f"Nível do usuário: {nivel}. {nivel_map.get(nivel, '')}",
        "Após explicar um assunto, SEMPRE termine sua resposta sugerindo ao usuário que teste o conhecimento com uma frase como: 'Quer que eu te faça algumas perguntas para fixar? Use /quizme!' ou variações naturais dessa frase.",
        "Quando o usuário responder perguntas do quiz, avalie a resposta com encorajamento, corrija gentilmente se errado e explique o motivo.",
        "Responda sempre em português do Brasil.",
    ]
    if nome:
        partes.append(f"O usuário se chama {nome}. Chame-o pelo nome ocasionalmente.")
    return " ".join(partes)


def extrair_topico_da_mensagem(msg: str) -> str | None:
    prompt = (
        f"A seguinte mensagem é uma pergunta ou pedido de explicação sobre algum assunto? "
        f"Se sim, responda APENAS com o nome do tópico em 2 a 4 palavras (ex: 'Teorema de Pitágoras', 'Fotossíntese', 'Recursão em Python'). "
        f"Se não for uma pergunta de estudo, responda exatamente: NAO\n\nMensagem: {msg}"
    )
    for modelo in MODELOS_DISPONIVEIS:
        try:
            resp = client.models.generate_content(model=modelo, contents=[{"role": "user", "parts": [{"text": prompt}]}])
            texto = resp.text.strip()
            if texto.upper() == "NAO" or not texto:
                return None
            return texto[:50]
        except Exception:
            pass
    return None

def gerar_quiz(historico_texto: str) -> list[dict] | None:
    prompt = f"""Com base na seguinte conversa de estudo, crie exatamente 3 perguntas de múltipla escolha para testar o conhecimento do usuário.

Conversa:
{historico_texto}

Responda APENAS com um JSON válido neste formato exato (sem markdown, sem texto extra):
[
  {{
    "pergunta": "texto da pergunta",
    "opcoes": ["A) opção 1", "B) opção 2", "C) opção 3", "D) opção 4"],
    "resposta_correta": 0,
    "explicacao": "por que essa é a resposta certa"
  }}
]

Onde resposta_correta é o índice (0=A, 1=B, 2=C, 3=D) da alternativa correta."""

    for modelo in MODELOS_DISPONIVEIS:
        try:
            resp = client.models.generate_content(
                model=modelo,
                contents=[{"role": "user", "parts": [{"text": prompt}]}]
            )
            texto = resp.text.strip().replace("```json", "").replace("```", "").strip()
            perguntas = json.loads(texto)
            if isinstance(perguntas, list) and len(perguntas) > 0:
                return perguntas
        except Exception as e:
            logger.error(f"Erro ao gerar quiz ({modelo}): {e}")
    return None

def gerar_resposta_simples(prompt_texto: str) -> str | None:
    system = build_system_instruction()
    for modelo in MODELOS_DISPONIVEIS:
        try:
            stream = client.models.generate_content_stream(
                model=modelo,
                contents=[{"role": "user", "parts": [{"text": prompt_texto}]}],
                config=types.GenerateContentConfig(system_instruction=system)
            )
            resposta, placeholder = "", st.empty()
            for chunk in stream:
                if chunk.text:
                    resposta += chunk.text
                    placeholder.markdown(resposta + "▌")
            if resposta:
                placeholder.markdown(resposta)
                return resposta
        except Exception as e:
            logger.error(f"Erro ({modelo}): {e}")
    return None


def gerar_resposta_com_historico(historico: list) -> tuple[str | None, str | None]:
    system = build_system_instruction()
    placeholder = st.empty()
    placeholder.markdown("💭 _Pensando..._")

    for modelo in MODELOS_DISPONIVEIS:
        try:
            resposta = ""
            stream = client.models.generate_content_stream(
                model=modelo,
                contents=historico,
                config=types.GenerateContentConfig(system_instruction=system)
            )
            for chunk in stream:
                if chunk.text:
                    resposta += chunk.text
                    placeholder.markdown(resposta + "▌")
            if resposta:
                placeholder.markdown(resposta)
                return resposta, None
        except Exception as e:
            logger.error(f"Erro ({modelo}): {e}")
            err = str(e).upper()
            if "429" in err or "QUOTA" in err or "RESOURCE_EXHAUSTED" in err:
                msg = "⏳ **Calma aí!** Atingi o limite de mensagens por minuto. Aguarda ~20 segundos e tenta de novo!"
            elif "503" in err or "UNAVAILABLE" in err:
                msg = "☁️ **Servidor ocupado.** Tenta novamente em alguns segundos!"
            else:
                msg = "😕 **Algo deu errado.** Tenta enviar de novo. Se persistir, verifique a chave de API."
            if modelo == MODELOS_DISPONIVEIS[-1]:
                placeholder.markdown(msg)
                return None, msg
    return None, "😕 Falha de conexão. Verifique sua chave de API."

def normalizar_comando(texto: str) -> tuple[str, str]:
    texto = texto.strip()
    if texto.startswith("/ "):
        texto = "/" + texto[2:]
    partes = texto.split(" ", 1)
    return partes[0].lower(), (partes[1].strip() if len(partes) > 1 else "")

def render_mensagem(message, inicial):
    if message["role"] == "user":
        content = message["content"]
        extra = ""
        if message.get("image"):
            img_data = base64.b64decode(message["image"])
            img = Image.open(io.BytesIO(img_data))
            st.markdown(f"""
            <div style="display:flex;justify-content:flex-end;align-items:flex-end;gap:10px;margin:12px 0;">
                <div style="max-width:70%;background:linear-gradient(135deg,#166534,#15803d);color:white;padding:12px 18px;border-radius:18px 18px 4px 18px;font-size:14px;line-height:1.7;box-shadow:0 4px 24px rgba(34,197,94,0.35);">
                    <em style="opacity:0.8;font-size:12px;">📎 imagem anexada</em><br>{content}
                </div>
                <div style="width:36px;height:36px;background:linear-gradient(135deg,#166534,#15803d);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:600;color:white;flex-shrink:0;">{inicial}</div>
            </div>
            """, unsafe_allow_html=True)
            st.image(img, width=250)
            return
        st.markdown(f"""
        <div style="display:flex;justify-content:flex-end;align-items:flex-end;gap:10px;margin:12px 0;">
            <div style="max-width:70%;background:linear-gradient(135deg,#166534,#15803d);color:white;padding:12px 18px;border-radius:18px 18px 4px 18px;font-size:14px;line-height:1.7;box-shadow:0 4px 24px rgba(34,197,94,0.35);">{content}</div>
            <div style="width:36px;height:36px;background:linear-gradient(135deg,#166534,#15803d);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:600;color:white;flex-shrink:0;">{inicial}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        if message.get("html"):
            st.markdown(f"""
            <div style="display:flex;justify-content:flex-start;align-items:flex-start;gap:10px;margin:12px 0;">
                <div style="width:36px;height:36px;background:linear-gradient(135deg,#0f2027,#1a3a1a);border:1px solid rgba(34,197,94,0.4);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;">🎓</div>
                <div style="max-width:75%;">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display:flex;justify-content:flex-start;align-items:flex-end;gap:10px;margin:12px 0;">
                <div style="width:36px;height:36px;background:linear-gradient(135deg,#0f2027,#1a3a1a);border:1px solid rgba(34,197,94,0.4);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;">🎓</div>
                <div style="max-width:75%;background:#0f1f0f;border:1px solid rgba(34,197,94,0.25);color:#e2e8f0;padding:12px 18px;border-radius:18px 18px 18px 4px;font-size:14px;line-height:1.7;box-shadow:0 4px 20px rgba(34,197,94,0.1);">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

def processar_comando(prompt_raw, current_chat) -> bool:
    comando, argumento = normalizar_comando(prompt_raw)

    if comando == "/ajuda":
        current_chat["messages"].append({"role": "user", "content": prompt_raw})
        current_chat["messages"].append({"role": "assistant", "content": COMANDOS_AJUDA, "html": True})
        current_chat["updated_at"] = uuid.uuid4().hex
        return True

    if comando == "/limpar":
        current_chat["messages"] = []
        current_chat["topicos"] = []
        current_chat["name"] = "Nova conversa"
        current_chat["is_first"] = True
        current_chat["updated_at"] = uuid.uuid4().hex
        st.session_state.quiz_ativo = None
        return True

    if comando == "/resumir":
        if not current_chat["messages"]:
            st.warning("Ainda não há conteúdo para resumir.")
            return True
        current_chat["messages"].append({"role": "user", "content": prompt_raw})
        texto = "\n".join([
            f"{'Usuário' if m['role'] == 'user' else 'Bot'}: {m['content']}"
            for m in current_chat["messages"] if not m["content"].startswith("/")
        ])
        with st.chat_message("assistant"):
            r = gerar_resposta_simples(
                f"Faça um resumo dos principais conceitos estudados nesta conversa, em tópicos claros:\n\n{texto}"
            )
            if r:
                current_chat["messages"].append({"role": "assistant", "content": r})
                current_chat["updated_at"] = uuid.uuid4().hex
        return True

    if comando == "/simplificar":
        ultima = get_last_assistant(current_chat["messages"])
        if not ultima:
            st.warning("Não há explicação anterior para simplificar.")
            return True
        current_chat["messages"].append({"role": "user", "content": prompt_raw})
        with st.chat_message("assistant"):
            r = gerar_resposta_simples(
                f"Reexplique o conteúdo abaixo de forma muito mais simples, como se fosse para uma criança de 12 anos, usando analogias do dia a dia:\n\n{ultima}"
            )
            if r:
                current_chat["messages"].append({"role": "assistant", "content": r})
                current_chat["updated_at"] = uuid.uuid4().hex
        return True

    if comando == "/aprofundar":
        ultima = get_last_assistant(current_chat["messages"])
        if not ultima:
            st.warning("Não há conteúdo anterior para aprofundar.")
            return True
        current_chat["messages"].append({"role": "user", "content": prompt_raw})
        with st.chat_message("assistant"):
            r = gerar_resposta_simples(
                f"Aprofunde o seguinte conteúdo com mais detalhes técnicos, conceitos relacionados e aplicações avançadas:\n\n{ultima}"
            )
            if r:
                current_chat["messages"].append({"role": "assistant", "content": r})
                current_chat["updated_at"] = uuid.uuid4().hex
        return True

    if comando == "/exemplo":
        ultima = get_last_assistant(current_chat["messages"])
        if not ultima:
            st.warning("Não há conteúdo anterior para exemplificar.")
            return True
        current_chat["messages"].append({"role": "user", "content": prompt_raw})
        with st.chat_message("assistant"):
            r = gerar_resposta_simples(
                f"Dê 3 exemplos práticos e diferentes do mundo real que ilustrem bem o seguinte conteúdo:\n\n{ultima}"
            )
            if r:
                current_chat["messages"].append({"role": "assistant", "content": r})
                current_chat["updated_at"] = uuid.uuid4().hex
        return True

    if comando == "/quizme":
        if not current_chat["messages"]:
            st.warning("Ainda não estudamos nada aqui! Faça uma pergunta primeiro 😊")
            return True
        current_chat["messages"].append({"role": "user", "content": prompt_raw})

        with st.chat_message("assistant"):
            loading = st.empty()
            loading.markdown("📝 _Preparando seu quiz..._")

            historico_texto = "\n".join([
                f"{'Usuário' if m['role'] == 'user' else 'Bot'}: {m['content']}"
                for m in current_chat["messages"]
                if not m["content"].startswith("/") and not m.get("html")
            ])
            perguntas = gerar_quiz(historico_texto)

            if perguntas:
                loading.markdown("✅ **Quiz gerado!** Responda as perguntas abaixo uma por vez.")
                st.session_state.quiz_ativo = {
                    "perguntas": perguntas,
                    "indice": 0,
                    "acertos": 0,
                    "chat_id": st.session_state.current_chat_id,
                }
                current_chat["messages"].append({
                    "role": "assistant",
                    "content": f"✅ **Quiz pronto!** {len(perguntas)} perguntas sobre o que estudamos. Vamos lá!"
                })
            else:
                loading.markdown("😕 Não consegui gerar o quiz agora. Tenta novamente!")
                current_chat["messages"].append({
                    "role": "assistant",
                    "content": "😕 Não consegui gerar o quiz agora. Tenta novamente!"
                })
            current_chat["updated_at"] = uuid.uuid4().hex
        return True

    return False


def enviar_mensagem(prompt_texto, current_chat, pending_image=None):
    is_first = len(current_chat["messages"]) == 0
    msg_entry = {"role": "user", "content": prompt_texto}
    if pending_image:
        msg_entry["image"] = pending_image["b64"]
        msg_entry["mime"] = pending_image["mime"]

    current_chat["messages"].append(msg_entry)
    current_chat["updated_at"] = uuid.uuid4().hex
    current_chat["is_first"] = False

    if is_first:
        auto_rename(current_chat, prompt_texto)
        topico = extrair_topico_da_mensagem(prompt_texto)
        if topico and topico not in current_chat["topicos"]:
            current_chat["topicos"].append(topico)

    historico = []
    for m in current_chat["messages"]:
        parts = []
        if m.get("image"):
            parts.append(types.Part.from_bytes(
                data=base64.b64decode(m["image"]),
                mime_type=m.get("mime", "image/jpeg")
            ))
        parts.append({"text": m["content"]})
        historico.append({"role": m["role"], "parts": parts})

    with st.chat_message("assistant"):
        resposta, erro = gerar_resposta_com_historico(historico)
        conteudo = resposta or erro or "😕 Não obtive resposta."
        current_chat["messages"].append({"role": "assistant", "content": conteudo})
        current_chat["updated_at"] = uuid.uuid4().hex

        if not is_first:
            topico = extrair_topico_da_mensagem(prompt_texto)
            if topico and topico not in current_chat["topicos"]:
                current_chat["topicos"].append(topico)

    st.session_state.pending_image = None

if not st.session_state.chats:
    criar_chat(is_first=True)

if st.session_state.current_chat_id is None or st.session_state.current_chat_id not in st.session_state.chats:
    criar_chat()

current_chat = st.session_state.chats[st.session_state.current_chat_id]

with st.sidebar:
    st.markdown(f"## 🎓 {BOT_NOME}")
    st.markdown(f"<span style='font-size:12px;color:#86efac;'>{BOT_DESCRICAO}</span>", unsafe_allow_html=True)
    st.markdown("---")

    col_new, col_search = st.columns(2)
    with col_new:
        if st.button("＋ Nova conversa", use_container_width=True):
            criar_chat()
            st.rerun()
    with col_search:
        if st.button("🔍 Buscar", use_container_width=True):
            st.session_state.show_search = not st.session_state.show_search

    search = ""
    if st.session_state.show_search:
        search = st.text_input("Buscar conversa", placeholder="Nome ou tópico...")

    todos_topicos = []
    for c in st.session_state.chats.values():
        todos_topicos.extend(c.get("topicos", []))
    todos_topicos = list(dict.fromkeys(todos_topicos))
    if todos_topicos:
        st.markdown("### 🗺️ Tópicos estudados")
        st.markdown(
            "<div style='display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;'>" +
            "".join([
                f"<span style='background:rgba(34,197,94,0.15);border:1px solid rgba(34,197,94,0.3);"
                f"color:#86efac;font-size:11px;padding:3px 10px;border-radius:20px;'>{t}</span>"
                for t in todos_topicos[-12:]
            ]) +
            "</div>",
            unsafe_allow_html=True
        )

    st.markdown("### 💬 Conversas")

    sorted_chats = sorted(
        st.session_state.chats.items(),
        key=lambda x: x[1].get("updated_at", ""),
        reverse=True
    )

    for chat_id, chat in sorted_chats:
        if search and search.lower() not in chat["name"].lower():
            topicos_str = " ".join(chat.get("topicos", []))
            if search.lower() not in topicos_str.lower():
                continue

        is_active = chat_id == st.session_state.current_chat_id
        icon = "▶" if is_active else "☰"
        col_chat, col_del = st.columns([0.82, 0.18])

        with col_chat:
            label = f"{icon} {chat['name']}"
            if chat.get("topicos"):
                n = len(chat["topicos"])
                label += f" · {n} tópico{'s' if n > 1 else ''}"
            if st.button(label, key=f"chat_{chat_id}", use_container_width=True):
                st.session_state.current_chat_id = chat_id
                st.session_state.quiz_ativo = None
                st.session_state.pending_image = None
                st.session_state.delete_confirm = None
                st.rerun()

        with col_del:
            if st.session_state.delete_confirm == chat_id:
                if st.button("✓", key=f"confirm_{chat_id}", use_container_width=True):
                    deletar_chat(chat_id)
                    st.session_state.delete_confirm = None
                    st.rerun()
            else:
                if st.button("🗑", key=f"del_{chat_id}", use_container_width=True):
                    st.session_state.delete_confirm = chat_id
                    st.rerun()

    st.markdown("---")

    st.markdown("""
    <style>
    .profile-box { margin-top: auto; padding: 16px 12px; border-top: 1px solid rgba(34,197,94,0.2); }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<div class="profile-box">', unsafe_allow_html=True)
    perfil = st.session_state.user_profile

    if not st.session_state.edit_profile:
        label = f"👤 {perfil['nome']}" if perfil["nome"] else "👤 Configurar perfil"
        if st.button(label, use_container_width=True):
            st.session_state.edit_profile = True
            st.rerun()
        if perfil["nome"]:
            st.markdown(f"<span style='font-size:12px;opacity:0.6;'>Nível: {perfil['nivel']}</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='font-size:11px;opacity:0.5;'>Configure seu nível para explicações personalizadas</span>", unsafe_allow_html=True)
    else:
        novo_nome = st.text_input("Seu nome", value=perfil["nome"], placeholder="Como posso te chamar?")
        novo_nivel = st.selectbox(
            "Seu nível de conhecimento",
            ["Iniciante", "Intermediário", "Avançado"],
            index=["Iniciante", "Intermediário", "Avançado"].index(perfil["nivel"]),
            help="Iniciante = explicações simples | Avançado = linguagem técnica"
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Salvar", use_container_width=True):
                st.session_state.user_profile = {"nome": novo_nome, "nivel": novo_nivel}
                st.session_state.edit_profile = False
                st.rerun()
        with c2:
            if st.button("Cancelar", use_container_width=True):
                st.session_state.edit_profile = False
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


current_chat = st.session_state.chats[st.session_state.current_chat_id]
nome_usuario = st.session_state.user_profile.get("nome", "") or "U"
inicial = nome_usuario[0].upper()

quiz = st.session_state.quiz_ativo
if quiz and quiz.get("chat_id") == st.session_state.current_chat_id:
    idx = quiz["indice"]
    perguntas = quiz["perguntas"]

    if idx < len(perguntas):
        q = perguntas[idx]
        st.markdown("---")
        progresso = idx / len(perguntas)
        st.progress(progresso, text=f"Pergunta {idx + 1} de {len(perguntas)}")

        st.markdown(f"""
        <div style="background:#0f1f0f;border:1px solid rgba(34,197,94,0.4);border-radius:16px;padding:20px;margin:12px 0;">
            <div style="color:#86efac;font-size:13px;font-weight:600;margin-bottom:10px;">📝 PERGUNTA {idx+1}</div>
            <div style="color:#f1f5f9;font-size:16px;line-height:1.6;">{q['pergunta']}</div>
        </div>
        """, unsafe_allow_html=True)

        for i, opcao in enumerate(q["opcoes"]):
            if st.button(opcao, key=f"quiz_opt_{idx}_{i}", use_container_width=True):
                acertou = (i == q["resposta_correta"])
                if acertou:
                    quiz["acertos"] += 1
                    feedback = f"✅ **Correto!** {q['explicacao']}"
                else:
                    correta = q["opcoes"][q["resposta_correta"]]
                    feedback = f"❌ **Não foi dessa vez.** A resposta certa era **{correta}**. {q['explicacao']}"

                current_chat["messages"].append({"role": "user", "content": f"[Quiz] {opcao}"})
                current_chat["messages"].append({"role": "assistant", "content": feedback})
                current_chat["updated_at"] = uuid.uuid4().hex
                quiz["indice"] += 1

                if quiz["indice"] >= len(perguntas):
                    acertos = quiz["acertos"]
                    total = len(perguntas)
                    pct = int(acertos / total * 100)
                    if pct == 100:
                        resultado = f"🏆 **Perfeito! {acertos}/{total} ({pct}%)** — Você dominou o assunto!"
                    elif pct >= 66:
                        resultado = f"🌟 **Muito bem! {acertos}/{total} ({pct}%)** — Boa compreensão! Revise os erros e refaça com `/quizme`."
                    else:
                        resultado = f"📖 **{acertos}/{total} ({pct}%)** — Vale revisar o conteúdo e tentar de novo com `/quizme`!"
                    current_chat["messages"].append({"role": "assistant", "content": resultado})
                    st.session_state.quiz_ativo = None

                st.rerun()
        st.markdown("---")

elif not current_chat["messages"]:
    if current_chat.get("is_first"):
        st.markdown(f"""
        <div style="text-align:center;margin-top:50px;margin-bottom:28px;">
            <div style="font-size:52px;margin-bottom:12px;">🎓</div>
            <h1 style="font-size:30px;margin-bottom:8px;">{BOT_NOME}</h1>
            <p style="color:#86efac;font-size:15px;max-width:480px;margin:0 auto;">{BOT_DESCRICAO}</p>
        </div>
        """, unsafe_allow_html=True)
        render_mensagem({"role": "assistant", "content": MENSAGEM_BOAS_VINDAS}, "🎓")
    else:
        st.markdown("""
        <div style="text-align:center;margin-top:80px;margin-bottom:24px;">
            <div style="font-size:40px;">📚</div>
            <p style="color:#86efac;font-size:16px;margin-top:8px;">Sobre qual assunto quer estudar hoje?</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<p style='text-align:center;color:#64748b;font-size:13px;margin:16px 0 10px;'>Escolha um tema para começar:</p>", unsafe_allow_html=True)
    sugestoes = random.sample(SUGESTOES, 4)
    cols = st.columns(2)
    for i, s in enumerate(sugestoes):
        with cols[i % 2]:
            label = s.split("  ", 1)[-1] if "  " in s else s
            if st.button(s, key=f"sug_{i}", use_container_width=True):
                st.session_state.sugestao_clicada = label

else:
    col_title, col_tags = st.columns([0.5, 0.5])
    with col_title:
        st.markdown(f"## {current_chat['name']}")
    with col_tags:
        if current_chat.get("topicos"):
            tags_html = " ".join([
                f"<span style='background:rgba(34,197,94,0.15);border:1px solid rgba(34,197,94,0.3);"
                f"color:#86efac;font-size:11px;padding:2px 8px;border-radius:12px;'>{t}</span>"
                for t in current_chat["topicos"][-5:]
            ])
            st.markdown(f"<div style='padding-top:12px;'>{tags_html}</div>", unsafe_allow_html=True)
    st.divider()
    for message in current_chat["messages"]:
        render_mensagem(message, inicial)
if st.session_state.pending_image and not quiz:
    st.markdown("**📎 Imagem pronta para enviar:**")
    img = Image.open(io.BytesIO(base64.b64decode(st.session_state.pending_image["b64"])))
    c1, c2 = st.columns([0.15, 0.85])
    with c1:
        st.image(img, width=80)
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✕ Remover"):
            st.session_state.pending_image = None
            st.rerun()
if not (quiz and quiz.get("chat_id") == st.session_state.current_chat_id):
    col_attach, col_input = st.columns([0.05, 0.95])
    with col_attach:
        if st.button("📎", help="Anexar imagem", use_container_width=True):
            st.session_state.show_uploader = not st.session_state.show_uploader
            st.rerun()
    with col_input:
        prompt = st.chat_input("Pergunte algo para estudar... (ou /ajuda)")

    if st.session_state.show_uploader:
        up = st.file_uploader("Imagem (PNG, JPG, WEBP, GIF)", type=["png", "jpg", "jpeg", "webp", "gif"],
                              key="img_up", label_visibility="visible")
        if up:
            b64 = image_to_base64(up.read())
            st.session_state.pending_image = {"b64": b64, "mime": up.type, "name": up.name}
            st.session_state.show_uploader = False
            st.rerun()
else:
    prompt = None

texto = None
if st.session_state.sugestao_clicada:
    texto = st.session_state.sugestao_clicada
    st.session_state.sugestao_clicada = None
elif prompt:
    texto = prompt.strip()

if texto:
    is_cmd = texto.startswith("/") or texto.startswith("/ ")
    if is_cmd:
        ok = processar_comando(texto, current_chat)
        if ok:
            st.rerun()
        else:
            cmd, _ = normalizar_comando(texto)
            st.warning(f"Comando **{cmd}** não encontrado. Digite `/ajuda` para ver os disponíveis.")
    else:
        enviar_mensagem(texto, current_chat, st.session_state.pending_image)
        st.rerun()