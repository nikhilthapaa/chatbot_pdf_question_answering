# 🛡️ Guardrailed Multi-Chat PDF QA Terminal

A secure, enterprise-grade conversational AI assistant built with **Streamlit** and **Google Gemini 2.5**. This application functions as a standard, polite chatbot for general chit-chat while seamlessly transitioning into a deep Document Intelligence tool when a PDF is provided.

What sets this project apart is its **Dual-Layer Hardwired Safety System**, which strictly monitors, blocks, and safely de-escalates harmful, unsafe, or sensitive user inputs.

---

## 📖 Table of Contents

1. What is this?
2. Key Features
3. Safety Guardrails Architecture
4. Prerequisites
5. Local Installation & Setup Guide
6. How to Use
---

## 🧐 What is this?

This repository contains a full-stack, single-file Python web application that allows users to create separate conversational streams (similar to ChatGPT or Gemini) and query large PDF texts securely.

The chatbot acts as a friendly, calm assistant that handles normal greetings gracefully, answers general logic questions, and respects absolute safety boundaries regarding explicit content, self-harm, or extreme violence.

---

## ⚡ Key Features

* **Multi-Chat Session Manager:** Dynamically spin up, title, navigate, or permanently delete independent chat sessions without losing track of other active topics.
* **Context Isolation:** Documents uploaded in one chat tab remain securely isolated to that specific thread, preventing cross-contamination of sensitive data.
* **Dynamic Engine Routing:** A sidebar option lets the user switch on the fly between Google's active foundational models:
* `Gemini 2.5 Flash` (Optimized for lightning-fast speeds)
* `Gemini 2.5 Pro` (Optimized for complex document extraction and analytical reasoning)


* **Automatic Chat Renaming:** The interface automatically extracts context from your first message to dynamically replace generic tab titles with contextually relevant titles.
* **De-escalation UI Engine:** If pushed with hostile inputs or policy violations, the chatbot uses a compassionate, unyielding rejection layout instead of generic application crashes.

---

## 🛡️ Safety Guardrails Architecture

The chatbot relies on an absolute, multi-tiered security perimeter:

| Security Layer | Mechanism | Target Threats |
| --- | --- | --- |
| **Layer 1: Local Pre-filter Interceptor** | Regex and text pattern matching executed completely in local runtime *before* calling cloud APIs. | Suicidal ideation, self-harm keywords, explicit sexual terms, acts of violence. |
| **Layer 2: Google Safety Directives** | Built-in Gemini backend filtering thresholds set strictly to `BLOCK_LOW_AND_ABOVE`. | Harassment, Hate Speech, Dangerous Content, Explicit Adult Material. |
| **Layer 3: System Instruction Anchors** | System-level prompt injections overrides model behaviors. | Prevents leakage of PII (Addresses, Passwords, SSNs) found inside documents; strictly enforces an ultra-calm, professional tone. |

---

## 🛠️ Prerequisites

Before launching the app, ensure you have the following installed on your local computer:

* **Python 3.10 to Python 3.14**
* A valid **Google Gemini API Key** (Get one for free at [Google AI Studio](https://www.google.com/search?q=https://aistudio.google.com/))
* *(Optional)* An OpenAI API Key if you intend to unlock the secondary GPT dropdown options.

---

## 💻 Local Installation & Setup Guide

Follow these sequential steps to pull down and run this repository locally:

### 1. Clone or Pull the Code

Open your terminal and clone this repository (or fetch the latest updates if you have already cloned it):

```bash
git clone https://github.com/nikhilthapaa/chatbot_pdf_question_answering.git
cd YOUR_REPO_NAME

```

### 2. Establish a Virtual Environment

It is highly recommended to use an isolated environment to prevent version conflicts with your globally installed packages:

```bash
# Create the environment
python3 -m venv .venv

# Activate the environment (Linux / macOS)
source .venv/bin/activate

# Activate the environment (Windows PowerShell)
# .venv\Scripts\Activate.ps1

```

### 3. Install Required Dependencies

Install the explicit Python packages required by the core processing framework:

```bash
pip install streamlit google-generativeai pypdf2 python-dotenv

```

### 4. Configure Your Local Keys (`.env`)

Create an environment configurations file named `.env` in the absolute **root directory** of your project:

```bash
touch .env

```

Open the `.env` file in your preferred text editor and add your secure variables:

```env
GOOGLE_API_KEY="AIzaSyYourActualGeminiAPIKeyGoesHere"
OPENAI_API_KEY="sk-proj-OptionalOpenAIKey"

```

> **⚠️ Security Warning:** Never commit your `.env` file to a public GitHub repository. Ensure `.env` is listed inside your `.gitignore` file.

### 5. Launch the Web Application

Start your Streamlit development server locally:

```bash
streamlit run guardials_testing.py

```

The app will compile instantly and provide your local access links (usually `http://localhost:8501`).

---

## 🚀 How to Use

1. **Standard Chat:** Type `"Hello!"` or `"Can you help me brainstorm a recipe?"` directly into the chat bar. The system will handle standard queries exactly like a default assistant.
2. **Analyze Documents:** Head to the sidebar control deck, create or pick a chat session, and drop a PDF file into the file uploader. Ask questions directly relating to your text.
3. **Test the Defenses:** Try asking something unsafe or trying to extract a fake credit card number contained inside your PDF. Watch the engine gracefully flag and securely divert the request using polite language.
