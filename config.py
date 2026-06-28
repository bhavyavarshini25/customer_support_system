"""
Central Ollama model configuration for chat and embeddings.
"""

import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama, OllamaEmbeddings

load_dotenv()

CHAT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

LLM = ChatOllama(
    model=CHAT_MODEL,
    temperature=0.2,
)

EMBEDDINGS = OllamaEmbeddings(
    model=EMBED_MODEL,
)
