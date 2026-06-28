"""
Task 6: RAG pipeline using company documents with ChromaDB vector store.
"""

from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document
from config import EMBEDDINGS

DOCS_DIR = Path(__file__).parent.parent / "docs"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

DOC_FILES = [
    "company_policy.txt",
    "pricing_guide.txt",
    "technical_manual.txt",
    "faq.txt",
]

_vectorstore = None


def build_vectorstore() -> Chroma:
    """Load documents, split, embed, and store in ChromaDB."""
    documents: list[Document] = []

    for fname in DOC_FILES:
        fpath = DOCS_DIR / fname
        if not fpath.exists():
            print(f"[RAG] Warning: {fpath} not found, skipping.")
            continue
        loader = TextLoader(str(fpath))
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = fname
        documents.extend(docs)

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    vectorstore = Chroma.from_documents(
        chunks, EMBEDDINGS, persist_directory=str(CHROMA_DIR)
    )
    print(f"[RAG] Vectorstore built with {len(chunks)} chunks.")
    return vectorstore


def get_vectorstore() -> Chroma:
    """Return existing vectorstore or build it."""
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    if CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir()):
        _vectorstore = Chroma(
            persist_directory=str(CHROMA_DIR), embedding_function=EMBEDDINGS
        )
        print("[RAG] Loaded existing vectorstore.")
    else:
        _vectorstore = build_vectorstore()

    return _vectorstore


def retrieve_context(query: str, k: int = 4) -> str:
    """Retrieve top-k relevant chunks for a query."""
    vs = get_vectorstore()
    docs = vs.similarity_search(query, k=k)
    if not docs:
        return "No relevant information found in knowledge base."
    parts = []
    for doc in docs:
        parts.append(f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)
