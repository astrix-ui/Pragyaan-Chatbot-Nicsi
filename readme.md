# 🧠 Chatbot with Company Knowledge Base (FastAPI + LangChain + Ollama)

This is a local AI-powered chatbot built with **FastAPI**, **LangChain**, **ChromaDB**, and **Ollama's LLaMA 3 model**. It answers user queries based **only on your uploaded company data** (PDFs or JSON).

---

## 🚀 Features

- 💬 Conversational chat interface via REST API
- 📄 Upload PDFs to train the chatbot
- 🧠 Uses vector search (ChromaDB) + `llama3` model via Ollama
- ✅ Follows company data strictly — won't hallucinate

---

## ⚙️ Requirements

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running locally
- `llama3` model pulled in Ollama:
  ```bash
  ollama pull llama3
