import streamlit as st

# Configure the app
st.set_page_config(
    page_title="Medical Chatbot Demo",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Critical symptoms (trigger emergency warnings)
CRITICAL_SYMPTOMS = [
    "chest pain", "difficulty breathing", "severe bleeding", 
    "heart attack", "stroke", "unconscious", "choking",
    "poisoning", "allergic reaction", "suicidal"
]

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "🏥 **Hello! I'm your Medical Assistant Demo.**\n\n"
                   "⚠️ *This is a simulation* - real deployment uses Ollama/gemma3n.\n"
                   "Try mentioning: headache, fever, or emergency symptoms."
    }]

# Simulate AI response (no Ollama required)
def get_response(user_input):
    user_input = user_input.lower()
    
    # 1. Emergency check
    for symptom in CRITICAL_SYMPTOMS:
        if symptom in user_input:
            return (
                f"🚨 **EMERGENCY**: Detected *'{symptom}'*!\n\n"
                "1. Call emergency services **immediately** (112/115)\n"
                "2. Do NOT wait for further instructions\n"
                "3. Follow operator guidance\n\n"
                "*This is a simulated emergency response.*"
            )
    
    # 2. Common symptoms
    responses = {
        "headache": (
            "**Possible causes**:\n"
            "- Tension headache\n- Migraine\n- Dehydration\n\n"
            "**Suggestions**:\n"
            "- Rest in a dark room\n- Stay hydrated\n"
            "- Monitor for worsening symptoms\n\n"
            "*Real AI would provide personalized advice.*"
        ),
        "fever": (
            "**When to seek help**:\n"
            "- Fever > 39°C (102°F)\n"
            "- Lasting > 3 days\n- With rash/severe pain\n\n"
            "**Self-care**:\n"
            "- Rest\n- Hydrate\n- Use fever reducers if appropriate\n\n"
            "*Simulated response - consult a doctor.*"
        ),
        "form": (
            "📋 **Medical Form Available in Sidebar**\n\n"
            "1. Fill out your symptoms\n"
            "2. Submit to contact a doctor\n"
            "3. For emergencies, call 112/115"
        )
    }
    
    # 3. Default response
    for keyword, response in responses.items():
        if keyword in user_input:
            return response
    
    return (
        f"Thanks for your question about *'{user_input}'*.\n\n"
        "This demo provides:\n"
        "- Emergency warnings 🚨\n"
        "- Basic symptom info\n"
        "- Medical form access\n\n"
        "**Real AI would give detailed advice here.**"
    )

# Sidebar - Medical Form
with st.sidebar:
    st.title("Medical Tools")
    with st.form("health_form"):
        st.write("**Simulated Patient Form**")
        name = st.text_input("Name")
        symptoms = st.text_area("Symptoms")
        submitted = st.form_submit_button("Submit to Doctor (Demo)")
        if submitted:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"📄 **Form Submitted (Simulated):**\n\nPatient: {name}\nSymptoms: {symptoms}"
            })
            st.toast("Demo form submitted!", icon="📋")

# Main Chat Interface
st.title("🤖 Medical Chatbot Demo")

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Chat input
if prompt := st.chat_input("Describe your symptoms..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Get and display response
    with st.spinner("Thinking..."):
        response = get_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)
