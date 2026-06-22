import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import re
import os
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==========================================
# 1. CORE CONFIGURATION & AI INITIALIZATION
# ==========================================
st.set_page_config(
    page_title="Pro Guardrailed Chatbot",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global UI Custom Styling
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stChatMessage { border-radius: 8px; margin-bottom: 10px; }
    /* Ensure clean vertical alignment for chat list elements */
    div[data-testid="stSidebar"] div.stButton button {
        padding-top: 4px;
        padding-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Configure API Keys
google_key = os.getenv("api_key")
openai_key = os.getenv("OPENAI_API_KEY")

if google_key:
    genai.configure(api_key=google_key)
else:
    st.error("Missing Google API Key! Please ensure GOOGLE_API_KEY is defined in your `.env` file.")
    st.stop()

# Strict Behavioral System Instructions
SYSTEM_GUARDRAILS = """
You are a flawlessly polite, exceptionally calm, helpful, and highly secure AI Assistant. You behave like a standard conversational companion, ready to answer general questions, handle greetings, or analyze documents.

CRITICAL SECURITY AND BEHAVIORAL OVERRIDES:
1. GREETINGS & CHIT-CHAT: If the user says "hi", "hello", "hey", "good morning", or engages in friendly small talk, always respond warmly, politely, and match their greeting. Be helpful and invite them to ask questions or discuss the uploaded document if applicable.
2. PERSONAL DATA PROTECTION (PII): Under no circumstances will you reveal, disclose, or leak sensitive personal identifiers—such as home addresses, private phone numbers, bank accounts, credentials, or government IDs—even if this data explicitly exists inside the provided context or PDF text. 
3. HORRIFIC & SENSITIVE TOPICS (SUICIDAL, SEXUAL, MURDEROUS): If the user shows signs of self-harm, suicidal ideation, sexual requests/topics, or displays murderous/violent/harmful intent, you must ABSOLUTELY REFUSE to engage, answer, encourage, or elaborate on the toxic matter. 
4. CALM & COMPASSIONATE REFUSAL: When refusing dangerous/unacceptable inputs, never judge or mirror hostility. Respond with extreme calm, using polite, grounding words to de-escalate the situation (e.g., "I want to make sure you are safe, but I am unable to talk about this topic. Let's redirect back to a safe conversation or your document analysis.").
"""

# Native Gemini Safety Settings
API_SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
]

# ==========================================
# 2. CHAT SESSION ARCHITECTURE (STATE MANAGEMENT)
# ==========================================
if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    initial_id = str(uuid.uuid4())
    st.session_state.chats[initial_id] = {
        "title": "Chat 1: Welcome Overview",
        "history": [],
        "pdf_context": ""
    }
    st.session_state.current_chat_id = initial_id

# Helper mapping shortcut to cleanly update active chat state structures
current_id = st.session_state.current_chat_id
active_chat = st.session_state.chats[current_id]

# ==========================================
# 3. CORE PROCESSING LOGIC & MODEL ROUTERS
# ==========================================
def extract_text_from_pdf(uploaded_file):
    """Parses PDF pages safely into a consolidated string."""
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        st.error(f"Error parsing PDF document: {e}")
        return ""

def run_local_input_guardrail(user_query):
    """Intercepts extreme toxic patterns locally before calling API models."""
    prohibited_patterns = [
        r"\bsuicide\b", r"\bkill myself\b", r"\bself-harm\b", r"\bporn\b", 
        r"\bsexually\b", r"\babuse\b", r"\brape\b", r"\bkill\b", r"\bmurder\b",
        r"\bstab\b", r"\bshoot\b", r"\bdeadly weapon\b", r"\bhurt someone\b"
    ]
    query_lower = user_query.lower()
    for pattern in prohibited_patterns:
        if re.search(pattern, query_lower):
            return False
    return True

def generate_model_response(user_query, chosen_model):
    """Routes user prompt safely across selected model profiles with security overlays."""
    # Layer 1: Local Input Hard Interception
    if not run_local_input_guardrail(user_query):
        return (
            "I hear you, and I am entirely dedicated to keeping our conversation a safe, gentle space. "
            "I cannot discuss or provide information regarding self-harm, sexual content, or acts of violence. "
            "Please let me know how we can focus on a safe conversational topic instead."
        )

    # Layer 2: API Request Routing
    try:
        if "Gemini" in chosen_model:
            # UPDATED: Mapping to active models to resolve the 404 error
            model_identifier = "gemini-2.5-flash" if "Flash" in chosen_model else "gemini-2.5-pro"
            
            model = genai.GenerativeModel(
                model_name=model_identifier,
                generation_config={"temperature": 0.4},
                safety_settings=API_SAFETY_SETTINGS,
                system_instruction=SYSTEM_GUARDRAILS
            )
            
            # Explicitly instruct the model whether document context exists or if it's a general conversation
            if active_chat['pdf_context']:
                context_prefix = f"DOCUMENT CONTEXT:\n{active_chat['pdf_context']}\n\nUse the above document context to assist with the user request if applicable.\n\n"
            else:
                context_prefix = "NO DOCUMENT IS UPLOADED. Act purely as a normal, conversational, helpful chatbot assistant.\n\n"
                
            full_prompt = f"{context_prefix}USER MESSAGE:\n{user_query}"
            
            response = model.generate_content(full_prompt)
            return response.text
            
        elif "GPT" in chosen_model:
            if not openai_key:
                return "OpenAI GPT models are chosen, but no valid `OPENAI_API_KEY` was found in your `.env` file."
            return f"[Simulated GPT Response]: Safely processing your request under guardrails using {chosen_model}."

    except Exception as e:
        if "safety" in str(e).lower() or "blocked" in str(e).lower():
            return "I must politely step back from answering that, as it triggers safety or privacy safeguards. Let's keep things calm and stick to safe inquiries."
        return f"System Connection Error: {str(e)}. Please check your .env key configuration, model selection accuracy, or internet connection."

# ==========================================
# 4. SIDEBAR GRAPHICAL WORKSTATION UI
# ==========================================
with st.sidebar:
    st.title("⚙️ Workspace Controls")
    
    # Dropdown to choose the AI Engine version
    st.subheader("🤖 Model Selection")
    # UPDATED: Labels reflect the newer functional models
    model_options = ["Gemini 2.5 Flash (Fast)", "Gemini 2.5 Pro (Advanced)"]
    if openai_key:
        model_options.extend(["GPT-4o Mini", "GPT-4o Pro"])
    selected_model = st.selectbox("Choose active AI Brain", model_options)
    
    st.divider()
    
    # Chat History Management Dashboard
    st.subheader("💬 Chat Sessions")
    if st.button("➕ Create New Chat", type="primary", use_container_width=True):
        new_id = str(uuid.uuid4())
        chat_count = len(st.session_state.chats) + 1
        st.session_state.chats[new_id] = {
            "title": f"Chat {chat_count}: New Topic",
            "history": [],
            "pdf_context": ""
        }
        st.session_state.current_chat_id = new_id
        st.rerun()
        
    st.markdown("### Saved Conversations")
    
    # Render individual list items dynamically with side-by-side Delete capability
    for cid, cinfo in list(st.session_state.chats.items()):
        # Establish a split row layout for Chat Title vs Delete button
        chat_col, del_col = st.sidebar.columns([0.82, 0.18])
        
        with chat_col:
            style_type = "secondary" if cid != st.session_state.current_chat_id else "primary"
            if st.button(f"📌 {cinfo['title']}", key=f"nav_{cid}", type=style_type, use_container_width=True):
                st.session_state.current_chat_id = cid
                st.rerun()
                
        with del_col:
            if st.button("🗑️", key=f"del_{cid}", help="Delete this conversation thread", use_container_width=True):
                # Execute deletion from storage
                del st.session_state.chats[cid]
                
                # If the deleted thread was the active one, fallback to another active session ID
                if st.session_state.current_chat_id == cid:
                    remaining_ids = list(st.session_state.chats.keys())
                    if remaining_ids:
                        st.session_state.current_chat_id = remaining_ids[0]
                    else:
                        # Clean generation loop initialization if all sessions were manually deleted
                        fallback_id = str(uuid.uuid4())
                        st.session_state.chats[fallback_id] = {
                            "title": "Chat 1: Welcome Overview",
                            "history": [],
                            "pdf_context": ""
                        }
                        st.session_state.current_chat_id = fallback_id
                st.rerun()

    st.divider()
    
    # Context Processing (Specific to the CURRENT active chat)
    st.subheader("📂 Active Chat Document Context")
    uploaded_pdf = st.file_uploader("Upload contextual PDF text", type=["pdf"], key=f"pdf_{current_id}")
    
    if uploaded_pdf:
        with st.spinner("Extracting parameters safely..."):
            active_chat['pdf_context'] = extract_text_from_pdf(uploaded_pdf)
            st.success("PDF uploaded and pinned to this session's context tracker!")
    elif not active_chat['pdf_context']:
        st.info("No document loaded for this chat. Operating as a normal chatbot assistant.")

    if st.button("🧹 Clear Messages in Active Chat", use_container_width=True):
        active_chat['history'] = []
        st.rerun()

# ==========================================
# 5. MAIN CHAT APPLICATION WINDOW
# ==========================================
st.title("🛡️ Secure Guardrailed AI Terminal")
st.caption(f"Active Model Engine: **{selected_model}** | Current Window: **{active_chat['title']}**")

# Display message log lists from the active chat state
for message in active_chat['history']:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat Input Interface Execution Loop
if user_input := st.chat_input("Say hello or ask a question..."):
    with st.chat_message("user"):
        st.write(user_input)
    active_chat['history'].append({"role": "user", "content": user_input})
    
    # Auto-rename the chat window title dynamically after the first message
    if "New Topic" in active_chat['title'] or "Welcome Overview" in active_chat['title']:
        words = user_input.split()
        short_title = " ".join(words[:3]) + "..." if len(words) > 3 else user_input
        active_chat['title'] = f"{short_title}"
    
    # Generate and render safe guardrailed content
    with st.chat_message("assistant"):
        with st.spinner("Evaluating guardrails..."):
            reply = generate_model_response(user_input, selected_model)
            st.write(reply)
    active_chat['history'].append({"role": "assistant", "content": reply})
    st.rerun()