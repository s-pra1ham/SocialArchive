import os
from dotenv import load_dotenv

# Optional imports: Wrap in try/except so the script doesn't crash 
# if you only have one SDK installed.
try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import ollama
except ImportError:
    ollama = None

load_dotenv()

class LLMWrapper:
    """Base wrapper to ensure all models return text in the same way."""
    def generate(self, prompt: str) -> str:
        raise NotImplementedError

class GeminiClient(LLMWrapper):
    def __init__(self, api_key, model_name):
        if not genai: raise ImportError("google-generativeai library not installed.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Gemini Error: {e}"

class OpenAIClient(LLMWrapper):
    def __init__(self, api_key, model_name):
        if not OpenAI: raise ImportError("openai library not installed.")
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def generate(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI Error: {e}"

class ClaudeClient(LLMWrapper):
    def __init__(self, api_key, model_name):
        if not anthropic: raise ImportError("anthropic library not installed.")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_name = model_name

    def generate(self, prompt):
        try:
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Claude Error: {e}"

class OllamaClient(LLMWrapper):
    def __init__(self, host, model_name):
        if not ollama: raise ImportError("ollama library not installed.")
        # The official python ollama lib relies on env vars or default localhost
        # We assume the user has OLLAMA_HOST set or is running locally
        self.model_name = model_name

    def generate(self, prompt):
        try:
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt},
            ])
            return response['message']['content']
        except Exception as e:
            return f"Ollama Error: {e}"

def get_llm_client(provider: str, model_name: str = None):
    """
    Factory function to return the correct client.
    
    :param provider: 'gemini', 'openai', 'claude', or 'ollama'
    :param model_name: Specific model (e.g., 'gpt-4o', 'llama3'). 
                       Defaults are applied if None.
    """
    provider = provider.lower()
    
    if provider == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        model = model_name or "gemini-1.5-flash"
        return GeminiClient(key, model)
    
    elif provider == "openai" or provider == "chatgpt":
        key = os.getenv("OPENAI_API_KEY")
        model = model_name or "gpt-4o"
        return OpenAIClient(key, model)
    
    elif provider == "claude":
        key = os.getenv("ANTHROPIC_API_KEY")
        model = model_name or "claude-3-5-sonnet-20240620"
        return ClaudeClient(key, model)
    
    elif provider == "ollama":
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        model = model_name or "llama3"
        return OllamaClient(host, model)
    
    else:
        raise ValueError(f"Unknown provider: {provider}")

# Test block
if __name__ == "__main__":
    print("Testing Wrapper...")
    try:
        # Example: Change provider to 'ollama', 'openai', etc. to test
        client = get_llm_client("gemini") 
        print(client.generate("Say hello!"))
    except Exception as e:
        print(f"Test failed: {e}")