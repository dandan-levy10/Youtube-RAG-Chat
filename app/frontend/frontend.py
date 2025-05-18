import streamlit as st
import requests
import json

API_BASE = "http://localhost:8000/api"

@st.cache_resource
def get_api_client():
    """
    Returns a requests.Session() that will:
    - Reuse TCP connections (faster)
    - automatically store & send cookies (session_id)
    - always send JSON in the body"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

api = get_api_client()

def fetch_summary(video_url: str) -> str:
    payload = {"video_url": video_url}
    response = api.post(f"{API_BASE}/summarise", json=payload)
    response.raise_for_status()
    data = response.json()
    # If response returns a session_id in the JSON, stash it in front-end state
    # if "session_id" in data:
    #     st.session_state.session_id = data["session_id"]
    return data["summary"]

def fetch_chat(video_url: str, question: str) -> str:
    payload = {
        "video_url": video_url,
        "question": question
    }
    # if "session_id" in st.session_state:
    #     payload["session_id"] = str(st.session_state.session_id)
    response = api.post(f"{API_BASE}/chat", json=payload)
    response.raise_for_status()
    return response.json()["answer"]

# Build the UI

# Title
st.title(body="Youtube RAG Chat")


# URL input form:
if "video_url" not in st.session_state:
    url = st.text_input("Enter a Youtube video URL and press ↵")
    if st.button("Get Summary") and url:
        # Save the URL in session_state
        st.session_state.video_url = url
        # Call backend for the summary
        st.session_state.summary = fetch_summary(url)
        # Initialise empty chat history
        st.session_state.chat_history = []

else:
    st.subheader("Summary")
    st.write(st.session_state.summary)
    
    st.subheader("Conversation")
    # Render the chat history
    for user_q, bot_a in st.session_state.chat_history:
        st.markdown(f"**You:** {user_q}")
        st.markdown(f"**Bot:** {bot_a}")
    
    # Chat input
    st.subheader(body="Ask a question about the video")
    question = st.text_input("Your question here:", key="user_question")
    if st.button("Send") and st.session_state.user_question.strip():
        answer = fetch_chat(video_url=st.session_state.video_url, question=question)
        st.session_state.chat_history.append((question, answer))
        st.session_state.user_question == ""

    if st.button("New video"):
        for key in ["video_url", "summary", "chat_history", "session_id"]:
            st.session_state.pop(key)

