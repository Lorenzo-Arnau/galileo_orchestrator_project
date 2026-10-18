<div align="center">

# Galileo AI Orchestrator

**[IT](#italiano)** | **[EN](#english)**

Un orchestratore agentico che combina API LLM gratuite in cascata,
con frontend Open WebUI e packaging nativo per Windows.

</div>

---

<a name="italiano"></a>
## Italiano

### Perché esiste questo progetto

Gli strumenti AI più potenti per scrivere, leggere e implementare codice —
Claude Code, Cursor, GitHub Copilot, Antigravity — costano tra i 20 e i 100 dollari al mese.
Per chi impara a programmare, per chi lavora su progetti personali, per chi semplicemente
non può o non vuole spendere quella cifra ogni mese, la barriera è reale.

**Galileo nasce da questa idea semplice:**
> *E se si potesse avere uno strumento simile, completamente gratuito, che gira sul tuo PC?*

Usando i **tier gratuiti** di Google AI Studio (Gemini), OpenRouter e — per chi ha una
macchina abbastanza potente — Ollama in locale, Galileo offre un assistente AI capace di:

- Conversare, spiegare, rispondere a domande tecniche e non
- **Leggere i tuoi file e il tuo codice** — puoi indicargli una cartella di progetto
  e lui la esplora, legge i file rilevanti e ti aiuta a capire cosa fa quel codice
- **Scrivere e modificare file** — propone le modifiche e le applica solo dopo la tua conferma
- **Generare immagini** gratis con Cloudflare Flux
- **Cercare nel workspace** — trova file per nome o contenuto

Non richiede abbonamenti, non manda i tuoi dati a server proprietari se usi Ollama,
e funziona con un doppio clic su Windows grazie all'exe precompilato.

È uno strumento per chi vuole **fare cose concrete con l'AI senza spendere soldi**.

---

### Cos'è Galileo (tecnico)

Galileo è un server Flask che espone un'API compatibile OpenAI (`/v1/chat/completions`)
e orchestra in cascata più provider LLM gratuiti:

```
Gemini  →  OpenRouter (tier gratuito)  →  Ollama (locale)
```

Se il primo provider fallisce (quota esaurita, errore di rete, chiave non configurata),
passa automaticamente al successivo — senza che l'utente debba fare nulla.
Il frontend è [Open WebUI](https://github.com/open-webui/open-webui), aperto nativamente
tramite un launcher Windows (`pywebview`).

**Funzionalità principali:**
- Cascata automatica tra provider (failover trasparente)
- `LIST_DIR` — elenca i file di qualsiasi cartella del PC (percorso assoluto)
- `READ_FILE` — legge file locali; protegge automaticamente `.env`, `.key`, `.pem`
- `SEARCH_WORKSPACE` — cerca nel workspace per nome file o contenuto
- `WRITE_FILE` — propone scrittura di file con conferma utente
- `GENERATE_IMAGE` — Cloudflare Flux → Pollinations (cascata)
- `GENERATE_VIDEO` — Hugging Face Space ZeroGPU (sperimentale/instabile)
- Dashboard statistiche su `/dashboard`
- Modalità Caveman con `/caveman`

---

### La cascata in dettaglio

#### 1. Gemini (Google AI Studio) — provider principale
Gratuito con limiti generosi. Galileo prova i modelli configurati in ordine:

```python
# in galileo_server.py
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash"]  # provati in sequenza
```

Ottieni la chiave su [aistudio.google.com](https://aistudio.google.com/app/apikey).

#### 2. OpenRouter — primo fallback (cloud, gratuito)
Aggrega decine di modelli open-source con un unico endpoint.
Il modello `openrouter/free` seleziona automaticamente tra quelli senza costo.

```python
OPENROUTER_MODEL = "openrouter/free"   # oppure es. "meta-llama/llama-3.1-8b-instruct:free"
```

Registrati su [openrouter.ai](https://openrouter.ai) → crea una chiave gratuita.

#### 3. Ollama — fallback finale (completamente locale, offline)
Ollama fa girare modelli LLM direttamente sul tuo PC, senza inviare dati a nessun server.
È il fallback definitivo: funziona anche senza connessione internet.

**Installazione Ollama:**

```bash
# Windows / macOS: scarica l'installer da
# https://ollama.ai/download

# Linux:
curl -fsSL https://ollama.ai/install.sh | sh
```

**Scaricare un modello** (esempi, scegli in base alla VRAM disponibile):

```bash
ollama pull gemma2:2b        # ~1.6 GB  — CPU, qualsiasi PC
ollama pull llama3.2:3b      # ~2.0 GB  — CPU, qualsiasi PC
ollama pull llama3.1:8b      # ~4.7 GB  — consigliato con GPU
ollama pull qwen2.5:14b      # ~8.9 GB  — buona GPU richiesta
ollama pull gemma2:27b       # ~16 GB   — GPU high-end
```

**Verificare che sia attivo** (Ollama avvia automaticamente un server su porta 11434):

```bash
ollama list          # mostra i modelli scaricati
curl http://localhost:11434/api/tags   # risponde con JSON se il server è su
```

**Configurare il modello in Galileo:**

```python
# in galileo_server.py — scegli il modello che hai scaricato
OLLAMA_MODEL = "llama3.2:3b"           # modello locale
OLLAMA_URL   = "http://localhost:11434/api/chat"  # non cambiare
```

> **Nota:** Se Ollama non è installato o il modello non è disponibile, Galileo
> mostrerà un errore solo su questo provider e non ne avrà altri da tentare.
> È buona pratica avere almeno un modello piccolo (es. `gemma2:2b`) come rete di sicurezza.

---

### Requisiti

- Python 3.10+
- [Open WebUI](https://github.com/open-webui/open-webui) su `localhost:3000`
- Almeno una chiave API tra Gemini e OpenRouter **oppure** Ollama installato localmente

```bash
pip install flask requests pywebview
pip install gradio_client   # opzionale, solo per /vid
```

---

### Configurazione

1. **Copia il template delle chiavi:**
   ```bash
   copy galileo.env.example galileo.env   # Windows
   cp galileo.env.example galileo.env     # Linux/Mac
   ```

2. **Apri `galileo.env` e incolla le tue chiavi** (vedi commenti nel file).
   Puoi lasciare vuote le chiavi dei provider che non usi — Galileo salterà quel provider.

3. **`galileo.env` non va mai committato** — è già in `.gitignore`.

---

### Avvio

```bash
# 1. Avvia Open WebUI
docker run -p 3000:8080 ghcr.io/open-webui/open-webui:main

# 2. (Opzionale) Avvia Ollama se vuoi il fallback locale
ollama serve   # di solito parte automaticamente come servizio

# 3. Lancia Galileo
python galileo_app.py
```

Il launcher:
- Legge `galileo.env` dalla stessa cartella
- Avvia Flask su `http://127.0.0.1:5000`
- Attende Open WebUI su `http://localhost:3000` (fino a 60 s)
- Apre la finestra nativa

Se non parte, controlla **`galileo_launch.log`** (stesso folder dell'exe/script).

---

### Build EXE (Windows)

```bash
pip install pyinstaller
pyinstaller galileo_app.spec
```

L'exe finisce in `dist/`. Metti `galileo.env` **nella stessa cartella** dell'exe.

> Se `/vid` non funziona dall'exe:
> ```bash
> pyinstaller galileo_app.spec --collect-all gradio_client
> ```

---

### Struttura del progetto

```
galileo_app.py          ← Launcher (pywebview + caricamento galileo.env)
galileo_server.py       ← Server Flask + logica agente + tools
galileo_router.py       ← Router provider (opzionale)
galileo_app.spec        ← Configurazione PyInstaller
galileo.env.example     ← Template chiavi API (compilare e rinominare in galileo.env)
galileo.env             ← Chiavi reali (NON nel repo, escluso da .gitignore)
galileo_workspace/      ← Workspace agente: immagini, video, file generati
```

---

### Licenza

MIT — usa, modifica, distribuisci liberamente.

---

<a name="english"></a>
## English

### Why this project exists

The most powerful AI coding assistants — Claude Code, Cursor, GitHub Copilot, Antigravity — often cost between $20 and $100 per month.
For learners, hobbyists, students, or anyone who cannot or does not want to pay recurring monthly subscriptions, this creates an unnecessary barrier to entry.

**Galileo was born from a simple premise:**
> *What if you could have a capable, agentic AI assistant running locally on your PC, completely free of charge?*

By chaining the generous **free tiers** of Google AI Studio (Gemini), OpenRouter, and (optionally) local offline LLMs via Ollama, Galileo gives you an agent capable of:

- Conversing, explaining concepts, and answering technical questions
- **Reading your workspace and codebases** — point it to a project directory and it will inspect folders, read relevant files, and explain how things work
- **Writing and editing files** — proposes changes with safe diffs and writes only after explicit user confirmation
- **Generating images** for free via Cloudflare Flux & Pollinations
- **Searching workspaces** — quickly find files or code by query

No subscriptions, no vendor lock-in, complete privacy when running Ollama offline, and a user-friendly double-click launch on Windows thanks to the pre-packaged app launcher.

---

### What is Galileo (Technical overview)

Galileo is a Flask server exposing an OpenAI-compatible API (`/v1/chat/completions`)
that orchestrates multiple free LLM providers in an automatic cascade:

```
Gemini  →  OpenRouter (free tier)  →  Ollama (local, offline)
```

If one provider fails (quota exhausted, network error, missing key), it silently
falls over to the next. The frontend is [Open WebUI](https://github.com/open-webui/open-webui),
opened natively via a Windows launcher (`pywebview`).

**Key features:**
- Automatic provider cascade (transparent failover)
- `LIST_DIR` — list files in any local folder (absolute path)
- `READ_FILE` — read local files; auto-protects `.env`/`.key`/`.pem`
- `SEARCH_WORKSPACE` — search workspace by filename or content
- `WRITE_FILE` — proposes file writes requiring user confirmation
- `GENERATE_IMAGE` — Cloudflare Flux → Pollinations (cascade)
- `GENERATE_VIDEO` — Hugging Face Space ZeroGPU (experimental)
- Live stats dashboard at `/dashboard`
- Caveman mode (terse responses) via `/caveman`

---

### The cascade explained

#### 1. Gemini — primary provider
Free with generous limits. Galileo tries the configured models in order:

```python
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash"]
```

Get your key at [aistudio.google.com](https://aistudio.google.com/app/apikey).

#### 2. OpenRouter — first fallback (cloud, free)
Aggregates dozens of open-source models under a single endpoint.
`openrouter/free` auto-selects from available no-cost models.

```python
OPENROUTER_MODEL = "openrouter/free"
```

Sign up at [openrouter.ai](https://openrouter.ai).

#### 3. Ollama — final fallback (fully local, offline)
Runs LLM models directly on your machine — no data sent anywhere.
Works without an internet connection.

**Install Ollama:**

```bash
# Windows / macOS: download from https://ollama.ai/download
# Linux:
curl -fsSL https://ollama.ai/install.sh | sh
```

**Pull a model** (pick based on your available VRAM):

```bash
ollama pull gemma2:2b       # ~1.6 GB — runs on CPU, any machine
ollama pull llama3.2:3b     # ~2.0 GB — runs on CPU, any machine
ollama pull llama3.1:8b     # ~4.7 GB — recommended with GPU
ollama pull qwen2.5:14b     # ~8.9 GB — good GPU required
```

**Check it's running:**

```bash
ollama list                              # shows downloaded models
curl http://localhost:11434/api/tags    # returns JSON if server is up
```

**Configure the model in Galileo:**

```python
# galileo_server.py
OLLAMA_MODEL = "llama3.2:3b"
OLLAMA_URL   = "http://localhost:11434/api/chat"
```

---

### Requirements

- Python 3.10+
- [Open WebUI](https://github.com/open-webui/open-webui) on `localhost:3000`
- At least one of: a Gemini/OpenRouter key **or** Ollama installed locally

```bash
pip install flask requests pywebview
pip install gradio_client   # optional, only for /vid
```

---

### Quick start

```bash
# 1. Copy and fill in your API keys
copy galileo.env.example galileo.env   # Windows
cp galileo.env.example galileo.env     # Linux/Mac

# 2. Start Open WebUI
docker run -p 3000:8080 ghcr.io/open-webui/open-webui:main

# 3. (Optional) Start Ollama for local fallback
ollama serve

# 4. Launch Galileo
python galileo_app.py
```

---

### Build (Windows EXE)

```bash
pip install pyinstaller
pyinstaller galileo_app.spec
# Place galileo.env next to the generated exe in dist/
```

---

### License

MIT
