# 🎓 StudyBot

Assistente de estudos com inteligência artificial desenvolvido em Python usando Streamlit e integração com a API Gemini.

O **StudyBot** não apenas responde perguntas — ele **ensina de verdade**. Explica conteúdos, aprofunda quando necessário e ainda te testa com quizzes para ajudar na fixação.

---

## 🚀 Tecnologias

* Python
* Streamlit
* Google Gemini API (`google-genai`)
* dotenv
* Pillow (manipulação de imagens)

---

## ⚙️ Pré-requisitos

* Python 3.10+
* Chave da API Gemini

---

## ▶️ Como executar

```bash
git clone https://github.com/LucasRonzellaAmado/ChatBoot---Python.git
cd ChatBoot---Python
pip install -r requirements.txt
streamlit run main.py
```

---

## ⚙️ Configuração

Crie um arquivo `.env` na raiz do projeto:

```
GEMINI_API_KEY=sua_chave_aqui
```

---

## 🌐 Acesso

Abra no navegador:

```
http://localhost:8501
```

---

## ✨ Funcionalidades

### 📚 Aprendizado inteligente

* Explicações adaptadas ao nível do usuário (Iniciante, Intermediário, Avançado)
* Incentivo ativo à fixação do conteúdo

### 🧠 Quiz automático

* Comando `/quizme` gera perguntas com base na conversa
* Correção automática com explicação

### 🗂️ Organização por contexto

* Múltiplas conversas
* Histórico salvo por sessão
* Tópicos estudados destacados automaticamente

### ⚡ Comandos rápidos

* `/quizme` → Gera um quiz
* `/resumir` → Resume a conversa
* `/simplificar` → Explica de forma mais simples
* `/aprofundar` → Aprofunda o conteúdo
* `/exemplo` → Mostra exemplos práticos
* `/limpar` → Limpa a conversa
* `/ajuda` → Lista de comandos

### 🖼️ Suporte a imagens

* Upload de imagens no chat
* Envio junto com perguntas

### 👤 Perfil do usuário

* Nome personalizado
* Ajuste de nível de conhecimento
* Respostas adaptadas automaticamente

### 🔍 Busca e navegação

* Busca por conversas
* Visualização de tópicos estudados

---

## 💡 Diferencial

O StudyBot segue uma abordagem ativa de aprendizado:

> Ele explica, reforça e depois testa você.

Isso ajuda muito mais na retenção do conteúdo do que apenas ler respostas.

---

## 👨‍💻 Autor

Lucas Amado
