import streamlit as st
import backend
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
                    num_chunks=backend.ingest_files(uploaded_files=uploaded_files)
                    st.success(f"Training Complete! Indexed {num_chunks} chunks.")
                except Exception as e:
                    st.error(f"Error during training: {e}")
        else:
            st.warning("Please upload at least one file.")
    
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
        with st.spinner("Thinking..."):
            try:
                response_payload=backend.get_rag_response(
                    user_query=prompt, chat_history=st.session_state.messages)

                #extract data from backend response
                answer_text=response_payload["answer"]
                source_docs=response_payload["context"]

                #display de answer
                st.markdown(answer_text)

                #update history
                st.session_state.messages.append({"role": "assistant", "content":answer_text})

                if source_docs:
                    with st.expander("View Source Documents"):
                        for i, doc in enumerate(source_docs):
                            source_name = doc.metadata.get("source", "Unknown")
                            # Preview first 300 chars to avoid clutter
                            preview_text = doc.page_content[:300].replace("\n", " ")
                            
                            st.markdown(f"**Source {i+1} ({source_name}):**")
                            st.caption(f"...{preview_text}...")
                            st.divider()
                            
            except Exception as e:
                st.error(f"Error generating response: {e}")
