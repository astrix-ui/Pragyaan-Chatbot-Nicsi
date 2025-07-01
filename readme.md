# 🧠 Company Knowledge Chatbot

A full-stack AI-powered chatbot that answers user queries based solely on uploaded PDFs and semantically scraped company website data. Built using FastAPI, LangChain, Ollama (LLaMA 3), and React.

---

## ⚙️ Tech Stack

- **FastAPI** (Python backend)
- **LangChain** + **Ollama (LLaMA 3)** for LLM interaction and embeddings
- **ChromaDB** as the vector store
- **React** frontend (in `/chatbot-app`)
- **PyMuPDF (fitz)** for PDF extraction
- **BeautifulSoup + Selenium** for semantic web scraping

---

## 📁 Project Structure

```
chatbot/
├── api.py                   # FastAPI backend API
├── categorize_to_vector.py # Converts scraped/categorized data into vector embeddings
├── semantic_scraper.py     # Deep crawler + categorizer using LLaMA3
├── company_data.json       # Stores structured content (scraped + PDFs)
├── user_queries.json       # Stores history of user queries
├── chroma_store/           # Folder containing Chroma vector DB
├── requirements.txt        # Python dependencies
├── chatbot-app/            # React frontend app
└── README.md               # This file
```

---

## 🚀 Getting Started

### 🔧 1. Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate       # On Windows
# or
source venv/bin/activate    # On macOS/Linux

# Install Python dependencies
pip install -r requirements.txt
```

### 🦙 2. Run Ollama with LLaMA 3

Make sure [Ollama](https://ollama.com/download) is installed and running:

```bash
ollama run llama3
```

### 🧠 3. Start the FastAPI Server

```bash
python api.py
```

This will load `company_data.json` into Chroma vector store and expose the backend API on `http://localhost:8000`.

---

### 🌐 4. Frontend (React)

```bash
cd chatbot-app
npm install
npm start
```

Visit [http://localhost:3000](http://localhost:3000) to start chatting with your data.

---

## 📄 Uploading PDFs

You can upload PDF documents via the frontend UI. They will be parsed and appended to `company_data.json` and embedded into Chroma vector DB automatically.

---

## 🌍 Scraping a Website

To scrape and categorize website content:

```bash
python semantic_scraper.py
```

Then embed that data:

```bash
python categorize_to_vector.py
```

---

## 🔁 Resetting Vector DB

To clear Chroma vector store and re-embed:

```bash
# Windows
rmdir /s /q chroma_store

# macOS/Linux
rm -rf chroma_store
```

Then rerun `api.py`.

---

## 📌 Maintained By

**Ayush Sharma**
