import os
from huggingface_hub import hf_hub_download
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

class AIAnalyst:
    """AI-powered error analysis and fix suggestion engine."""
    
    def __init__(self):
        self.model_id = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
        self.filename = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
        self.llm = None
        self._load_model()
        
    def _load_model(self):
        if not Llama:
            print("⚠ Warning: llama-cpp-python not installed. AI analysis disabled.")
            return

        try:
            print(f"🧠 Loading AI Analyst ({self.filename})...")
            model_path = hf_hub_download(repo_id=self.model_id, filename=self.filename)
            
            # Initialize Llama model
            self.llm = Llama(
                model_path=model_path,
                n_ctx=2048,  # Context window
                n_threads=4, # CPU threads
                verbose=False
            )
            print("✓ AI Analyst ready.")
        except Exception as e:
            print(f"⚠ Failed to load AI model: {e}")

    def analyze_bugs(self, bugs):
        """Analyze a list of bugs and add AI insights."""
        if not self.llm:
            return

        print("✨ Analyzing bugs with AI...")
        count = 0
        
        for bug in bugs:
             # Only analyze significant errors
             if bug['severity'] in ['CRITICAL', 'HIGH', 'MEDIUM']:
                 self._analyze_single_bug(bug)
                 count += 1
                 
        print(f"✓ AI analyzed {count} issues.")

    def _analyze_single_bug(self, bug):
        """Analyze a single bug in-place."""
        title = bug.get('title', '')
        desc = bug.get('description', '')
        stderr = bug.get('output', {}).get('stderr', '') or bug.get('output', {}).get('error', '')
        
        # Construct prompt
        prompt = f"""<|system|>
You are an expert debugger. specificy the cause and fix for the error.
<|user|>
Error: {title}
Description: {desc}
Log:
{stderr[:500]}

Explain why this error happened and suggest a command to fix it.
<|assistant|>
**Analysis:** """

        try:
            output = self.llm(
                prompt, 
                max_tokens=256, 
                stop=["<|user|>", "<|system|>"], 
                echo=False
            )
            text = output['choices'][0]['text']
            
            # Split into explanation and fix if possible, otherwise just put all in explanation
            bug['ai_explanation'] = text.strip()
            bug['ai_fix'] = "See analysis above." # TinyLlama might not unstructured it perfectly, so we keep it simple
            
        except Exception as e:
            print(f"⚠ AI Analysis failed for bug: {e}")
