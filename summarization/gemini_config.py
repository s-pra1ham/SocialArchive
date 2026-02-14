import os
import google.generativeai as genai
from google.api_core import retry

# Configuration
# You can hardcode your key here for testing, but environment variables are safer.
os.environ["GEMINI_API_KEY"] = "AIzaSyA1Rnv5FsdF5Ex77cJEbg_-cCA7tMcFDt4"

DEFAULT_MODEL = "gemini-1.5-flash"  # Flash is fast and cheap; use "gemini-1.5-pro" for complex reasoning

def configure_gemini(api_key=None):
    """
    Sets up the Gemini API client.
    Prioritizes the passed api_key, then looks for GEMINI_API_KEY env var.
    """
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "❌ API Key missing. Please set 'GEMINI_API_KEY' environment variable "
            "or pass it to the constructor."
        )

    genai.configure(api_key=api_key)
    return True

def get_gemini_model(model_name=DEFAULT_MODEL):
    """
    Returns a configured GenerativeModel object ready for generation.
    """
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
    )
    return model

if __name__ == "__main__":
    # Test configuration
    try:
        configure_gemini()
        print(f"✅ Gemini configured successfully using model: {DEFAULT_MODEL}")
        m = get_gemini_model()
        print("✅ Model object created.")
    except Exception as e:
        print(f"❌ Configuration failed: {e}")