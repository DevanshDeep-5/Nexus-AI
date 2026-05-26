<div align="center">
  <img src="extension/icons/icon128.png" width="128" height="128" alt="Ask This Page AI Logo" />
  <h1>🧠 Ask This Page AI</h1>
  <p><strong>Chat with any webpage, get summaries, structured notes, and extract insights directly from your Chrome browser.</strong></p>

  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![React](https://img.shields.io/badge/react-%2320232a.svg?style=flat&logo=react&logoColor=%2361DAFB)](https://reactjs.org/)
  [![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
  [![Chrome Extensions](https://img.shields.io/badge/Chrome-Extensions-red.svg?logo=google-chrome&logoColor=white)](https://developer.chrome.com/docs/extensions/)
</div>

---

## 🌟 Overview

**Ask This Page AI** is a powerful Chrome Extension that empowers you to interact with long articles, documentation, or YouTube videos effortlessly. It seamlessly extracts the content of the active tab and passes it through a Retrieval-Augmented Generation (RAG) pipeline powered by OpenAI/OpenRouter, giving you pinpointed answers, summaries, debates, and notes—all grounded **strictly** in the context of the page.

### 🎯 Key Features

- **💬 Chat & Q&A:** Ask questions about the page content, and the AI will search the text to give you a precise answer.
- **⚡ TL;DR Summaries:** Get a quick 5-point takeaway with key insights in a single click.
- **👶 ELI5 (Explain Like I'm 5):** Simplifies complex jargon or difficult concepts into easily digestible explanations.
- **📝 Structured Notes:** Automatically generates structured, readable notes with definitions for key terms.
- **⚔️ Debate Mode:** Extracts the main arguments of the page and presents the "For" and "Against" perspectives.
- **🔍 Source Highlighting:** The AI cites its sources. Clicking a citation highlights the exact text on the actual webpage!
- **📋 Floating Action Menu:** Simply select text on any page to quickly Summarize, Explain, or Find Examples for that specific text.
- **📺 YouTube Transcript Support:** Works flawlessly on YouTube videos by extracting transcripts for video Q&A.
- **🌗 Dark/Light Mode UI:** Beautiful, responsive UI built with Tailwind CSS that respects your system theme.

---

## 📸 Screenshots & Demo

> **Note:** Add your screen recordings or screenshots here to showcase the extension in action!
> 
> Example:
> ```markdown
> ![App Demo](path/to/demo.gif)
> ```

---

## 🏗️ Architecture

This project is split into two perfectly decoupled layers:

1. **Frontend (`/extension`)**: A Manifest V3 Chrome Extension. Uses React and Vite to render a beautiful side panel. Content scripts extract the page's text (or YouTube captions) and handle text highlighting.
2. **Backend (`/backend`)**: A robust, asynchronous FastAPI Python server. It manages the LLM integrations, text chunking, embedding generation (via ChromaDB), and vector similarity searches to power the RAG engine.

```text
📦 Ask This Page AI
 ┣ 📂 backend                 # Python FastAPI Server
 ┃ ┣ 📂 app
 ┃ ┃ ┣ 📂 routes              # API Endpoints (ask, summarize, eli5, etc.)
 ┃ ┃ ┗ 📂 services            # RAG, LLM integrations, and text extractors
 ┃ ┣ 📜 main.py               # FastAPI application entry point
 ┃ ┣ 📜 requirements.txt      # Python dependencies
 ┃ ┗ 📜 .env.example          # Template for backend environment variables
 ┗ 📂 extension               # Chrome Extension (React + Vite)
   ┣ 📂 src
   ┃ ┣ 📂 background          # Service Worker (Extension Lifecycle)
   ┃ ┣ 📂 content             # Content Scripts (DOM extraction, highlighting)
   ┃ ┗ 📂 sidepanel           # React App (The UI you interact with)
   ┣ 📜 manifest.json         # Chrome Extension Manifest V3
   ┣ 📜 package.json          # Node dependencies and build scripts
   ┗ 📜 vite.config.ts        # Vite bundler configuration
```

---

## 🚀 Getting Started

Follow these steps to run the project locally.

### 1️⃣ Prerequisites

- **Node.js** (v18 or higher)
- **Python** (v3.11 or higher)
- **API Keys**: An API key from [OpenAI](https://platform.openai.com/) or [OpenRouter](https://openrouter.ai/) (which offers free models like Llama 3).

### 2️⃣ Start the Backend Server

The backend requires Python and running a local FastAPI server on port `8000`.

```bash
# 1. Navigate to the backend directory
cd backend

# 2. Create and activate a Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Open .env and add your OPENAI_API_KEY (or OPENROUTER_API_KEY)

# 5. Start the server (auto-reloads on file changes)
uvicorn main:app --reload --port 8000
```

> **Note:** On your first run, the backend will download a local sentence-transformer embedding model (~80MB).

You can view the interactive API documentation at `http://localhost:8000/docs`.

### 3️⃣ Build the Chrome Extension

The frontend is a React application built with Vite.

```bash
# 1. Open a new terminal and navigate to the extension directory
cd extension

# 2. Install dependencies
npm install

# 3. Start the Vite development build (rebuilds automatically)
npm run dev

# (Alternatively, to create a production build, run: npm run build)
```

### 4️⃣ Load the Extension in Chrome

1. Open Google Chrome and go to `chrome://extensions/`.
2. Turn on **Developer mode** in the top right corner.
3. Click the **Load unpacked** button.
4. Select the `extension/dist` folder (created by the Vite build process).
5. Pin the extension to your toolbar. Click it on any page to open the Ask This Page AI side panel!

---

## ⚙️ Configuration & Environment Variables

The project requires configuring a `.env` file in the `backend/` directory. (See `backend/.env.example`).

**Supported Providers:**
- **OpenAI:** `OPENAI_API_KEY=sk-...`
- **OpenRouter:** Use free models if you don't have credits. Set `OPENAI_API_KEY=sk-or-...` and change `OPENAI_MODEL` to a free variant (e.g., `meta-llama/llama-3.2-3b-instruct:free`).

**RAG Settings:**
You can tweak the text chunking and overlap logic in your `.env`:
```ini
CHUNK_SIZE=512
CHUNK_OVERLAP=50
MAX_PAGE_LENGTH=100000
TOP_K_RESULTS=5
```

---

## 🛡️ Security & Privacy

- **No Data Hoarding:** The backend receives page context, processes the answer in memory/local vector db, and returns it. Nothing is permanently stored on the server.
- **Isolated Context:** Content scripts run in an isolated world and the floating menu utilizes the Shadow DOM to prevent CSS bleeding and interference with host websites.
- **API Keys are Hidden:** The extension does not store API keys. All keys remain safely on the backend server.

---

## 🐛 Troubleshooting

| Symptom | Fix |
|---------|-----|
| **No chat response, no error** | Ensure the backend is running. Rebuild extension (`npm run build`), reload in `chrome://extensions`, and **refresh the webpage**. |
| **`402 Insufficient credits`** | Update your `backend/.env` to use a free model, e.g. `meta-llama/llama-3.2-3b-instruct:free` (via OpenRouter) |
| **Empty page error** | Extensions cannot run on `chrome://` or `edge://` pages. Go to a normal webpage (like wikipedia.org), refresh the tab, and try again. |

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
