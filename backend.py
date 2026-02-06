from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import Config
from langchain_core.prompts import ChatPromptTemplate
from operator import itemgetter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from textwrap import dedent

#INITIALIZATION FUNCTIONS

def get_llm():
    """Returns the Gemini LM instance"""
    return ChatGoogleGenerativeAI(
        model=Config.LLM_MODEL,
        google_api_key=Config.GEMINI_API_KEY,
        temperature=0.5)

def get_embeddings():
    """Return Embeddings model"""
    return HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL)

def get_vector_store():
    """Returns ChromaDB instance"""
    return Chroma(
        collection_name=Config.COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=Config.CHROMA_PATH
    )

#INGESTION LOGIC

def ingest_files(uploaded_files):
    documents = []
    for file in uploaded_files:
        text = file.read().decode("utf-8")
        doc = Document(page_content=text, metadata={"source": file.name})
        documents.append(doc)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP
    )
    
    splits = text_splitter.split_documents(documents)
    
    if splits:
        vectorstore = get_vector_store()
        vectorstore.add_documents(splits)
            
    return len(splits)

def format_history(messages, max_chars=Config.MAX_HISTORY_CHARS):
    """Format the history using a sliding window"""
    buffer=[]
    total_chars=0

    #from newest to oldest messages
    for msg in reversed(messages[:-1]):
        msg_content=msg.get("content","")
        msg_len=len(msg_content)

        #Verify if fits in budget
        if total_chars+msg_len>max_chars:
            break

        buffer.insert(0, msg)
        total_chars+=msg_len
    
    formatted_text=""
    for msg in buffer:
        role= "User" if msg["role"]=="user" else "Assistant"
        formatted_text+=f"{role}: {msg['content']}\n"
    
    return formatted_text

#RETRIEVAL LOGIC

# We will use a generator function for the UI
def stream_rag_response(user_query, chat_history):
    """
    Generator that yields chunks of the response.
    Also returns the source documents as the last yielded item (or handles them via callback).
    For simplicity in Streamlit, we will yield text chunks, and maybe store docs in session state via a side effect mechanism,
    OR we execute retrieval first, then stream LLM.
    """
    vectorstore = get_vector_store()
    retriever = vectorstore.as_retriever(search_kwargs={"k": Config.RETRIEVAL_K})
    
    # 1. Retrieve first (Synchronous part)
    docs = retriever.invoke(user_query)
    source_docs = docs
    
    # 2. Format context
    context_text = "\n\n".join([doc.page_content for doc in docs])
    if not context_text:
        context_text = "No relevant context found in the documents"
        
    # 3. Format history
    history_text = format_history(chat_history)
    
    # 4. Prepare prompt
    # Using dedented string to avoid unexpected indentation in LLM input
    from textwrap import dedent
    
    human_msg = dedent("""
    CONTEXT:
    {context}
    
    CHAT HISTORY:
    {history}
    
    QUESTION:
    {question}
    """).strip()
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", Config.SYSTEM_INSTRUCTION),
        ("human", human_msg)
    ])
    
    llm = get_llm()
    
    # Use StrOutputParser to get string chunks directly
    from langchain_core.output_parsers import StrOutputParser
    chain = prompt_template | llm | StrOutputParser()
    
    # 5. Stream
    stream = chain.stream({
        "context": context_text,
        "history": history_text,
        "question": user_query
    })
    
    for chunk in stream:
        yield chunk

    # We can't yield docs easily in a pure text stream consumed by st.write_stream
    # So we will provide a separate synchronous helper to get docs 
    # or rely on the caller to call retrieval if they need sources displayed.
    
def get_docs_for_query(user_query):
    """Helper to retrieve docs without generation"""
    vectorstore = get_vector_store()
    retriever = vectorstore.as_retriever(search_kwargs={"k": Config.RETRIEVAL_K})
    return retriever.invoke(user_query)


