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
set_custom_css(
    background_image_path='background_art/background_3.jpg',
    gif_path='background_art/sparkle_one.gif',
    gif_count=5,
    gif_blur='2px'
)

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

if st.session_state.helper_visible:
    helper_panel = st.container()
    with helper_panel:
        helper_chat.display_helper(st.session_state.active_chat_id)

        helper_input_box = st.container()
        with helper_input_box:
            helper_user_input = st.chat_input(
                "Ask about the chat",
                key=f"helper_input_{st.session_state.active_chat_id}"
            )

        if helper_user_input:
            helper_chat._handle_helper_input(
                st.session_state.active_chat_id,
                helper_user_input
            )

    helper_pos = float_css_helper(
        top="12vh",
        bottom="12vh",
        width="315px",
        border_radius="0.5rem",
        z_index="9998",
        right="0px"
    )
    helper_panel.float(helper_pos)

    helper_input_pos = float_css_helper(
        top="auto",
        bottom="125px",
        height="auto",
        width="314px",
        border_radius="0px",
        z_index="9999",
    )
    helper_input_box.float(helper_input_pos)


################################################################################## MAIN CHAT FLOATED PANEL ###########################################################################################

main_chat = st.container()

with main_chat:
    st.markdown("<div style='height:3rem;'></div>", unsafe_allow_html=True)

    display_chat_history()

    main_input_container = st.container()

    # Float immediately 
    main_input_pos = float_css_helper(
        top="auto",
        bottom="90px",
        height="auto",
        width="700px",
        border_radius="0.5rem",
        background_color="rgba(37,38,50, 1.0)",
        padding="0.5rem",
        z_index="9999",
    )
    main_input_container.float(main_input_pos)

    with main_input_container:
        # Chat input
        main_user_input = st.chat_input(
            "Ask anything",
            key=f"main_input_{st.session_state.active_chat_id}"
        )

        # Below that: a tiny two-column row
        col_u, col_m = st.columns([0.12, 0.88], gap="small")
        with col_u:
            st.markdown('<div class="file-upload-button">+</div>', unsafe_allow_html=True)

        with col_m:
            st.selectbox(
                label="placeholder",  # hide default Streamlit label
                options=["gpt-4o", "gpt-4.5-preview", "o4-mini", "o4-mini-high"],
                key="model",
                label_visibility="collapsed"
            )


    if main_user_input:
        st.session_state.input_box = main_user_input
        handle_user_input()

main_chat_pos = float_css_helper(
    top="8vh",
    bottom="8vh",
    width="725px",
    border_radius="0.5rem",
    z_index="9997",
    left="50%",
    margin_left="-340px",
)
main_chat.float(main_chat_pos)

hidden_uploader = st.container()

with hidden_uploader:
    uploaded = st.file_uploader(
        label="placeholder",                             # no label
        type=["pdf", "py", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key=f"offscreen_uploader_{st.session_state.active_chat_id}",
        label_visibility="collapsed"
    )
    if uploaded and st.session_state.active_chat_id:
        handle_file_upload(uploaded, st.session_state.active_chat_id)

# Float it completely off‐screen:
hidden_pos = float_css_helper(
    top="500px",               # can be anywhere
    left="-1000px",           # far off to the left
    width="1px",              # effectively zero footprint
    height="1px",
    z_index="-1",             # behind everything
)
hidden_uploader.float(hidden_pos)

