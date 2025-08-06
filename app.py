import streamlit as st
from datetime import datetime

# Configure the app
st.set_page_config(
    page_title="Smart Medical Chatbot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced emergency symptoms with specific responses
EMERGENCY_SYMPTOMS = {
    "chest pain": {
        "category": "Cardiac",
        "response": "🚨 **CARDIAC EMERGENCY**: Chest pain may indicate:\n\n"
                   "• Heart attack\n• Angina\n• Pulmonary embolism\n\n"
                   "**Action Required**:\n"
                   "1. Stop all activity\n2. Call 911/112 immediately\n"
                   "3. Chew 325mg aspirin if available\n"
                   "4. Form auto-updated to EMERGENCY status"
    },
    "difficulty breathing": {
        "category": "Respiratory",
        "response": "🚨 **RESPIRATORY EMERGENCY**: Could indicate:\n\n"
                   "• Asthma attack\n• Pulmonary edema\n• Pneumothorax\n\n"
                   "**Action Required**:\n"
                   "1. Sit upright\n2. Use inhaler if available\n"
                   "3. Call emergency services\n"
                   "4. Form marked URGENT"
    },
    "severe headache": {
        "category": "Neurological",
        "response": "🚨 **NEUROLOGICAL EMERGENCY**: May suggest:\n\n"
                   "• Stroke\n• Aneurysm\n• Meningitis\n\n"
                   "**Action Required**:\n"
                   "1. Check FAST symptoms (Face-Arms-Speech-Time)\n"
                   "2. Call ambulance immediately\n"
                   "3. Note time of onset\n"
                   "4. Form updated with emergency details"
    }
}

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "🏥 **Smart Medical Assistant**\n\n"
                   "I'll automatically track symptoms in your form.\n"
                   "Try: 'I have a headache' or 'My chest hurts badly'"
    }]
    
if "medical_form" not in st.session_state:
    st.session_state.medical_form = {
        "symptoms": [],
        "urgency": "Non-urgent",
        "categories": [],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "notes": "Conversation history:\n"
    }

if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

# Smart response generator
def generate_response(user_input):
    user_input_lower = user_input.lower()
    response = ""
    form_updated = False
    
    # 1. Check for emergencies first
    for symptom, details in EMERGENCY_SYMPTOMS.items():
        if symptom in user_input_lower:
            # Update form with emergency details
            st.session_state.medical_form["symptoms"].append(symptom)
            st.session_state.medical_form["categories"].append(details["category"])
            st.session_state.medical_form["urgency"] = "Emergency"
            st.session_state.medical_form["notes"] += f"\n[{datetime.now().strftime('%H:%M')}] EMERGENCY: {symptom}"
            
            response = details["response"]
            form_updated = True
            break
    
    # 2. Handle non-emergency symptoms
    if not form_updated:
        symptom_keywords = {
            "headache": ("Neurological", "Consider pain level and duration"),
            "fever": ("Infection", "Monitor temperature every 2 hours"),
            "cough": ("Respiratory", "Note if productive or dry"),
            "nausea": ("Gastrointestinal", "Track frequency and triggers")
        }
        
        for symptom, (category, note) in symptom_keywords.items():
            if symptom in user_input_lower:
                # Add to existing symptoms
                if symptom not in st.session_state.medical_form["symptoms"]:
                    st.session_state.medical_form["symptoms"].append(symptom)
                    st.session_state.medical_form["categories"].append(category)
                    st.session_state.medical_form["notes"] += f"\n[{datetime.now().strftime('%H:%M')}] Reported {symptom}"
                
                response = (
                    f"✅ Added '{symptom}' to your form\n\n"
                    f"**Category**: {category}\n"
                    f"**Advice**: {note}\n\n"
                    "I'll keep tracking your symptoms. "
                    "Describe anything else you're feeling."
                )
                form_updated = True
                break
    
    # 3. Default response
    if not form_updated:
        response = (
            "Thank you for sharing. I've noted this in your form.\n\n"
            "Please describe any:\n"
            "- Specific symptoms\n"
            "- Pain levels (1-10)\n"
            "- Duration of symptoms"
        )
        st.session_state.medical_form["notes"] += f"\n[{datetime.now().strftime('%H:%M')}] Note: {user_input}"
    
    return response

# Sidebar - Auto-updating Medical Form
with st.sidebar:
    st.title("🩺 Auto-Filled Medical Form")
    
    # Display real-time form data
    with st.expander("Current Symptoms", expanded=True):
        if st.session_state.medical_form["symptoms"]:
            st.write("**Reported Symptoms:**")
            for symptom in st.session_state.medical_form["symptoms"]:
                st.write(f"- {symptom.capitalize()}")
        else:
            st.warning("No symptoms reported yet")
        
        st.write(f"**Urgency:** {st.session_state.medical_form['urgency']}")
        
        if st.session_state.medical_form["categories"]:
            st.write("**Possible Categories:**")
            st.write(", ".join(set(st.session_state.medical_form["categories"])))
    
    # Form submission - moved outside of form context
    name = st.text_input("Full Name (required)", key="patient_name")
    age = st.number_input("Age", min_value=1, max_value=120, key="patient_age")
    
    if st.button("Submit to Doctor"):
        if name:
            st.session_state.form_submitted = True
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"📄 **Form Sent to Doctor**\n\nPatient: {name}, {age}\nSymptoms: {', '.join(st.session_state.medical_form['symptoms']) or 'None'}"
            })
            st.success("Form submitted successfully!")
            st.rerun()
        else:
            st.error("Please enter at least your name")

# Main Chat Interface
st.title("🤖 Symptom Tracker Chatbot")

# Display conversation
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Chat input
if prompt := st.chat_input("Describe how you're feeling..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Generate and display response
    with st.spinner("Analyzing..."):
        response = generate_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)
        st.rerun()  # Refresh to show updated form
