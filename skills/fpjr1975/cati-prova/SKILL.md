---
name: cati-prova
description: "Prepara material de estudo completo para a Catarina quando ela tem uma prova. Dado um tema e matéria, faz pesquisa automática, monta um NotebookLM completo e gera TODOS os artefatos de estudo: quiz, flashcards, podcast, vídeo, infográfico, mapa mental e slide deck — tudo pronto pra estudar. Triggers: 'tenho prova', 'prova da Cati', 'Cati tem prova', 'material de estudo', 'prepare prova', 'estudo pra prova', 'montar material', 'cati prova', 'kit de estudo', 'prova de [matéria]'. Também aciona quando a Catarina disser 'tenho prova de X', 'preciso estudar X', 'me ajuda pra prova'. Contextualiza sempre para 4º ano do ensino fundamental (9-10 anos), linguagem acessível e carinhosa."
---

# 🌙 Cati Prova — Kit de Estudo Completo

Skill de carinho: monta um kit de estudos completo pra Catarina (9 anos, 4º ano).

**Fluxo:** pesquisa → notebook → fontes → gera todos os artefatos → entrega

## Pré-check obrigatório

```bash
notebooklm auth check
# Se falhar: avisar Fafá que precisa renovar login do NotebookLM
```

## Passo 1 — Entender o pedido

Coletar (perguntar se faltar):
- **Matéria:** Ciências, História, Português, Matemática, Geografia...
- **Tema específico:** "sistema solar", "Revolução Francesa", "frações"...
- **Quando é a prova:** hoje, amanhã, em X dias (afeta profundidade da pesquisa)
- **Série:** assume 4º ano se não informado

Adaptar linguagem: sempre simples, carinhosa, para criança de 9-10 anos.

## Passo 2 — Pesquisa de fontes

```bash
# Busca web pra coletar URLs relevantes
# Priorizar: sites educativos br (.gov, .edu, portais escolares)
# Ex: brasilescola.uol.com.br, mundoeducacao.uol.com.br, educacao.uol.com.br
# YouTube: buscar vídeos didáticos infantis sobre o tema
```

Coletar 4-6 fontes de qualidade:
- 2-3 URLs de portais educativos brasileiros
- 1-2 vídeos do YouTube (didáticos, animados se possível)
- 1 texto resumido inline se o tema for muito específico

## Passo 3 — Criar e montar o notebook

```bash
# Criar com nome carinhoso
notebooklm create "📚 Prova de [MATÉRIA]: [TEMA] — Cati [DATA]"

# Setar contexto
notebooklm use <id>

# Garantir idioma PT-BR
notebooklm language set pt_BR

# Adicionar fontes uma a uma
notebooklm source add "https://url1..."
notebooklm source add "https://url2..."
notebooklm source add "https://youtube.com/watch?v=..."

# Aguardar processamento
notebooklm source wait
```

## Passo 4 — Gerar todos os artefatos

Gerar em sequência (aguardar cada um):

```bash
# 1. Quiz (perguntas de múltipla escolha pra treinar)
notebooklm generate quiz "Perguntas sobre [TEMA] para criança de 9 anos, 4º ano"

# 2. Flashcards (frente/verso pra decorar conceitos-chave)
notebooklm generate flashcards "Conceitos importantes de [TEMA] em linguagem simples"

# 3. Podcast (conversa explicativa pra ouvir)
notebooklm generate audio "Explica [TEMA] de forma divertida para criança de 9 anos" --format overview --length medium

# 4. Vídeo (explicação visual)
notebooklm generate video "Resumo visual de [TEMA] para estudantes do ensino fundamental"

# 5. Infográfico (visual bonito do conteúdo)
notebooklm generate infographic "Infográfico colorido e didático sobre [TEMA]" --style instructional

# 6. Mapa mental (organização dos conceitos)
notebooklm generate mind-map "Mapa mental de [TEMA] com conceitos principais"

# 7. Slide deck (apresentação resumida)
notebooklm generate slide-deck "Slides de estudo sobre [TEMA] para 4º ano"

# Aguardar todos os artefatos
notebooklm artifact wait
```

## Passo 5 — Download dos artefatos

```bash
# Baixar tudo pra pasta organizada
mkdir -p /tmp/cati-prova/[tema-slug]

notebooklm download quiz --output /tmp/cati-prova/[tema-slug]/quiz.json
notebooklm download flashcards --output /tmp/cati-prova/[tema-slug]/flashcards.json  
notebooklm download audio --output /tmp/cati-prova/[tema-slug]/podcast.mp3
notebooklm download video --output /tmp/cati-prova/[tema-slug]/video.mp4
notebooklm download infographic --output /tmp/cati-prova/[tema-slug]/infografico.png
notebooklm download mind-map --output /tmp/cati-prova/[tema-slug]/mapa-mental.png
notebooklm download slide-deck --output /tmp/cati-prova/[tema-slug]/slides.pdf
```

## Passo 6 — Entrega

Montar mensagem carinhosa pra Catarina com:

```
🌟 Kit de Estudos da Cati — [MATÉRIA]: [TEMA]

Oi Cati! Preparei tudo pra você arrasar na prova! 📚✨

🎙️ Podcast — ouça explicando tudo (ótimo antes de dormir!)
🎬 Vídeo — visual e divertido
❓ Quiz — teste seus conhecimentos
📇 Flashcards — ótimos pra revisar rápido
🗺️ Mapa Mental — veja tudo conectado
📊 Infográfico — resumo visual colorido
📑 Slides — resumão organizado

💪 Você vai mandar muito bem!
```

Enviar pelo **@VegaCompanionBot** diretamente pra Catarina (chat_id: 8393879368).
Enviar na ordem: podcast primeiro (mais imediato), depois vídeo, depois os visuais.

```python
import requests
TOKEN = "8208364716:AAEwO1tURypqAuEKCRUejF8d-6_QF_F0LGs"
CATI_CHAT_ID = 8393879368

# Enviar arquivo
requests.post(f"https://api.telegram.org/bot{TOKEN}/sendDocument",
    data={"chat_id": CATI_CHAT_ID, "caption": "🎙️ Teu podcast de revisão, Cati!"},
    files={"document": open("/tmp/cati-prova/[tema]/podcast.mp3", "rb")})

# Enviar mensagem
requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    json={"chat_id": CATI_CHAT_ID, "text": "📚 Kit completo chegou!"})
```

## Adaptações por matéria

| Matéria | Dicas de prompt |
|---------|----------------|
| Ciências | Enfatizar experimentos, natureza, corpo humano |
| História | Focar em personagens, datas-chave, causa e efeito |
| Geografia | Mapas, regiões, características físicas |
| Português | Regras, exemplos práticos, historinhas |
| Matemática | Evitar texto denso; priorizar quiz com cálculos visuais |

## Notas importantes

- **Tempo total:** 15-25 minutos (vídeo e podcast são mais lentos)
- **Se o notebook já existir** para esse tema: usar `notebooklm use` pelo ID salvo em vez de criar novo
- **Se auth falhar:** avisar Fafá imediatamente — sem login o fluxo inteiro trava
- **Linguagem nos prompts:** sempre mencionar "para criança de 9 anos" ou "4º ano" — muda muito a qualidade do output
- **Salvar ID do notebook** em `/tmp/cati-prova/notebooks.json` para reuso futuro
