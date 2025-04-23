from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage
import os

def load_zendesk_documents(base_path="zendesk_text"):
    base_path = Path(base_path)
    documents = []
    for file_path in base_path.rglob("*.txt"):
        loader = TextLoader(str(file_path), encoding="utf-8")
        docs = loader.load()
        # Tag metadata from path
        for doc in docs:
            doc.metadata["source"] = "zendesk"
            doc.metadata["topic"] = file_path.parents[1].name
            doc.metadata["category"] = file_path.parent.name
        documents.extend(docs)
    return documents

def chunk_documents(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    return splitter.split_documents(docs)


def create_and_save_faiss(docs, save_path="faiss_zendesk_store"):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(save_path)

def load_zendesk_vectorstore(path="faiss_zendesk_store"):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.load_local(path, embeddings)

def savePipline():
    docs = load_zendesk_documents()
    chunks = chunk_documents(docs)
    create_and_save_faiss(chunks)
    print("Data is saved with RAG")

def prompt_claude(prompt_text: str, model_name="claude-3-5-sonnet-20241022", temperature=0.0):
    api_key = "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"
    llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0 , anthropic_api_key=api_key)
    messages = [HumanMessage(content=prompt_text)]

    try:
        response = llm.invoke(messages)
        return response.content.strip()
    except Exception as e:
        return f"❌ Error invoking Claude: {str(e)}"


def chat_with_zendesk_context(query, vectorstore, k=3):
    relevant_docs = vectorstore.similarity_search(query, k=k)
    context = "\n\n".join([doc.page_content for doc in relevant_docs])

    prompt = f"""You are a helpful support assistant using Zendesk documentation to answer user queries.
    
Relevant Information:
{context}

User Query:
{query}

→ Based on the above, provide a concise and informative response."""
    
    return prompt_claude(prompt)





