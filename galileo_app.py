import os
import sys
import time
import html
import socket
import logging
import threading
import traceback

# --- cartella base: accanto all exe (o allo script) ---
BASE_DIR = (os.path.dirname(sys.executable) if getattr(sys, "frozen", False)
            else os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE_DIR)
LOG_PATH = os.path.join(BASE_DIR, "galileo_launch.log")

# senza console stdout/stderr sono None: li giro sul log
_log_stream = None
if sys.stdout is None or sys.stderr is None:
    _log_stream = open(LOG_PATH, "a", encoding="utf-8")
    if sys.stdout is None:
        sys.stdout = _log_stream
    if sys.stderr is None:
        sys.stderr = _log_stream

logging.basicConfig(filename=LOG_PATH, level=logging.INFO, force=True, encoding="utf-8",
                    format="%(asctime)s %(levelname)s: %(message)s")
logging.getLogger("werkzeug").setLevel(logging.ERROR)
log = logging.getLogger("galileo_launcher")

def load_env_file(path):
    """Legge KEY=VALUE da galileo.env senza sovrascrivere variabili gia impostate."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))

load_env_file(os.path.join(BASE_DIR, "galileo.env"))

import requests
import webview

IMPORT_ERROR = None
try:
    from galileo_server import app as flask_app
except Exception:
    flask_app = None
    IMPORT_ERROR = traceback.format_exc()

UI_URL = "http://localhost:3000"
UI_PORT = 3000
SERVER_PORT = 5000

def port_open(port, host="127.0.0.1"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex((host, port)) == 0

def run_flask_server():
    try:
        log.info("Avvio server Flask sulla porta %s", SERVER_PORT)
        flask_app.run(host="127.0.0.1", port=SERVER_PORT, debug=False, use_reloader=False)
    except Exception:
        log.error("Server Flask terminato:\n%s", traceback.format_exc())

def wait_for(port, timeout, thread=None):
    start = time.time()
    while time.time() - start < timeout:
        if thread is not None and not thread.is_alive():
            return False
        if port_open(port):
            return True
        time.sleep(0.5)
    return False

def show_error(title, detail):
    tail = ""
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, encoding="utf-8", errors="replace") as f:
            tail = "".join(f.readlines()[-25:])
    body = (
        "<body style='font-family:sans-serif;padding:1.5rem'>"
        f"<h2>{html.escape(title)}</h2><p>{html.escape(detail)}</p>"
        f"<pre style='background:#eee;padding:1rem;white-space:pre-wrap'>{html.escape(tail)}</pre>"
        f"<p>Log completo: {html.escape(LOG_PATH)}</p></body>"
    )
    webview.create_window("Galileo - errore", html=body, width=900, height=600)
    webview.start()

if __name__ == "__main__":
    if flask_app is None:
        log.error("Import di galileo_server fallito:\n%s", IMPORT_ERROR)
        show_error("Impossibile caricare il server", "Errore durante l import di galileo_server.")
        sys.exit(1)

    if port_open(SERVER_PORT):
        log.error("Porta %s gia occupata", SERVER_PORT)
        show_error("Porta 5000 gia occupata",
                   "Un altro programma (forse un altra copia di Galileo) usa gia la porta 5000.")
        sys.exit(1)

    server_thread = threading.Thread(target=run_flask_server, daemon=True)
    server_thread.start()

    if not wait_for(SERVER_PORT, 30, server_thread):
        show_error("Il server interno non e partito", "Ultime righe del log:")
        sys.exit(1)

    if not wait_for(UI_PORT, 60):
        show_error("Open WebUI non risponde su localhost:3000",
                   "Galileo e attivo, ma Open WebUI no. Avvialo (Docker o servizio) e riapri.")
        sys.exit(1)

    webview.create_window("Galileo AI - Open WebUI", UI_URL, width=1200, height=800,
                          resizable=True, min_size=(800, 600))
    webview.start()
