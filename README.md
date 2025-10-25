# Docify (Bernin)

A Flask-based web app for simple medical consultation workflows with login/registration, a dashboard to submit/update consultation forms, a FAQ page, and a chatbot endpoint with graceful fallbacks (no ML dependencies required to get started).

## Features

- User register/login (SQLite)
- Dashboard: submit and update consultation forms
- FAQ page
- Chatbot endpoint with multiple backends; defaults to a safe, no-ML fallback
- IP allowlist for incoming requests (secure by default)
- Health check endpoint at `/health`

## Requirements

- Windows (tested) or any OS with Python 3.10+
- Python 3.10+ recommended

## Quick start (no ML/AI dependencies)

This path runs the app using the simple chatbot fallback. It’s fastest to set up and works on any machine.

1) Open a terminal in the project folder

2) Create and activate a virtual environment

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

3) Install minimal packages

```powershell
python -m pip install -U pip
python -m pip install Flask==3.0.3 Flask-SQLAlchemy requests
```

4) Run the app

```powershell
python app.py
```

- App starts on http://127.0.0.1:5000
- Health: http://127.0.0.1:5000/health
- Default IP allowlist only permits 127.0.0.1; see “IP allowlist” below if you need external access.

5) Run tests (optional)

```powershell
python testsprite.py
```

All tests should pass without ML/AI libraries installed.

## Full setup (ML/AI features)

To enable RAG and model-backed chat variants you can install the full dependency set:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -U pip
python -m pip install -r requirements.txt
```

Some optional chatbot services (run in separate terminals):

- `chatbot.py` (port 5001): FAISS + Flan-T5 small via Transformers/HF Pipeline
- `chatbot2.py` (port 5002): FAISS + LoRA fine-tuned Flan-T5 (requires model files at `fine_tuning/lora_flan_t5_small/finetuned`)
- `chatbot3usingllama2formollama.py` (port 5003): FAISS + Ollama model `docify` on localhost:11434

To proxy the web app to a chatbot microservice (on 5003), run `app2.py` instead of `app.py`:

```powershell
python app2.py
```

Notes:
- These ML options are heavier and may require GPU/large downloads.
- The main `app.py` does not require them to function; it falls back safely.

## IP allowlist

The app blocks requests by default except localhost (127.0.0.1/32). Configure allowed IPs using an environment variable before starting the app:

```powershell
$env:ALLOWED_IPS = "127.0.0.1/32,192.168.1.0/24"
python app.py
```

To expose publicly (not recommended for production without hardening), you can use `0.0.0.0/0`:

```powershell
$env:ALLOWED_IPS = "0.0.0.0/0"
python app.py
```

Health endpoint `/health` is exempt from IP checks for probes/monitoring.

## Environment variables (.env supported)

- `SECRET_KEY` — Flask secret key (the app uses a fallback if not set)
- `ALLOWED_IPS` — Comma-separated CIDRs; default `127.0.0.1/32`
- `GOOGLE_API_KEY` — Optional for Gemini usage in `evaluate_different_modules.py`

You can create a `.env` file (if you install `python-dotenv`) with:

```
SECRET_KEY=change-me
ALLOWED_IPS=127.0.0.1/32
GOOGLE_API_KEY=your_key_here
```

## Data & files

- SQLite DB auto-creates at first run (`docify.db`)
- `users.csv` is exported after registration
- `query_dataset.csv` collects user messages from the chatbot
- FAISS index is stored under `faiss_index/` if you generate vectors locally

These are ignored by `.gitignore`.

## Project layout (key files)

- `app.py` — main Flask app with login, dashboard, FAQ, `/chatbot`, `/health`
- `app2.py` — same UI; proxies `/chatbot` to `http://127.0.0.1:5003/chatbot`
- `evaluate_different_modules.py` — chatbot helpers with safe fallbacks
- `vector_creator.py` — build/load FAISS index from `faq.txt`
- `chatbot*.py` — optional chatbot microservices (ports 5001/5002/5003)
- `templates/` — Jinja templates (index, dashboard, login, register, etc.)
- `testsprite.py` — endpoint tests using Flask test client
- `requirements.txt` — full dependency list (ML/AI heavy)

## Troubleshooting

- 403 on routes: your IP is not allowed; set `ALLOWED_IPS` to include your client.
- Import errors for ML libs: they are optional unless you run the ML chatbots; install via `requirements.txt`.
- Port already in use: stop the conflicting service or change `app.run(..., port=5000)`.
- Ollama model not found: ensure Ollama is running and the `docify` model is available for the Llama-based chatbot.

## License

This project is for assessment/educational purposes.
