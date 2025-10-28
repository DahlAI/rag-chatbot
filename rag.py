import streamlit as st
import requests
import uuid

# Page config
st.set_page_config(page_title="Knowledge Base RAG Chatbot", page_icon="🤖", layout="wide")

# Title
st.title("🤖 Knowledge Base RAG Chatbot")
st.markdown("Ask questions about real estate marketing, SMS strategies, cold calling, and more!")

# Webhook URL - CHANGE THIS TO YOUR PRODUCTION URL
WEBHOOK_URL = "https://greteldahl.app.n8n.cloud/webhook/rag-query"

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your knowledge base..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            try:
                # Call n8n webhook
                response = requests.post(
                    WEBHOOK_URL,
                    json={
                        "message": prompt,
                        "session_id": st.session_state.session_id
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    answer = response.text
                    
                    # Format citations nicely
                    # Replace [Source: ...] with styled citations
                    import re
                    
                    # Find all citations in format [Source: Article Title]
                    citations = re.findall(r'\[Source: ([^\]]+)\]', answer)
                    
                    # Display the main answer (remove inline citations)
                    main_answer = re.sub(r'\[Source: ([^\]]+)\]', '', answer)
                    st.markdown(main_answer)
                    
                    # Display citations separately if they exist
                    if citations:
                        st.markdown("---")
                        st.markdown("**📚 Sources:**")
                        for i, citation in enumerate(set(citations), 1):  # use set to remove duplicates
                            st.markdown(f"{i}. *{citation}*")
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Error: Received status code {response.status_code}")
                    st.text(response.text)
                    
            except requests.exceptions.Timeout:
                st.error("Request timed out. The query is taking too long.")
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to the chatbot: {str(e)}")

# Sidebar with info
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This chatbot uses **RAG (Retrieval-Augmented Generation)** to answer questions about your knowledge base.
    
    **How it works:**
    1. Your question is converted to a vector embedding
    2. Similar articles are retrieved from the knowledge base
    3. AI generates an answer based on the retrieved content
    
    **Topics covered:**
    - Real estate marketing strategies
    - SMS messaging best practices
    - Cold calling techniques
    - Direct mail campaigns
    - Skip tracing
    - Lead generation
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# Footer
st.markdown("---")
st.markdown("*Powered by n8n, Pinecone, and OpenAI*")
