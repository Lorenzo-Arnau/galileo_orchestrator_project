import os
import requests
import json
import sys

# CONFIGURAZIONE DELLA CASCATA
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")

MODELS = [
    {
        'name': 'Gemini',
        'url': f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}',
        'type': 'gemini'
    },
    {
        'name': 'OpenRouter',
        'url': 'https://openrouter.ai/api/v1/chat/completions',
        'headers': {'Authorization': f'Bearer {OPENROUTER_KEY}'},
        'payload': {'model': 'google/gemma-2-9b-it:free', 'messages': []}
    },
    {
        'name': 'Ollama',
        'url': 'http://localhost:11434/api/chat',
        'payload': {'model': 'gemma4:31b-cloud', 'messages': []}
    }
]

def call_gemini(prompt):
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(MODELS[0]['url'], json=payload, timeout=10)
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    raise Exception(f'Status {response.status_code}')

def call_openrouter(prompt):
    payload = MODELS[1]['payload'].copy()
    payload['messages'] = [{'role': 'user', 'content': prompt}]
    response = requests.post(MODELS[1]['url'], headers=MODELS[1]['headers'], json=payload, timeout=10)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    raise Exception(f'Status {response.status_code}')

def call_ollama(prompt):
    payload = MODELS[2]['payload'].copy()
    payload['messages'] = [{'role': 'user', 'content': prompt}]
    payload['stream'] = False
    response = requests.post(MODELS[2]['url'], json=payload, timeout=10)
    if response.status_code == 200:
        return response.json()['message']['content']
    raise Exception(f'Status {response.status_code}')

def main():
    if len(sys.argv) < 2:
        print("Uso: python galileo_router.py 'Tuo prompt qui'")
        return

    prompt = sys.argv[1]
    
    print(f"--- Avvio Cascata Galileo ---")
    
    # TENTATIVO 1: GEMINI
    try:
        print("Tento Gemini...", end=' ', flush=True)
        res = call_gemini(prompt)
        print("✅ OK")
        print(f"\n[Gemini]: {res}")
        return
    except Exception as e:
        print(f"❌ Fallito ({e})")

    # TENTATIVO 2: OPENROUTER
    try:
        print("Tento OpenRouter...", end=' ', flush=True)
        res = call_openrouter(prompt)
        print("✅ OK")
        print(f"\n[OpenRouter]: {res}")
        return
    except Exception as e:
        print(f"❌ Fallito ({e})")

    # TENTATIVO 3: OLLAMA
    try:
        print("Tento Ollama...", end=' ', flush=True)
        res = call_ollama(prompt)
        print("✅ OK")
        print(f"\n[Ollama]: {res}")
        return
    except Exception as e:
        print(f"❌ Fallito ({e})")
        print("\n⚠️ TUTTI I PROVIDER HANNO FALLITO.")

if __name__ == '__main__':
    main()
