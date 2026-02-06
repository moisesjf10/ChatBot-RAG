import streamlit as st
import backend
import time
from config import Config

#Page configuration
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

#Validate API Key
try:
    Config.validate()
except ValueError as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

# --- CACHING RESOURCES ---
@st.cache_resource
def load_vector_store():
    return backend.get_vector_store()

@st.cache_resource
def load_llm():
    return backend.get_llm()

# Pre-load resources
vector_store = load_vector_store()

#SIDEBAR (Data ingestion)
with st.sidebar:
    st.title("Knowlegde base")
    st.markdown("Upload your documents here to train the bot")

    uploaded_files=st.file_uploader(
        "Upload .txt or .md files",
        type=["txt", "md"],
        accept_multiple_files=True
    )

    #Train button
    if st.button("Train/Update"):
        if uploaded_files:
            with st.spinner("Preprocessing documents..."):
                try:
                    # Ingest files (not cached as it changes state)
                    num_chunks = backend.ingest_files(uploaded_files=uploaded_files)
                    st.success(f"Training Complete! Indexed {num_chunks} chunks.")
                    
                    # Force reload of vector store cache if needed, 
                    # though usually Chroma handles updates internally.
                    # st.cache_resource.clear() 
                except Exception as e:
                    st.error(f"Error during training: {e}")
        else:
            st.warning("Please upload at least one file.")
    
    st.markdown("---")
    
    # Clear Chat Button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("Powered by Gemini 3 Flash & LangChain")

#Main chat interface
st.title("Chat with your Docs")

#Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages=[]

#Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#User input handling
if prompt:=st.chat_input("Ask something about your documents..."):
    #Display User Message
    st.session_state.messages.append({"role":"user", "content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    #Generate assistant response
    with st.chat_message("assistant"):
        try:
            # STREAMING RESPONSE
            stream_generator = backend.stream_rag_response(
                user_query=prompt, 
                chat_history=st.session_state.messages
            )
            
            response_text = st.write_stream(stream_generator)
            
            # Add to history
            st.session_state.messages.append({"role": "assistant", "content": response_text})

            # Retrieve sources separately for display
            # We do this after streaming to not block the first byte
            # Ideally backend.stream_rag_response would allow accessing docs, 
            # but generators are one-way. 
            # We call the helper query function synchronously.
            with st.spinner("Checking sources..."):
                source_docs = backend.get_docs_for_query(prompt)
            
            if source_docs:
                with st.expander("View Source Documents"):
                    for i, doc in enumerate(source_docs):
                        source_name = doc.metadata.get("source", "Unknown")
                        preview_text = doc.page_content[:300].replace("\n", " ")
                        
                        st.markdown(f"**Source {i+1} ({source_name}):**")
                        st.caption(f"...{preview_text}...")
                        st.divider()
                        
        except Exception as e:
            st.error(f"Error generating response: {e}")
