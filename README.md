Here is a professional, detailed, and comprehensive `README.md` tailored specifically for your project. You can copy and paste this directly into your GitHub repository.

```markdown
# 🛡️ Secure Guardrailed Multi-LLM Chat Terminal

A production-ready, highly secure Streamlit chat interface featuring a **Dual-Layer Guardrail Architecture**. This application allows users to chat seamlessly with various commercial and local AI models (Gemini, OpenAI GPT, and Ollama/Mistral) while ensuring strict personal data protection (PII) and deterministic content filtering. It includes a multi-source RAG pipeline that handles simultaneous indexing and cross-comparison of multiple PDF documents.

---

## 📖 Table of Contents
1. [What is this?](#-what-is-this)
2. [Key Features](#-key-features)
3. [Prerequisites & Requirements](#-prerequisites--requirements)
4. [Local Installation & Setup](#-local-installation--setup)
5. [How to Use the Workspace](#-how-to-use-the-workspace)
6. [Security Architecture Detailing](#-security-architecture-detailing)

---

## 💡 What is this?
This project is an advanced, enterprise-grade AI chatbot platform built on top of **Streamlit**. It solves a common flaw found in local open-source models (like `mistral` or `llama3` via Ollama): their tendency to bypass system prompt guidelines under complex context injection. 

By employing a hybrid security approach—combining strict system instructions with an automated post-generation regex scrubber—this terminal guarantees that sensitive data patterns (e.g., emails, phone numbers, SSNs) are permanently redacted before ever being rendered in the UI view layers.

---

## ✨ Key Features

### 1. 🛡️ Dual-Layer Security & Guardrails
* **Input Filter Interceptor:** Drops toxic patterns, violent topics, or self-harm triggers locally before calling any API.
* **Deterministic Output Scrubber:** A post-execution regex layer that intercepts model outputs to securely redact phone numbers, private emails, and national identity numbers.

### 2. 🗂️ Universal Multi-Source RAG Pipeline
* **Simultaneous File Multi-Tenancy:** Context fractions from *every* uploaded document are shared in prompt slots dynamically, preventing any file from being dropped from model visibility.
* **Smart Overlap Chunking:** Utilizes a custom PyPDF2 parser with semantic lookback sliding windows to keep reference fragments highly coherent.

### 3. 🤖 Premium Agnostic Model Routing
* **Commercial Models:** Native hooks into Google Gemini (`gemini-2.5-flash`, `gemini-2.5-pro`) and OpenAI GPT (`gpt-4o-mini`, `gpt-4o`).
* **Local Privacy Engines:** Seamless local execution configurations via Ollama (`mistral`, `llama3`).

### 4. 💎 Deluxe UX Control Deck
* **Chat History Vault:** Full multi-session management allowing users to create, switch, share, or hard-delete individual conversations.
* **Inline Stream Editing:** Users can step back to edit past inputs or trigger localized model regenerations ("Redo") instantly.
* **Micro-scaled Copy Utility:** Custom sandboxed HTML/JS click-to-copy functionality attached beautifully to every assistant message box.

---

## 🛠️ Prerequisites & Requirements

Before running the application, ensure you have the following installed on your machine:
* **Python 3.9, 3.10, or 3.11**
* **Git**
* **Ollama Desktop** *(Optional: Only required if running local offline models like Mistral/Llama3)*

---

## 🚀 Local Installation & Setup

Follow these step-by-step instructions to get the application running on your computer:

### 1. Clone the Repository
Open your terminal or command prompt and clone the project:
```bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
cd YOUR_REPOSITORY_NAME

```

### 2. Establish a Virtual Environment

It is highly recommended to isolate your dependencies using a virtual environment:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

```

### 3. Install Required Dependencies

Install all necessary Python packages via `pip`:

```bash
pip install streamlit google-generativeai openai pypdf2 python-dotenv ollama

```

### 4. Configure Environment Variables

Create a file named `.env` in the root directory of the project and insert your API keys:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

```

> ⚠️ **Note:** If you don't possess an OpenAI API key, the system will gracefully disable GPT options while keeping Gemini and Local Ollama routes fully interactive.

### 5. Start Local Models (Optional)

If you wish to use local models like Mistral:

1. Ensure the Ollama background service application is running.
2. Pull the model through your terminal command line interface:
```bash
ollama pull mistral

```



### 6. Launch the Streamlit Terminal

Boot up the interface engine directly:

```bash
streamlit run app.py

```

Your default web browser should open a new tab automatically targeting `http://localhost:8501`.

---

## 📖 How to Use the Workspace

1. **Select Your Model:** Use the dropdown selector in the sidebar to declare your active AI brain configuration.
2. **Upload Documents:** Drop any collection of text PDFs into the **Document Center** tab. The system will slice them into vector chunks and verify the unified index payload instantly.
3. **Engage and Chat:** Ask questions regarding your files. If you notice a mistake in an earlier query, hover over your prompt card and press **✏️ Edit** to fix the chat lineage downstream.
4. **Manage Sessions:** Use the **➕ Create New Chat** action button to start distinct modular topics without muddying current variable stores.

---

## 🔒 Security Architecture Detailing

```
User Input ──> [Local Input Guardrails] ──> [Context / Multi-RAG Injection]
                                                        │
[UI Display Layer] <── [Regex PII Scrubber] <── [LLM Engine Processing]

```

Standard systems depend entirely on system instructions to enforce safety behavior. This terminal applies a **fail-safe loop** strategy:

1. **Prompt Containment:** The RAG text index blocks are wrapped inside strict system isolation rules.
2. **Deterministic Redaction:** If a model like `mistral` forgets its constraints and inadvertently surfaces a phone number or an email string pattern from the parsed files, the `clean_output_pii_scrubber` function catches it instantly and swaps it with safe string tokens (`[REDACTED]`) before it can draw on screen.

```

```
