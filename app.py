
# Refactored medical chatbot using Streamlit + Ollama chat API (gemma3n)
# File: medical_chatbot.py

import streamlit as st
import requests
import warnings
import time
import sys
import os

# Suppress warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Medical Chatbot with gemma3n",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

SYSTEM_PROMPT = """You are a medical information assistant using the gemma3n model. Follow these rules:

1. EMERGENCY SYMPTOMS: If patient mentions chest pain, difficulty breathing, severe bleeding, heart attack, stroke symptoms, loss of consciousness, severe burns, choking, poisoning, or allergic reaction:
   → Respond: "🚨 EMERGENCY: [symptom] detected! Call emergency services IMMEDIATELY (112 or 115). Do NOT wait for further instructions."

2. MEDICAL FORM REQUESTS: If patient mentions "form", "doctor", "contact doctor", "see doctor", "severe condition":
   → Respond: "📋 Medical Form Available In The Menu. Fill out the form and it will be sent to one of our trusted doctors."

3. GENERAL SYMPTOMS: For other health concerns:
   → Provide helpful medical information
   → Suggest 2-3 possible causes
   → Recommend consulting healthcare professionals
   → Use empathetic language

4. GREETINGS: Respond warmly and ask how you can help.

Always end with: "Please consult a healthcare professional for proper diagnosis."
Never provide specific diagnoses or medication recommendations."""

CRITICAL_SYMPTOMS = [
    "chest pain", "difficulty breathing", "severe bleeding", "heart attack",
    "stroke symptoms", "loss of consciousness", "severe burns", "choking",
    "poisoning", "allergic reaction", "suicidal thoughts"
]


class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.model = "gemma3n"   # ép chỉ dùng gemma3n
        self.available = self._check_ollama()

    def _check_ollama(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(self.model in model.get("name", "") for model in models)
            return False
        except:
            return False


class MedicalChatbot:
    def __init__(self):
        self.ollama = OllamaClient()
        self.model_info = self.ollama.model
        self.history = []

    def generate_response(self, messages):
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages},
                timeout=30
            )
            if response.status_code == 200:
                return response.json()["message"]["content"]
            else:
                return "⚠️ Failed to generate response from model."
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    def _fallback_response(self, user_input):
        return f"""Thank you for your question about: "{user_input}"

Please consult a healthcare professional for proper diagnosis.

⚠️ *Fallback response - Ollama/gemma3n not available.*"""

    def reset_history(self):
        self.history = []

    def get_status(self):
        return {
            "ollama_available": self.ollama.available,
            "model": self.model_info,
            "conversation_turns": len(self.history),
            "mode": "AI" if self.ollama.available else "Fallback"
        }


def main():
    bot = MedicalChatbot()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        status = bot.get_status()
        msg = f"✅ Connected to {status['model']}" if status['ollama_available'] else "⚠️ Ollama not available, using fallback mode."
        st.session_state.chat_history.append({"role": "assistant", "content": msg})

    st.sidebar.title("🏥 Medical Chatbot")
    status = bot.get_status()
    st.sidebar.write(f"**Mode:** {status['mode']}")
    st.sidebar.write(f"**Model:** {status['model']}")
    st.sidebar.write(f"**Turns:** {status['conversation_turns']}")
    if st.sidebar.button("🔄 Reset Chat"):
        bot.reset_history()
        st.session_state.chat_history = []
        st.rerun()

    st.title("🤖 Chat with Medical Assistant")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Enter your symptoms or question")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Generating response..."):
                response = bot.generate_response(prompt)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.markdown(response)


if __name__ == "__main__":
    main()
