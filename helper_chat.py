import streamlit as st
import logging
from openai import OpenAI
from database import load_chat_messages, save_helper_message, load_helper_messages
from rag_handler import get_rag_context

client = OpenAI()
user_avatar_image = 'assets/transparent.png'
assistant_avatar_image = 'assets/transparent.png'

def init_helper_state():
    if "helper_visible" not in st.session_state:
        st.session_state.helper_visible = False
    if "helper_messages" not in st.session_state:
        st.session_state.helper_messages = {}

def display_helper(main_chat_id: int):
    """Renders the helper‐chat UI in the right column."""
    init_helper_state()
    if not main_chat_id:
        st.info("Open or create a main chat first.")
        return

    # load persistent helper history from DB on first render
    if main_chat_id not in st.session_state.helper_messages:
        msgs = load_helper_messages(main_chat_id)
        st.session_state.helper_messages[main_chat_id] = msgs

    helper_msgs = st.session_state.helper_messages[main_chat_id]

    # Display history
    for msg in helper_msgs:
        avatar = user_avatar_image if msg["role"]=="user" else assistant_avatar_image
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

def _handle_helper_input(main_chat_id: int, question: str):
    """Handle sending the helper question through OpenAI."""
    # append user
    user_msg = {"role":"user","content":question}
    st.session_state.helper_messages[main_chat_id].append(user_msg)
    save_helper_message(main_chat_id, "user", question)
    with st.chat_message("user", avatar=user_avatar_image):
        st.text(question)

    # build system prompt
    main_history = load_chat_messages(main_chat_id)
    rag_context = get_rag_context(main_chat_id, question)
    helper_history = st.session_state.helper_messages[main_chat_id]

    system_prompt = (
        "You are an assistant helping the user understand or clarify the MAIN chatbot's conversation.  \n"
        "Below is the most recent MAIN chat history:\n\n"
        f"{_format_messages(main_history)}\n\n"
        "Here are some longer‐term snippets retrieved via RAG:\n\n"
        f"{rag_context}\n\n"
        "And this is the history of THIS helper chat:\n\n"
        f"{_format_messages(helper_history)}\n\n"
        "Answer the user’s question in context."
    )

    messages = [
        {"role":"system","content":system_prompt},
        {"role":"user","content":question}
    ]

    # stream response
    with st.chat_message("assistant", avatar=assistant_avatar_image):
        placeholder = st.empty()
        reply = ""
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                stream=True
            )
            for chunk in response:
                delta = getattr(chunk.choices[0].delta, "content", "")
                if delta:
                    reply += delta
                    placeholder.markdown(reply)
        except Exception as e:
            placeholder.markdown(f"Error: {e}")
            logging.error(e)
            reply = f"Error: {e}"

    # save assistant
    st.session_state.helper_messages[main_chat_id].append({"role":"assistant","content":reply})
    save_helper_message(main_chat_id, "assistant", reply)

def _format_messages(msgs):
    return "\n".join(f"{m['role'].upper()}: {m['content']}" for m in msgs)