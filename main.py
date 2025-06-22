import streamlit as st
import helper_chat

from style import set_custom_css
from javascript import set_custom_js
from database import init_db, load_chat_messages
from chat_handler import (
    sidebar_chat_sessions,
    handle_user_input,
    initialize_session_state,
    display_chat_history
)
from file_upload import handle_file_upload
from logger import initialize_logger

from streamlit_float import float_init, float_css_helper


################################################################################## ON LOAD SETUPS ###########################################################################################


float_init()

if 'logging_initialized' not in st.session_state:
    initialize_logger()
    st.session_state.logging_initialized = True

if 'helper_visible' not in st.session_state:
    st.session_state.helper_visible = False

# CSS and JS to load 
set_custom_css('background_art/background_3.jpg')
set_custom_js()

# Initialize databases
init_db()
initialize_session_state()
helper_chat.init_helper_state()


################################################################################## MAIN PAGE LAYOUT ###########################################################################################


# Sidebar chat selections
sidebar_chat_sessions()
if st.session_state.active_chat_id:
    st.session_state.messages = load_chat_messages(
        st.session_state.active_chat_id
    )
else:
    st.session_state.messages = []

# CSS behavior for main chat
if st.session_state.helper_visible:
    st.markdown(
        """
        <style>
          .block-container {
            max-width: 640px;
            margin-right: 165px !important;
          }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
          .block-container {
            max-width: 640px;
            margin: auto;
          }
        </style>
        """,
        unsafe_allow_html=True
    )

# Main chat layout
st.markdown("<div style='height:300px;'></div>", unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Upload files",
    type=["pdf", "py", "png", "jpg", "jpeg"],
    accept_multiple_files=True,
    key=f"file_uploader_{st.session_state.active_chat_id}"
)
if uploaded and st.session_state.active_chat_id:
    handle_file_upload(uploaded, st.session_state.active_chat_id)

st.selectbox(
    "Choose a model:",
    options=["gpt-4o","gpt-4.5-preview","o4-mini","o4-mini-high"],
    key="model",
)

st.markdown("<div style='height:200px;'></div>", unsafe_allow_html=True)


################################################################################## HELPER CHAT LAYOUT ###########################################################################################

# Toggle button
def _toggle_helper():
    st.session_state.helper_visible = not st.session_state.helper_visible

toggle = st.container()
with toggle:
    label = "◂" if not st.session_state.helper_visible else "▸"
    st.button(
        label,
        key="toggle_helper",
        on_click=_toggle_helper,
    )

toggle_pos = float_css_helper(
    top="40vh",
    height="8rem",
    width="2rem",
    border_radius="0.5rem",
    z_index="1",
    **(
        {"right": "314px"}
        if st.session_state.helper_visible
        else {"right": "-7px"}
    )
)
toggle.float(toggle_pos)

# Helper chat panel 
if st.session_state.helper_visible:
    helper_panel = st.container()

    with helper_panel:
        # Show the history
        helper_chat.display_helper(st.session_state.active_chat_id)

        # Wrap the helper input in its own container
        helper_input_box = st.container()
        with helper_input_box:
            helper_user_input = st.chat_input(
                "Ask about the chat",
                key=f"helper_input_{st.session_state.active_chat_id}")

        if helper_user_input:
            # Call the handler in helper_chat.py
            helper_chat._handle_helper_input(
                st.session_state.active_chat_id,
                helper_user_input
            )

    # Float the helper panel itself
    helper_pos = float_css_helper(
        top="12vh",
        bottom="12vh",
        width="315px",
        border_radius="0.5rem",
        z_index="9998",
        right="0px"
    )
    helper_panel.float(helper_pos)

    # Float the helper chat’s input box
    helper_input_pos = float_css_helper(
        # pin to bottom of helper panel
        top="auto",
        bottom="125px",
        height="auto",
        width="314px",       # Offset by one so styling doesnt target it
        border_radius="0px",
        z_index="9999",
    )
    helper_input_box.float(helper_input_pos)


###############################################################################################################################################################################


display_chat_history()

main_input_container = st.container()

with main_input_container:
    main_user_input = st.chat_input(
        "Ask anything",
        key=f"main_input_{st.session_state.active_chat_id}")

# Compute its float position exactly like for toggle
main_input_pos = float_css_helper(
    top="auto",                # Leave vertical flow alone (it’ll stick to bottom)
    bottom="45px",             # Pin to bottom of viewport
    height="auto",             # Natural height
    width="675px",              # Full width 
    border_radius="0px",
    z_index="9999",            
                               # Shifts handled in JS
)

# Float it
main_input_container.float(main_input_pos)

# Check for user inputs
if main_user_input:
    st.session_state.input_box = main_user_input
    handle_user_input()

