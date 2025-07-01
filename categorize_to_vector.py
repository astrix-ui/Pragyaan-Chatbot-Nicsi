# STEP: Embed categorized data into vector store for chatbot
import json
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from pathlib import Path

# === Load Categorized Data ===
categorized_file = "pragyan_navbar_pages_categorized.json"
with open(categorized_file, "r", encoding="utf-8") as f:
    categorized = json.load(f)

# === Prepare Data ===
documents = []
metadatas = []
for category, entries in categorized.items():
    grouped_text = "\n".join(f"[{e['tag'].upper()}] {e['text']} (Source: {e['url']})" for e in entries)
    documents.append(grouped_text)
    metadatas.append({"category": category})

# === Create Vector Store ===
vectorstore_dir = "chroma_store"
embeddings = OllamaEmbeddings(model="llama3:1b")
vectorstore = Chroma.from_texts(
    texts=documents,
    embedding=embeddings,
    metadatas=metadatas,
    persist_directory=vectorstore_dir
)

# Optional: save the processed data for use in API
structured_data = [
    {"title": meta["category"], "content": doc}
    for doc, meta in zip(documents, metadatas)
]

with open("company_data.json", "w", encoding="utf-8") as f:
    json.dump(structured_data, f, indent=2, ensure_ascii=False)

print("✅ Vectorstore updated and company_data.json written.")
