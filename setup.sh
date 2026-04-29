#!/bin/bash

echo "🚀 --- Instalando dependências do StudyBot ---"

# Atualiza o pip
python -m pip install --upgrade pip

# =========================
# Core do projeto
# =========================
echo "📦 Instalando bibliotecas principais..."
pip install streamlit
pip install google-generativeai

# =========================
# Utilitários usados no código
# =========================
echo "🧰 Instalando utilitários..."
pip install python-dotenv
pip install pillow

# =========================
# Extras (opcional mas já deixei pronto)
# =========================
echo "🎤 Instalando extras opcionais..."
pip install streamlit-mic-recorder SpeechRecognition

# =========================
# Boas práticas
# =========================
echo "📝 Gerando requirements.txt..."
pip freeze > requirements.txt

echo ""
echo "✅ --- Instalação concluída! ---"
echo ""
echo "▶️ Para rodar o projeto:"
echo "streamlit run app.py"
echo ""
echo "⚠️ Não esqueça de criar o arquivo .env com sua API:"
echo "GEMINI_API_KEY=sua_chave_aqui"