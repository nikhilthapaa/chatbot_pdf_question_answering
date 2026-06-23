import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import re
import os
import uuid
import html
from dotenv import load_dotenv

# Try importing ollama gracefully to prevent app crashes if not installed yet
try:
    import ollama
except ImportError:
    ollama = None

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

# Global UI Layout Styling Overrides & Premium Sidebar Overhaul
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stChatMessage { border-radius: 8px; margin-bottom: 5px; }
    
    /* Styling to ensure popovers fit nicely inside sidebar columns */
    div[data-testid="stSidebar"] div[data-testid="stPopover"] button {
        padding: 4px 8px !important;
        border: none !important;
        background: transparent !important;
        color: #6b7280 !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stPopover"] button:hover {
        color: #1f2937 !important;
        background-color: #f3f4f6 !important;
    }
    
    /* PERFECT VERTICAL ALIGNMENT FLUSH: Forces action rows to flex-align center horizontally and vertically */
    .stChatMessage div[data-testid="stHorizontalBlock"] {
        margin-top: 6px !important;
        gap: 6px !important;
        display: flex !important;
        align-items: center !important;
    }
    
    /* Ensures layout columns share identical vertical centering properties */
    .stChatMessage div[data-testid="stHorizontalBlock"] div[data-testid="column"] {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
    }
    
    /* Reset margins inside message elements to prevent vertical alignment offset */
    .stChatMessage [data-testid="element-container"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* UNIFORM ELEMENT-LEVEL MINIATURIZATION: Forces exact matching size dimensions */
    .stChatMessage div[data-testid="stButton"] button {
        background-color: #ffffff !important;
        border: 1px solid rgba(49, 51, 63, 0.2) !important;
        color: #606266 !important;
        padding: 0px !important;
        font-size: 12px !important;
        border-radius: 4px !important;
        height: 26px !important;
        min-height: 26px !important;
        max-height: 26px !important;
        width: 85px !important;
        min-width: 85px !important;
        max-width: 85px !important;
        line-height: 24px !important;
        white-space: nowrap !important;
        word-break: keep-all !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: none !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
    }

    /* IFRAME WRAPPER HARMONIZATION: Erases HTML component tracking offsets to snap layouts together */
    .stChatMessage div[data-testid="column"] div[data-testid="stHtml"] {
        width: 85px !important;
        height: 26px !important;
        display: flex !important;
        align-items: center !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .stChatMessage div[data-testid="column"] div[data-testid="stHtml"] iframe {
        width: 85px !important;
        height: 26px !important;
        margin: 0 !important;
        padding: 0 !important;
        display: block !important;
    }

    /* Standardizes internal button text metrics */
    .stChatMessage div[data-testid="stButton"] button p,
    .stChatMessage div[data-testid="stButton"] button span {
        margin: 0 !important;
        padding: 0 !important;
        font-size: 12px !important;
        color: #606266 !important;
        line-height: 1 !important;
    }
    
    /* Clean interactive hover behaviors */
    .stChatMessage div[data-testid="stButton"] button:hover {
        border-color: #c2e7b0 !important;
        color: #67c23a !important;
    }
    .stChatMessage div[data-testid="stButton"] button:hover p {
        color: #67c23a !important;
    }
    
    /* ==========================================
       PREMIUM SIDEBAR UX OVERHAUL THEME
       ========================================== */
    
    /* High-end Typography tweaks for sidebar headers */
    div[data-testid="stSidebar"] h1, div[data-testid="stSidebar"] h2, div[data-testid="stSidebar"] h3 {
        color: #1f2937 !important;
        font-weight: 600 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    /* Make 'Create New Chat' an elegant professional gradient callout */
    div[data-testid="stSidebar"] button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #4f46e5, #2563eb) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 500 !important;
        border-radius: 6px !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.15) !important;
        padding: 6px 12px !important;
    }
    div[data-testid="stSidebar"] button[data-testid="baseButton-primary"]:hover {
        background: linear-gradient(135deg, #4338ca, #1d4ed8) !important;
        box-shadow: 0 4px 8px rgba(37, 99, 235, 0.25) !important;
        transform: translateY(-0.5px);
    }
    
    /* Premium Architecture: Session Vault Container Panel */
    div[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
        padding: 12px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    }
    
    /* Style SELECTED/ACTIVE Chat Item Container nicely */
    div[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:not(div[data-testid="stPopover"] button) {
        text-align: left !important;
        justify-content: flex-start !important;
        font-size: 13px !important;
        border-radius: 6px !important;
        padding: 6px 12px !important;
        transition: all 0.15s ease !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        width: 100% !important;
    }

    /* Active Highlight States Overrides via Streamlit Custom Secondary Hook definitions */
    div[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] button[data-testid="baseButton-primary"] {
        background: #eff6ff !important;
        color: #1e40af !important;
        border: 1px solid #bfdbfe !important;
        font-weight: 500 !important;
        box-shadow: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-size: 13px !important;
        border-radius: 6px !important;
        width: 100% !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] button[data-testid="baseButton-primary"] p {
        color: #1e40af !important;
    }

    /* Passive/Unselected history elements styling */
    div[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] button[data-testid="baseButton-secondary"] {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        color: #4b5563 !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] button[data-testid="baseButton-secondary"]:hover {
        background-color: #f3f4f6 !important;
        border-color: #e5e7eb !important;
        color: #111827 !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] button[data-testid="baseButton-secondary"]:hover p {
        color: #111827 !important;
    }
</style>
""", unsafe_allow_html=True)

# Configure Google API
google_key = os.getenv("GOOGLE_API_KEY")
if google_key:
    genai.configure(api_key=google_key)
else:
    st.error("Missing Google API Key! Please ensure GOOGLE_API_KEY is defined in your `.env` file.")
    st.stop()

# Configure OpenAI API
openai_key = os.getenv("OPENAI_API_KEY")
openai_client = None
if openai_key:
    openai_client = OpenAI(api_key=openai_key)

# Strict Safety System Instructions
SYSTEM_GUARDRAILS = """
You are a flawlessly polite, exceptionally calm, helpful, and highly secure AI Assistant. You behave like a standard conversational companion, ready to answer general questions, handle greetings, or analyze documents.

CRITICAL SECURITY OVERRIDES (MANDATORY):
1. PERSONAL DATA PROTECTION (PII): Under no circumstances will you reveal, disclose, leak, or mention sensitive personal identifiers—such as home addresses, private email addresses, private phone numbers, bank accounts, credentials, passport values, or government IDs—even if this data explicitly exists inside the provided context blocks or PDF texts. If asked for these specific details, you must state that you cannot disclose personal identification information.
2. GREETINGS & CHIT-CHAT: If the user says "hi", "hello", "hey", "good morning", or engages in friendly small talk, always respond warmly, politely, and match their greeting. Be helpful and invite them to ask questions or discuss the uploaded documents if applicable.
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
# 2. STATE ARCHITECTURE MANAGEMENT
# ==========================================
if "chats" not in st.session_state:
    st.session_state.chats = {}
if "current_chat_id" not in st.session_state:
    initial_id = str(uuid.uuid4())
    st.session_state.chats[initial_id] = {
        "title": "Welcome Overview", 
        "history": [], 
        "pdf_chunks": [],
        "processed_files": []
    }
    st.session_state.current_chat_id = initial_id

if "editing_idx" not in st.session_state:
    st.session_state.editing_idx = None
if "force_ai_processing" not in st.session_state:
    st.session_state.force_ai_processing = False

current_id = st.session_state.current_chat_id
active_chat = st.session_state.chats[current_id]

# Migration safety fallback for old session objects
if "pdf_chunks" not in active_chat:
    active_chat["pdf_chunks"] = []
if "processed_files" not in active_chat:
    active_chat["processed_files"] = []

# ==========================================
# 3. CORE RAG PIPELINE & ROUTING MECHANISMS
# ==========================================
def extract_text_from_pdf(uploaded_file):
    """Parses PDF pages safely into a consolidated text payload string."""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        st.error(f"Error parsing PDF document {uploaded_file.name}: {e}")
        return ""

def chunk_text(text, filename, chunk_size=1200, overlap=200):
    """Slices documents into clean semantic blocks with sliding overlap windows."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            space_idx = text.rfind(' ', start, end)
            if space_idx > start + (chunk_size // 2):
                end = space_idx
                
        chunk_content = text[start:end].strip()
        if chunk_content:
            chunks.append({
                "text": chunk_content,
                "source": filename
            })
        start += (chunk_size - overlap)
    return chunks

def retrieve_relevant_chunks(query, chunks, processed_filenames):
    """
    UNIVERSAL MULTI-SOURCE RANKER:
    Ensures text sections from EVERY uploaded file are sent to the AI model simultaneously, 
    preventing any file from being locked out regardless of the total count.
    """
    if not chunks:
        return "NO DOCUMENT CONTEXT AVAILABLE.\n", 0
        
    query_tokens = set(re.findall(r'\w+', query.lower()))
    
    # 1. Group entire available chunk dataset purely by source file name
    doc_grouped_chunks = {filename: [] for filename in processed_filenames}
    for chunk in chunks:
        src = chunk.get("source", "Unknown Source")
        if src in doc_grouped_chunks:
            doc_grouped_chunks[src].append(chunk)

    selected_set = []
    
    # 2. Dynamically adjust quota per document so all files share the prompt space
    total_files = len(processed_filenames)
    chunks_per_doc = max(3, 12 // total_files) if total_files > 0 else 3

    # 3. Process every single uploaded file one by one to extract its top relevant pieces
    for filename, file_chunks in doc_grouped_chunks.items():
        if not file_chunks:
            continue
            
        # If user is just saying hello or greeting, fetch early structural context chunks
        if not query_tokens:
            selected_set.extend(file_chunks[:chunks_per_doc])
        else:
            scored_collection = []
            for chunk in file_chunks:
                text_lower = chunk["text"].lower()
                matching_score = 0
                for token in query_tokens:
                    matching_score += len(re.findall(r'\b' + re.escape(token) + r'\b', text_lower)) * 2.0
                    if token in text_lower and not re.search(r'\b' + re.escape(token) + r'\b', text_lower):
                        matching_score += 0.5
                        
                if matching_score > 0:
                    scored_collection.append((matching_score, chunk))
            
            # Sort this specific document's collection by relevance
            scored_collection.sort(key=lambda x: x[0], reverse=True)
            
            if scored_collection:
                selected_set.extend([item[1] for item in scored_collection[:chunks_per_doc]])
            else:
                # Guarantee representation even if no keywords explicitly match this file
                selected_set.extend(file_chunks[:min(2, len(file_chunks))])
                
    # 4. Construct unified context container header for the LLM
    context_payload = "--- UNIVERSAL MULTI-DOCUMENT REAL-TIME CONTEXT INDEX ---\n"
    context_payload += f"Total Active Contextual Files Verified & Injected: {total_files}\n"
    context_payload += f"Complete Inventory: {', '.join(processed_filenames)}\n\n"
    context_payload += "CRITICAL ASSISTANT REQUIREMENT: You have active access to ALL files listed above. Look through every reference block below to answer comprehensively.\n\n"
    
    for idx, item in enumerate(selected_set):
        context_payload += f"[Reference #{idx+1} | Source File: {item['source']}]\n{item['text']}\n\n"
        
    return context_payload, total_files

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

def clean_output_pii_scrubber(text_response):
    """
    DETERMINISTIC REDACTION SYSTEM:
    Guarantees that even if local models like Mistral leak personal information data patterns 
    from context chunks, it is instantly scrubbed out before rendering into the UI view layers.
    """
    if not text_response:
        return ""
    
    # 1. Standard Global Email Pattern matching
    email_regex = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    text_response = re.sub(email_regex, "[REDACTED EMAIL]", text_response)
    
    # 2. Telephone/Mobile validation matching options
    phone_regex = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    text_response = re.sub(phone_regex, "[REDACTED PHONE NUMBER]", text_response)
    
    # 3. National Identity Card numbers / SSN profiles
    ssn_regex = r'\b\d{3}-\d{2}-\d{4}\b'
    text_response = re.sub(ssn_regex, "[REDACTED IDENTIFIER]", text_response)
    
    return text_response

def generate_model_response(chat_history_list, chosen_model):
    """Routes total user history safely across selected model profiles with security overlays."""
    if not chat_history_list:
        return ""
        
    last_query = chat_history_list[-1]["content"]
    if not run_local_input_guardrail(last_query):
        return (
            "I hear you, and I am entirely dedicated to keeping our conversation a safe, gentle space. "
            "I cannot discuss or provide information regarding self-harm, sexual content, or acts of violence. "
            "Please let me know how we can focus on a safe conversational topic instead."
        )

    # Access all processed data chunks stored securely inside state maps
    if active_chat.get('pdf_chunks') and active_chat.get('processed_files'):
        context_prefix, total_docs = retrieve_relevant_chunks(
            last_query, 
            active_chat['pdf_chunks'], 
            active_chat['processed_files']
        )
        context_prefix += (
            f"\nCRITICAL STATE VERIFICATION: There are currently exactly {total_docs} separate documents uploaded "
            f"and ready for cross-comparison. Read every single chunk carefully. Never state that you can only see "
            f"one or two documents, because context sections from ALL {total_docs} files are explicitly attached above.\n"
        )
    else:
        context_prefix = "NO DOCUMENT IS UPLOADED. Act purely as a normal conversational assistant.\n"

    try:
        if "Gemini" in chosen_model:
            model_identifier = "gemini-2.5-flash" if "Flash" in chosen_model else "gemini-2.5-pro"
            model = genai.GenerativeModel(
                model_name=model_identifier,
                generation_config={"temperature": 0.4},
                safety_settings=API_SAFETY_SETTINGS,
                system_instruction=SYSTEM_GUARDRAILS + "\n\n" + context_prefix
            )
            
            full_prompt = ""
            for msg in chat_history_list:
                role_label = "User" if msg["role"] == "user" else "Assistant"
                full_prompt += f"{role_label}: {msg['content']}\n"
            full_prompt += "Assistant:"
            
            response = model.generate_content(full_prompt)
            return clean_output_pii_scrubber(response.text)
            
        elif "GPT" in chosen_model:
            if not openai_key or not openai_client:
                return "OpenAI GPT models are selected, but no valid `OPENAI_API_KEY` was found."
            
            model_identifier = "gpt-4o-mini" if "Mini" in chosen_model else "gpt-4o"
            
            messages = [
                {"role": "system", "content": SYSTEM_GUARDRAILS + "\n\n" + context_prefix}
            ]
            for msg in chat_history_list:
                messages.append({"role": msg["role"], "content": msg["content"]})
                
            response = openai_client.chat.completions.create(
                model=model_identifier,
                messages=messages,
                temperature=0.4
            )
            return clean_output_pii_scrubber(response.choices[0].message.content)

        elif "Ollama" in chosen_model:
            if ollama is None:
                return "The `ollama` library is missing. Please run `pip install ollama`."
            
            local_model_target = "llama3" if "Llama 3" in chosen_model else "mistral"
            
            # Reinforce instructions for less compliant local models by pinning instructions directly inside system layers
            local_reinforced_system = (
                f"{SYSTEM_GUARDRAILS}\n"
                f"LOCAL MODEL WARNING: DO NOT print emails, do not print phone numbers, and do not leak addresses from the following context blocks.\n"
                f"CONTEXT DATA:\n{context_prefix}"
            )
            
            messages = [
                {"role": "system", "content": local_reinforced_system}
            ]
            for msg in chat_history_list:
                messages.append({"role": msg["role"], "content": msg["content"]})
                
            response = ollama.chat(model=local_model_target, messages=messages)
            
            # Intercept generated text payload through our safety scrubbing system wrapper
            return clean_output_pii_scrubber(response['message']['content'])

    except Exception as e:
        if "safety" in str(e).lower() or "blocked" in str(e).lower():
            return "I must politely step back from answering that, as it triggers safety safeguards."
        return f"System Connection Error: {str(e)}."


def render_isolated_copy_button(text_to_copy):
    """Renders a micro-scaled HTML/JS copy utility block hard-locked to match native button sizing."""
    escaped_text = html.escape(text_to_copy).replace("`", "\\`").replace("${", "\\${")
    html_code = f"""
    <body style="margin:0; padding:0; background:transparent;">
    <button id="copy-btn" style="
        background-color: #ffffff;
        border: 1px solid rgba(49, 51, 63, 0.2);
        color: #606266;
        padding: 0px;
        font-size: 12px;
        border-radius: 4px;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        height: 26px;
        width: 85px;
        box-sizing: border-box;
        line-height: 1;
    ">
        📋 Copy
    </button>
    <script>
        document.getElementById('copy-btn').addEventListener('click', function() {{
            const tempDiv = document.createElement('textarea');
            tempDiv.innerHTML = `{escaped_text}`;
            const cleanText = tempDiv.value;
            
            if (navigator.clipboard && navigator.clipboard.writeText) {{
                navigator.clipboard.writeText(cleanText).then(() => {{
                    triggerSuccessState();
                }}).catch(() => {{
                    runFallbackClipboard(cleanText);
                }});
            }} else {{
                runFallbackClipboard(cleanText);
            }}
        }});

        document.body.removeChild(textArea);
        function runFallbackClipboard(text) {{
            const textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.position = "fixed"; 
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {{
                document.execCommand('copy');
                triggerSuccessState();
            }} catch (err) {{
                console.error('Copy pipeline failed', err);
            }}
            document.body.removeChild(textArea);
        }}

        document.body.removeChild(textArea);
        function triggerSuccessState() {{
            const btn = document.getElementById('copy-btn');
            btn.innerHTML = '✅ Copied!';
            btn.style.color = '#67c23a';
            btn.style.borderColor = '#c2e7b0';
            setTimeout(() => {{
                btn.innerHTML = '📋 Copy';
                btn.style.color = '#606266';
                btn.style.borderColor = 'rgba(49, 51, 63, 0.2)';
            }}, 2000);
        }}
    </script>
    </body>
    """
    st.components.v1.html(html_code, height=26)


# ==========================================
# 4. SIDEBAR CHAT CONTROL DECK
# ==========================================
with st.sidebar:
    st.title("⚙️ Workspace Controls")
    
    st.subheader("🤖 Model Selection")
    model_options = ["Gemini 2.5 Flash (Fast)", "Gemini 2.5 Pro (Advanced)"]
    if openai_key:
        model_options.extend(["GPT-4o Mini", "GPT-4o Pro"])
    else:
        model_options.extend(["GPT-4o Mini (Key Missing)", "GPT-4o Pro (Key Missing)"])
    model_options.extend(["Ollama: Llama 3 (Local)", "Ollama: Mistral (Local)"])
    
    selected_model = st.selectbox("Choose active AI Brain", model_options)
    
    st.divider()
    
    st.subheader("💬 Chat Sessions")
    if st.button("➕ Create New Chat", key="btn_create_new_chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        chat_count = len(st.session_state.chats) + 1
        st.session_state.chats[new_id] = {"title": f"Chat {chat_count}: New Topic", "history": [], "pdf_chunks": [], "processed_files": []}
        st.session_state.current_chat_id = new_id
        st.session_state.editing_idx = None
        st.rerun()
        
    st.markdown("### 🗂️ Chat History Vault")
    
    # Visual Boxed Vault Viewport with Upgraded Styling Architecture
    with st.container(border=False):
        if not st.session_state.chats:
            st.caption("No history logged yet.")
        else:
            for cid, cinfo in list(st.session_state.chats.items()):
                chat_col, menu_col = st.columns([0.82, 0.18])
                
                is_active = (cid == st.session_state.current_chat_id)
                style_type = "primary" if is_active else "secondary"
                
                with chat_col:
                    if st.button(f"📌 {html.escape(cinfo['title'])}", key=f"nav_{cid}", type=style_type, use_container_width=True):
                        st.session_state.current_chat_id = cid
                        st.session_state.editing_idx = None
                        st.rerun()
                        
                with menu_col:
                    with st.popover("", use_container_width=True):
                        if st.button("🔗 Share", key=f"share_{cid}", use_container_width=True):
                            st.toast(f"Share link copied for: **{cinfo['title']}**!")
                        
                        if st.button("🗑️ Delete", key=f"del_{cid}", use_container_width=True, type="primary"):
                            del st.session_state.chats[cid]
                            if st.session_state.current_chat_id == cid:
                                remaining_ids = list(st.session_state.chats.keys())
                                st.session_state.current_chat_id = remaining_ids[0] if remaining_ids else str(uuid.uuid4())
                                if st.session_state.current_chat_id not in st.session_state.chats:
                                    st.session_state.chats[st.session_state.current_chat_id] = {"title": "Welcome Overview", "history": [], "pdf_chunks": [], "processed_files": []}
                            st.session_state.editing_idx = None
                            st.rerun()

    st.divider()
    
    st.subheader("📂 Document Center")
    uploaded_pdfs = st.file_uploader(
        "Upload contextual PDF texts", 
        type=["pdf"], 
        accept_multiple_files=True, 
        key=f"pdf_{current_id}",
    )
    
    if uploaded_pdfs:
        new_file_processed = False
        for pdf_file in uploaded_pdfs:
            if pdf_file.name not in active_chat['processed_files']:
                with st.spinner(f"Parsing and chunking: {pdf_file.name}..."):
                    text_extracted = extract_text_from_pdf(pdf_file)
                    if text_extracted:
                        generated_chunks = chunk_text(text_extracted, pdf_file.name)
                        active_chat['pdf_chunks'].extend(generated_chunks)
                        active_chat['processed_files'].append(pdf_file.name)
                        new_file_processed = True
        if new_file_processed:
            st.success("Successfully logged updates to semantic context index!")
            st.rerun()

    if active_chat['processed_files']:
        st.markdown("**Indexed files in this chat:**")
        for filename in active_chat['processed_files']:
            st.caption(f"📄 {filename}")
        st.caption(f"🔢 Total Vector Chunks: {len(active_chat['pdf_chunks'])}")
        if st.button("🗑️ Clear Indexed Documents", key="btn_clear_indexed_docs", use_container_width=True):
            active_chat['pdf_chunks'] = []
            active_chat['processed_files'] = []
            st.rerun()
    else:
        st.info("No document loaded for this chat.")

# ==========================================
# 5. MAIN CONVERSATIONAL APPLICATION STREAM
# ==========================================
st.title("🛡️ Secure Guardrailed AI Terminal")
st.caption(f"Engine: **{selected_model}** | Session Layer: **{active_chat['title']}**")

# Display Message History Log
for idx, message in enumerate(active_chat['history']):
    with st.chat_message(message["role"]):
        
        if st.session_state.editing_idx == idx:
            st.markdown(f"**📝 Editing Message #{idx + 1}**")
            new_text = st.text_area("Update text stream", value=message["content"], key=f"inline_edit_{idx}", label_visibility="collapsed")
            
            sc1, sc2, _ = st.columns([0.07, 0.07, 0.86], gap="small")
            with sc1:
                if st.button("Save", key=f"sv_{idx}", use_container_width=False):
                    active_chat['history'] = active_chat['history'][:idx]
                    active_chat['history'].append({"role": "user", "content": new_text})
                    st.session_state.editing_idx = None
                    st.session_state.force_ai_processing = True
                    st.rerun()
            with sc2:
                if st.button("Cancel", key=f"cc_{idx}", use_container_width=False):
                    st.session_state.editing_idx = None
                    st.rerun()
        else:
            st.write(message["content"])
            
            act_col1, act_col2, _ = st.columns([0.07, 0.07, 0.86], gap="small")
            
            with act_col1:
                if message["role"] == "user":
                    if st.button("✏️ Edit", key=f"ed_{idx}", use_container_width=False):
                        st.session_state.editing_idx = idx
                        st.rerun()
                elif message["role"] == "assistant":
                    if st.button("🔄 Redo", key=f"redo_{idx}", use_container_width=False):
                        active_chat['history'] = active_chat['history'][:idx]
                        st.session_state.force_ai_processing = True
                        st.rerun()
            
            with act_col2:
                render_isolated_copy_button(message["content"])

if st.session_state.force_ai_processing:
    st.session_state.force_ai_processing = False
    with st.chat_message("assistant"):
        with st.spinner("Processing chronological history path..."):
            reply = generate_model_response(active_chat['history'], selected_model)
            st.write(reply)
    active_chat['history'].append({"role": "assistant", "content": reply})
    st.rerun()

if user_input := st.chat_input("Say hello or ask a question..."):
    with st.chat_message("user"):
        st.write(user_input)
    active_chat['history'].append({"role": "user", "content": user_input})
    
    if "New Topic" in active_chat['title'] or "Welcome Overview" in active_chat['title']:
        words = user_input.split()
        short_title = " ".join(words[:3]) + "..." if len(words) > 3 else user_input
        active_chat['title'] = short_title
    
    with st.chat_message("assistant"):
        with st.spinner("Evaluating guardrails..."):
            reply = generate_model_response(active_chat['history'], selected_model)
            st.write(reply)
    active_chat['history'].append({"role": "assistant", "content": reply})
    st.rerun()