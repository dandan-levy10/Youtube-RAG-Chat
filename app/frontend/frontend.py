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


# Initialise input value keys
if "url_input_value" not in st.session_state:
    st.session_state.url_input_value = ""
if "input_chat_message" not in st.session_state:
    st.session_state.input_chat_message = ""

# Initialise key session state variables
if "video_url" not in st.session_state:
    st.session_state.video_url = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# API-calling functions
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

# ------ Callback functions --------
def handle_get_summary_click():
    input_url = st.session_state.get("url_input_value", "") # Retrieve using key given to text input box
    if input_url:
        st.session_state.video_url = input_url
        summary = fetch_summary(video_url=input_url)
        st.session_state.summary = summary
        st.session_state.chat_history = []
        # Clear input value from state- clear textbox input
        st.session_state.url_input_value = ""
    else:
        st.write("Please enter a video URL")

def handle_send_message_click():
    # Retrieve question widget input from state
    question = st.session_state.get("input_chat_message", "") 
    if question and st.session_state.video_url:
        answer = fetch_chat(
            video_url= st.session_state.video_url,
            question=question
            )
        st.session_state.chat_history.append((question, answer))
        # Clear question widget input
        st.session_state.input_chat_message = "" 
    elif not st.session_state.video_url:
        st.write("Please enter a video URL first")
    else:
        st.write("Please enter a question")

def handle_new_video_click():
    # Initialise input value keys
    st.session_state.url_input_value = ""
    st.session_state.input_chat_message = ""

    # Initialise key session state variables
    st.session_state.video_url = None
    st.session_state.summary = None
    st.session_state.chat_history = []

# -------- Build the UI ----------

# Title
st.title(body="Youtube RAG Chat")


# URL input form:
if not st.session_state.video_url:
    url = st.text_input(
        "Enter a Youtube video URL and press ↵", 
        key="url_input_value" # This links the widget to st.session_state.url_input_value
        )
    st.button("Get Summary", on_click=handle_get_summary_click)

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
    question = st.text_input("Your question here:", key="input_chat_message")
    st.button("Send", on_click=handle_send_message_click) 
    
    st.button("New video", on_click=handle_new_video_click)

