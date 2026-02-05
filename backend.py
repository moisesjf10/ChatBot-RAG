from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import Config
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
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

def get_rag_response(user_query, chat_history):
    """Manual RAG Pipeline
    1.Search DB
    2.Build prompt string
    3.Call LLM
    """
    llm=get_llm()
    vectorstore=get_vector_store()

    #Find most similar documents
    retriever=vectorstore.as_retriever(search_kwargs={"k":Config.RETRIEVAL_K})
    docs=retriever.invoke(user_query)#do the search

    #Context building
    context_text="\n\n".join([doc.page_content for doc in docs])

    if not context_text:
        context_text="No relevant context found in the documents"

    #history processing
    history_text=format_history(chat_history)

    #Prompt emgineering
    system_part=Config.SYSTEM_INSTRUCTION

    human_part=f"""Please answer the question based on the following information:

    KNOWLEDGE BASE:
    {context_text}

    CONVERSATION HISTORY:
    {history_text}

    USER QUESTION:
    {user_query}
    """
    prompt=ChatPromptTemplate.from_messages([
        ("system", system_part),
        ("human", "{input_data}")
    ])

    chain=prompt|llm
    response_message=chain.invoke({"input_data": human_part})
    content = response_message.content
    final_answer = ""

    if isinstance(content, str):
        # Si ya es texto, todo bien
        final_answer = content
    elif isinstance(content, list):
        # Si es una lista (tu caso), unimos las partes de texto
        for part in content:
            if isinstance(part, dict) and "text" in part:
                final_answer += part["text"]
            elif isinstance(part, str):
                final_answer += part
    else:
        # Por si acaso es otro tipo raro
        final_answer = str(content)
    return {
        "answer": final_answer,
        "context": docs
    }


