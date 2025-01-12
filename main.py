import streamlit as st
import openai

from style import set_custom_background
from database import init_db, load_chat_messages
from chat_handler import (
    sidebar_chat_sessions,
    handle_user_input,
    initialize_session_state,
    display_chat_history
)
from file_upload import handle_file_upload
from logger import initialize_logger

# Load environment variables

# Initialize logging
if 'logging_initialized' not in st.session_state:
    st.session_state.logging_initialized = True
    initialize_logger()

# Set custom backgrounds and styles 
set_custom_background('background_art/background_3.jpg')

# Initialize the database
init_db()

# Initialize session state variables
initialize_session_state()

# Sidebar for chat sessions
sidebar_chat_sessions()

# Load messages for the active chat
if st.session_state.active_chat_id:
    st.session_state.messages = load_chat_messages(st.session_state.active_chat_id)
else:
    st.session_state.messages = []

# Invisible element to act as padding 
st.markdown("<div style='height: 300px;'></div>", unsafe_allow_html=True)

# File uploader for PDFs, .py files, and images
uploaded_files = st.file_uploader(
    "Upload files",
    type=["pdf", "py", "png", "jpg", "jpeg"],
    accept_multiple_files=True,
    key=f"file_uploader_{st.session_state.active_chat_id}"  # Unique key per chat_id
)

# Handle file upload
if uploaded_files and st.session_state.active_chat_id:
    handle_file_upload(uploaded_files, st.session_state.active_chat_id)


st.selectbox(
    "Choose a model:",
    options=["o1-preview", "gpt-4-turbo", "o1-mini"],
    key="model",
)

# Invisible element to act as padding 
st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)


# Display chat history
display_chat_history()

# Handle user input 
user_input = st.chat_input("Type your message here...")
if user_input:
    st.session_state.input_box = user_input
    handle_user_input()
