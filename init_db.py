"""
Database initialization script.
Run this ONCE before starting the application.
Also builds the RAG vector store from company documents.
"""

import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from memory.sqlite_memory import init_db
from rag.rag_pipeline import build_vectorstore


def main():
    print("=" * 50)
    print("ABC Technologies - Support System Setup")
    print("=" * 50)

    # Step 1: Initialize SQLite memory DB
    print("\n[1/2] Initializing SQLite memory database...")
    init_db()
    print("      Done.")

    # Step 2: Build RAG vectorstore
    print("\n[2/2] Building RAG vectorstore from company documents...")
    build_vectorstore()
    print("      Done.")

    print("\nSetup complete. Run 'python main.py' to start the system.")


if __name__ == "__main__":
    main()
