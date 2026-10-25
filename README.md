<div align="center">

# Galileo AI Orchestrator

**[IT](#italiano)** | **[EN](#english)**

Un orchestratore agentico a due livelli che combina i tier gratuiti di Gemini, OpenRouter e Ollama con Claude per i compiti complessi, con frontend Open WebUI e packaging Windows.

</div>

---

<a name="italiano"></a>
## Italiano

### Perche esiste questo progetto

Gli strumenti AI commerciali per scrivere, leggere e implementare codice (come Claude Code, Cursor, GitHub Copilot) costano tra i 20 e i 100 dollari al mese. Per chi impara a programmare, lavora su progetti personali o vuole evitare costi fissi mensili, questa spesa rappresenta un ostacolo concreto.

**Galileo nasce da una logica ibrida e sostenibile:**
> *Usare in via prioritaria i tier gratuiti per la stragrande maggioranza dei task quotidiani, attivando modelli avanzati come Claude solo quando il compito richiede vero ragionamento architetturale o refactoring complesso.*

Sfruttando i **tier gratuiti** di Google AI Studio (Gemini), OpenRouter e Ollama in locale, affiancati opzionalmente da **Anthropic Claude**, Galileo offre un assistente desktop capace di:

- Conversare, spiegare concetti e rispondere a domande tecniche
- **Leggere codice e progetti sul PC** (`LIST_DIR`, `READ_FILE`): esplora cartelle locali, analizza codice esistente e ne spiega il funzionamento
- **Scrivere e modificare file** (`WRITE_FILE`): propone modifiche con anteprima e scrive solo dopo esplicita conferma dell'utente (ok / no)
- **Generare immagini** (`GENERATE_IMAGE`): generazione gratuita tramite Cloudflare Flux e Pollinations
- **Cercare nel workspace** (`SEARCH_WORKSPACE`): ricerca rapida per nome file o contenuto
- **Protezione automatica segreti**: rifiuta la lettura di file sensibili (.env, .pem, .key, credentials)

Non richiede abbonamenti obbligatori, garantisce la privacy offline se si usa Ollama, e include un launcher desktop Windows con controllo porte e gestione errori.

---

### Routing intelligente a due livelli (Light vs Heavy)

Galileo analizza automaticamente ogni richiesta in ingresso assegnandola al livello corretto:

```
[Richiesta Utente]
        |
        v
  Classificatore
  /            \
(Light)        (Heavy)
  |              |
  v              v
Tier Gratuito   Tier Avanzato (Claude)
(Gemini/OR/Oll) (Fallback sui gratuiti)
```

1. **Livello Light (Leggero):**
   - Richieste brevi, spiegazioni, chiacchiere generali, link/URL.
   - Richieste di servizio interne di Open WebUI (`### Task:` per la generazione automatica di titoli e tag delle chat).
   - Ordine di chiamata: **Gemini -> OpenRouter -> Ollama** (Claude solo come estrema risorsa se tutto fallisce).
   - Obiettivo: zero costi di token per le operazioni di routine.

2. **Livello Heavy (Pesante):**
   - Riconoscimento automatico di: blocchi di codice (```), percorsi locali di progetto (`C:\Users\...`, `/home/...`), prompt lunghi (> 1500 caratteri), parole chiave tecniche (debug, refactor, architettura, traceback, regex, sql, implementa, ecc.).
   - Ordine di chiamata: **Claude (Sonnet / Haiku) -> Gemini -> OpenRouter -> Ollama**.
   - Obiettivo: massima qualita di ragionamento e precisione nella scrittura di codice.

3. **Override manuale via chat:**
   - `/claude <richiesta>`: forza il livello Heavy (Claude prioritario).
   - `/free <richiesta>`: forza il livello Light (provider gratuiti prioritari).
   - `/full <richiesta>`: genera una risposta completa per esteso (disattiva temporaneamente la modalita Caveman).
   - `/caveman`: attiva o disattiva le risposte telegrafiche essenziali.
   - `/img <descrizione>`: genera un'immagine con Cloudflare Flux o Pollinations.
   - `/vid <descrizione>`: genera un video tramite Hugging Face Space ZeroGPU (sperimentale).

---

### I provider della cascata

#### 1. Claude (Anthropic) - Livello Heavy
Riservato a compiti complessi, analisi di progetti e refactoring. Modelli configurati:
```python
ANTHROPIC_MODELS = ["claude-sonnet-5-5", "claude-haiku-5-5"]
```
Richiede una chiave API su [console.anthropic.com](https://console.anthropic.com/). Se non configurata, Galileo passa direttamente ai provider gratuiti senza errori.

#### 2. Gemini (Google AI Studio) - Provider gratuito principale
Tier gratuito con rate limit generosi:
```python
GEMINI_MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash"]
```
Ottieni la chiave gratuita su [aistudio.google.com](https://aistudio.google.com/app/apikey).

#### 3. OpenRouter - Primo fallback cloud (gratuito)
Aggrega decine di modelli open-source senza costi tramite il router automatico:
```python
OPENROUTER_MODEL = "openrouter/free"
```
Registrati su [openrouter.ai](https://openrouter.ai) e crea una chiave gratuita.

#### 4. Ollama - Fallback locale definitivo (offline)
Esegue modelli open-source sul tuo hardware senza inviare dati all'esterno:
```python
OLLAMA_MODEL = "gemma4:31b-cloud"  # oppure es. llama3.2:3b
OLLAMA_URL = "http://localhost:11434/api/chat"
```

**Installazione Ollama:**
- Windows / macOS: scarica l'installer da [ollama.ai/download](https://ollama.ai/download)
- Linux: `curl -fsSL https://ollama.ai/install.sh | sh`

**Modelli consigliati in base all'hardware:**
```bash
ollama pull llama3.2:3b      # ~2.0 GB - CPU, qualsiasi PC
ollama pull gemma2:2b        # ~1.6 GB - leggero e veloce
ollama pull llama3.1:8b      # ~4.7 GB - consigliato con GPU dedicata
```

---

### Cooldown automatico dei provider

Quando un provider restituisce un errore (limite di quota, timeout o errore di rete), Galileo imposta automaticamente un periodo di **cooldown** per quel servizio. Durante questo intervallo, le richieste successive saltano direttamente il provider temporaneamente indisponibile, evitando rallentamenti nell'esecuzione dei tool agentici.

---

### Requisiti

- Python 3.10+
- [Open WebUI](https://github.com/open-webui/open-webui) in esecuzione su `localhost:3000`
- Almeno una chiave API (Gemini o OpenRouter) o Ollama in locale

```bash
pip install flask requests pywebview
pip install gradio_client   # opzionale, solo per /vid
```

---

### Configurazione

1. **Copia il file di configurazione:**
   ```bash
   copy galileo.env.example galileo.env   # Windows
   cp galileo.env.example galileo.env     # Linux / Mac
   ```

2. **Compila `galileo.env` con le tue chiavi:**
   - `GEMINI_API_KEY`: chiave principale per i task gratuiti.
   - `ANTHROPIC_API_KEY`: facoltativa, per attivare Claude nei compiti complessi.
   - `OPENROUTER_API_KEY`: facoltativa, per il fallback cloud.
   - `CLOUDFLARE_ACCOUNT_ID` e `CLOUDFLARE_API_TOKEN`: per immagini Flux.
   - `galileo.env` e' escluso da `.gitignore` e resta sempre privato sul tuo PC.

---

### Avvio

```bash
# 1. Avvia Open WebUI (via Docker)
docker run -p 3000:8080 ghcr.io/open-webui/open-webui:main

# 2. Avvia Galileo
python galileo_app.py
```

Il launcher:
- Carica le variabili da `galileo.env` accanto al file eseguibile.
- Verifica la disponibilita della porta 5000 prima di avviare Flask.
- Attende la risposta di Open WebUI su `http://localhost:3000`.
- Apre la finestra desktop nativa (pywebview).
- In caso di errore, apre una finestra diagnostica mostrando le ultime 25 righe di `galileo_launch.log`.

---

### Build EXE (Windows)

```bash
pip install pyinstaller
pyinstaller galileo_app.spec
```

L'eseguibile verra' generato in `dist/`. Copia il tuo file `galileo.env` nella stessa cartella dell'eseguibile `galileo_app.exe`.

---

<a name="english"></a>
## English

### Why this project exists

Commercial AI coding assistants (Claude Code, Cursor, Copilot) require monthly subscriptions between $20 and $100. For students, hobbyists, and developers working on personal projects, this recurring fee creates an avoidable barrier.

**Galileo implements a practical hybrid strategy:**
> *Rely on generous free tiers for routine queries, explanations, and lightweight tasks, while seamlessly routing to Claude when a task genuinely demands complex architectural reasoning, debugging, or multi-file refactoring.*

By leveraging **free tiers** from Google AI Studio (Gemini), OpenRouter, and local offline models via Ollama, with optional support for **Anthropic Claude**, Galileo provides a self-hosted desktop assistant capable of:

- Conversational explanations and technical Q&A
- **Inspecting local projects and codebases** (`LIST_DIR`, `READ_FILE`): navigates PC directories, reads source code, and summarizes architectures
- **Safely proposing file modifications** (`WRITE_FILE`): generates previews and only writes upon explicit user approval (ok / no)
- **Generating images** (`GENERATE_IMAGE`): free image generation via Cloudflare Flux and Pollinations
- **Searching workspaces** (`SEARCH_WORKSPACE`): quick search by filename or text content
- **Automatic credential protection**: refuses to read sensitive files (.env, .pem, .key, credentials)

---

### Two-tier intelligent routing (Light vs Heavy)

Every incoming request is automatically evaluated by a lightweight classifier:

```
[User Request]
       |
       v
   Classifier
   /        \
(Light)     (Heavy)
   |           |
   v           v
Free Cascade  Advanced Tier (Claude)
(Gemini/OR)   (Failover to free tiers)
```

1. **Light Tier:**
   - Everyday questions, conceptual explanations, URLs/documentation links.
   - Open WebUI internal task calls (`### Task:` service prompts for automatic chat title and tag generation).
   - Call order: **Gemini -> OpenRouter -> Ollama** (Claude only as last resort if enabled).
   - Keeps token expenses at zero for standard usage.

2. **Heavy Tier:**
   - Triggered by: code fences (```), local project file paths (`C:\Users\...`, `/home/...`), large inputs (> 1500 chars), and technical keywords (debug, refactor, architecture, traceback, sql, regex, etc.).
   - Call order: **Claude (Sonnet / Haiku) -> Gemini -> OpenRouter -> Ollama**.
   - Ensures high reasoning quality on programming tasks.

3. **Manual Chat Commands:**
   - `/claude <prompt>`: force Heavy tier (Claude prioritized).
   - `/free <prompt>`: force Light tier (free providers prioritized).
   - `/full <prompt>`: request full verbose response (temporarily disables Caveman style).
   - `/caveman`: toggle terse telegraphic responses.
   - `/img <prompt>`: generate image via Cloudflare / Pollinations.
   - `/vid <prompt>`: experimental video generation via Hugging Face Space ZeroGPU.

---

### Provider Cascade & Cooldown

- **Claude (Anthropic)**: Configured with `claude-sonnet-5-5` and `claude-haiku-5-5`. Requires `ANTHROPIC_API_KEY`. If unconfigured, automatically skipped.
- **Gemini (Google AI Studio)**: Primary free provider (`gemini-3.5-flash-lite`, `gemini-3.8-flash`).
- **OpenRouter**: Free cloud fallback routing across open-source models (`openrouter/free`).
- **Ollama**: Local offline fallback (`localhost:11434`).
- **Automatic Cooldown**: Any provider encountering rate limits or connection errors is placed on temporary cooldown to prevent blocking multi-step agent actions.

---

### Quick Start

```bash
# 1. Copy template and configure keys
copy galileo.env.example galileo.env

# 2. Start Open WebUI
docker run -p 3000:8080 ghcr.io/open-webui/open-webui:main

# 3. Launch Galileo
python galileo_app.py
```

### License

MIT
