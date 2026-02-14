import subprocess
import time
import requests
import sys
import os

# Configuration
OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2:1b.2:1b"  # Change to 'mistral', 'gemma', etc. as needed

def is_server_running():
    """Checks if the Ollama server is reachable."""
    try:
        response = requests.get(OLLAMA_HOST)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def start_ollama_serve():
    """Starts the Ollama server as a subprocess if not running."""
    if is_server_running():
        print(f"✅ Ollama is already running at {OLLAMA_HOST}")
        return

    print("⏳ Starting Ollama server...")
    try:
        # Start ollama serve in a non-blocking way, redirecting output to prevent clutter
        # logic works for Linux/Mac/Windows if 'ollama' is in PATH
        subprocess.Popen(
            ["ollama", "serve"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            start_new_session=True # Detach from current process group
        )
        
        # Wait for the server to spin up
        retries = 0
        while not is_server_running():
            time.sleep(1)
            retries += 1
            if retries > 10:
                raise TimeoutError("Ollama server failed to start after 10 seconds.")
        
        print(f"✅ Ollama server started successfully at {OLLAMA_HOST}")

    except FileNotFoundError:
        print("❌ Error: 'ollama' command not found. Is Ollama installed?")
        sys.exit(1)

def ensure_model_pulled(model_name=DEFAULT_MODEL):
    """Checks if the requested model exists; pulls it if missing."""
    import ollama
    
    try:
        # List available models
        models_info = ollama.list()
        # Handle difference in return structure between versions
        existing_models = [m['name'] for m in models_info.get('models', [])]
        
        # Check for exact match or match with tag (e.g. llama3.2:1b:latest)
        if not any(model_name in m for m in existing_models):
            print(f"⬇️ Model '{model_name}' not found locally. Pulling now (this may take a while)...")
            ollama.pull(model_name)
            print(f"✅ Model '{model_name}' downloaded.")
        else:
            print(f"✅ Model '{model_name}' is ready.")
            
    except Exception as e:
        print(f"❌ Failed to check/pull model: {e}")

def initialize_ollama(model_name=DEFAULT_MODEL):
    """Master function to prepare the environment."""
    start_ollama_serve()
    ensure_model_pulled(model_name)
    return model_name

if __name__ == "__main__":
    # Test the initialization independently
    initialize_ollama()