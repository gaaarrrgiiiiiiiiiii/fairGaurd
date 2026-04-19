import os
import requests
from dotenv import load_dotenv

# Load variables from .env mapped to our backend root
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

class LLMService:
    def generate_explanation(self, features: dict, original_decision: str, corrected_decision: str, protected_attributes: list) -> str:
        prompt = f"""
        You are an AI fairness compliance auditor. 
        A loan application was originally `{original_decision}` by a machine learning model.
        The applicant has features: {features}.
        Our algorithmic firewall detected a demographic parity violation heavily attributed to: {protected_attributes}.
        Our counterfactual engine intercepted the request and flipped the decision to `{corrected_decision}`.
        
        Write a very concise (1 sentence) legal explanation of this interception to be displayed on a dashboard audit log.
        """

        if GEMINI_API_KEY:
            # Use Gemini (Google Solution Challenge alignment)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "systemInstruction": {
                    "parts": [{"text": "You provide extremely concise, professional, legal-sounding compliance logs."}]
                },
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 60
                }
            }
            try:
                response = requests.post(url, json=payload, timeout=3.0)
                response.raise_for_status()
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            except Exception as e:
                print("Gemini generation failed, falling back:", str(e))
                # Fall back to groq logic or simple text below
        
        if GROQ_API_KEY:
            # Fast inference with LLaMA 3 on Groq
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": "You provide extremely concise, professional, legal-sounding compliance logs."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 60
            }
            
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=2.0)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print("Groq LLM generation failed:", str(e))
                
        if MISTRAL_API_KEY:
            url = "https://api.mistral.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {MISTRAL_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "mistral-tiny",
                "messages": [
                    {"role": "system", "content": "You provide extremely concise, professional, legal-sounding compliance logs."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 60
            }
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=2.0)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print("Mistral LLM generation failed:", str(e))
                
        # Ultimate Fallback if no keys or both failed
        return f"Application {corrected_decision} after bias correction operations on protected attributes {protected_attributes}."

llm_service = LLMService()
