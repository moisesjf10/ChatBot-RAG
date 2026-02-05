import os
from dotenv import load_dotenv

#load environment variables
load_dotenv()

class Config:
    #API key
    GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")

    #LLM Model
    LLM_MODEL="gemini-3-flash-preview"

    #Model for creating vector embeddings
    EMBEDDING_MODEL="all-MiniLM-L6-v2"

    #Path where the vector database will persist on disk
    CHROMA_PATH="./chroma_langchain_db"

    #Name of the collection inside ChromaDB
    COLLECTION_NAME="knowledge_base"

    #TEXT SPLITTING
    CHUNK_SIZE=600 #Characters per chunk
    CHUNK_OVERLAP=100 

    #Memory optimization
    MAX_HISTORY_MESSAGES=10
    MAX_HISTORY_CHARS=2000

    #Number of documents to retrieve for each query
    RETRIEVAL_K=6

    # --- SYSTEM PROMPT ---
    # Define personality
    SYSTEM_INSTRUCTION = """
                        You are a specialized technical assistant.
                        Rules:
                        1. Answer only using the provided context.
                        2. Be concise and professional.
                        3. If unsure, admit it directly.
                        """

    @staticmethod
    def validate():
        """
        Validates that API key is available
        """
        if not Config.GEMINI_API_KEY:
            raise ValueError(
                "CRITICAL ERROR: 'GEMINI_API_KEY' not found. "
                "Please create a .env file with your API key."
            )