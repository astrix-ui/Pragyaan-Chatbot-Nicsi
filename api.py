from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.documents import Document
import json
from datetime import datetime
from pathlib import Path
import fitz  # PyMuPDF
import traceback
import shutil

# === Constants ===
CHROMA_DIR = "chroma_store"
QUERIES_FILE = "user_queries.json"
COMPANY_DATA_FILE = "company_data.json"

# === FastAPI Setup ===
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Load and Embed Company Knowledge Base ===
def load_company_data():
    try:
        with open(COMPANY_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 💡 Include the title in the embedded content for better match
        documents = [f"{entry['title']}. {entry['content']}" for entry in data]
        metadatas = [{"title": entry["title"]} for entry in data]

        # 🔄 Optionally clear old DB (you can also delete 'chroma_store' manually)
        if Path(CHROMA_DIR).exists():
            shutil.rmtree(CHROMA_DIR)

        embeddings = OllamaEmbeddings(model="llama3")
        vectorstore = Chroma.from_texts(
            documents, embeddings, metadatas=metadatas, persist_directory=CHROMA_DIR
        )
        return vectorstore, data
    except Exception as e:
        print(f"[ERROR] Failed to load company data: {e}")
        return None, []

vectorstore, company_data_raw = load_company_data()

# === Model & Prompt ===
system_message = SystemMessagePromptTemplate.from_template(
    "You are a helpful assistant. ONLY use the company data provided to answer the user's questions. If the answer is not found in the data, reply: 'I couldn’t find that information in our company records.'"
)

model = ChatOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # Any non-empty value works
    model="llama3"
)

chat_history_store = []

# === Models ===
class ChatRequest(BaseModel):
    text: str
    chat_history: list = []

class ChatResponse(BaseModel):
    response: str
    chat_history: list

# === Helpers ===
def save_user_query(query: str):
    try:
        Path(QUERIES_FILE).touch(exist_ok=True)
        try:
            with open(QUERIES_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
        data.append({"query": query, "timestamp": datetime.now().isoformat()})
        with open(QUERIES_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving query: {e}")

@app.post("/api/save-query")
async def save_query_endpoint(request: ChatRequest):
    try:
        save_user_query(request.text)
        return {"message": "Query saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_history():
    history = [system_message]
    for chat in chat_history_store:
        history.append(HumanMessagePromptTemplate.from_template(chat["user"]))
        history.append(AIMessagePromptTemplate.from_template(chat["assistant"]))
    return history

def generate_response(history):
    messages = ChatPromptTemplate.from_messages(history).format_messages()
    print("🧠 Final Prompt to Model:\n", messages)  # Debug output
    return model.invoke(messages)

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        text = request.text.strip()
        save_user_query(text)

        history = get_history()
        history.append(HumanMessagePromptTemplate.from_template(text))

        docs = []
        if vectorstore:
            docs = vectorstore.similarity_search(text, k=5)
            print(f"🔍 Similarity search returned {len(docs)} documents")

        if not docs and company_data_raw:
            for item in company_data_raw:
                if text.lower() in item["content"].lower():
                    docs.append(Document(page_content=item["content"], metadata={"title": item["title"]}))

        if docs:
            print("✅ Injected context from company knowledge")
            print(f"→ Match count: {len(docs)}\n")
            for i, doc in enumerate(docs):
                print(f"Doc {i+1}: [{doc.metadata.get('title', '')}] {doc.page_content[:100]}...\n")

            company_context = "\n\n".join([
                f"[{doc.metadata.get('title', 'General')}] {doc.page_content}" for doc in docs
            ])

            history.insert(1, HumanMessagePromptTemplate.from_template(
                f"""You are a company assistant. Use ONLY the data below to answer the user's question truthfully.

--- Company Data Start ---
{company_context}
--- Company Data End ---

User's Question: {text}
"""
            ))
        else:
            print("❌ No match found in vectorstore or raw data.")
            chat_history_store.append({"user": text, "assistant": "I couldn’t find that information in our company records."})
            return {"response": "I couldn’t find that information in our company records.", "chat_history": chat_history_store}

        response = generate_response(history)
        chat_history_store.append({"user": text, "assistant": response.content})

        return {"response": response.content, "chat_history": chat_history_store}
    except Exception as e:
        print("🔥 ERROR TRACEBACK:\n", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        pdf_bytes = await file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        title = Path(file.filename).stem

        Path(COMPANY_DATA_FILE).touch(exist_ok=True)
        try:
            with open(COMPANY_DATA_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []

        data.append({"title": title, "content": text.strip()})

        with open(COMPANY_DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

        global vectorstore, company_data_raw
        vectorstore, company_data_raw = load_company_data()
        print(f"📄 Loaded {len(data)} sections from company_data.json")

        return {"message": "PDF uploaded and data extracted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
