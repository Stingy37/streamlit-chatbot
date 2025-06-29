import streamlit as st
import random
import helper_chat
import streamlit.components.v1 as components

from live2D import live_2d_html
from style import set_custom_css
from javascript import set_dragging_resizing_js, set_styling_js
from database import init_db, load_chat_messages, get_all_chats, create_chat
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

# Collapse the sidebar initially
st.set_page_config(
    initial_sidebar_state="collapsed"
)

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
set_dragging_resizing_js()
set_styling_js()

# Initialize databases 
init_db()

# First-visit: spin up a default chat
all_chat_ids = get_all_chats()
if not all_chat_ids:
    default_id = create_chat("New Chat")
    st.session_state.active_chat_id = default_id

# Initialize session states
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


################################################################################### LIVE 2D FLOATED PANEL ###########################################################################################

live2d_slot = st.empty()
live2d_container = live2d_slot.container(key="live2d_avatar_container")

# Embed the Live2D iframe
with live2d_container:
    components.html(
        live_2d_html,
        width=400,    # Pixel width of the embedded html 
        height=700,   # Pixel height of the embedded html 
    )

# Float it on screen
live2d_pos = float_css_helper(
    top="3vh",
    bottom="3vh",
    left="-100px",
    width="400px",
    z_index="4",
)
live2d_container.float(live2d_pos)


################################################################################## HELPER CHAT LAYOUT ###########################################################################################

 # Wrap the helper-chat UI into a fragment so it reruns independently (do NOT write into fragment containers from outside—keep things independent)
@st.fragment
def helper_fragment(active_chat_id: int):
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
        width="2rem",
        border_radius="0.5rem",
        z_index="10",
        **(
            {"right": "314px"}
            if st.session_state.helper_visible
            else {"right": "-7px"}
        )
    )
    toggle.float(toggle_pos)

    if st.session_state.helper_visible:
        helper_panel_slot = st.empty()
        helper_panel = helper_panel_slot.container()

        with helper_panel:
            helper_chat.display_helper(st.session_state.active_chat_id)

            helper_input_box = st.container()

            # Immediately float the helper 
            helper_input_pos = float_css_helper(
                top="auto",
                bottom="125px",
                height="auto",
                width="314px",
                border_radius="0px",
                z_index="9999",
            )
            helper_input_box.float(helper_input_pos)

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
            top="8vh",
            bottom="8vh",
            width="315px",
            border_radius="0.5rem",
            z_index="9998",
            right="0px"
        )
        helper_panel.float(helper_pos)

# Call the fragment
helper_fragment(st.session_state.active_chat_id)


################################################################################## MAIN CHAT FLOATED PANEL ###########################################################################################


main_chat_slot = st.empty() # We must wrap in st.empty to avoid rerun styling "flashes"
main_chat = main_chat_slot.container(key="main_chat_panel")

with main_chat:
    # Avoid rerun styling flash
    _input_slot = st.empty()

    st.markdown("<div style='height:3rem;'></div>", unsafe_allow_html=True)

    # Add a initial randomized greeting message 
    if not st.session_state.messages:
        greetings = [
            "What's on the agenda today?",
            "Hello there! Ready to chat?",
            "How can I help you?",
            "Got questions? I'm all ears.",
            "Hey! What's up?"
        ]
        greeting = random.choice(greetings)

        greeting_slot = st.empty()
        with greeting_slot:
            st.markdown(
                f'<div id="greeting">{greeting}</div>', # Use the ID here to target it in CSS
                unsafe_allow_html=True
            )


    display_chat_history()

    # Create the container object via the empty slot
    main_input_container = _input_slot.container()

    # Float it immediately
    main_input_pos = float_css_helper(
        top="auto",
        bottom="90px",
        height="auto",
        width="770px",
        border_radius="0.5rem",
        background_color="rgba(37,38,50, 1.0)",
        padding="0.5rem",
        z_index="9999",
    )
    main_input_container.float(main_input_pos)

    # Render actual chat input inside 
    with main_input_container:
        main_user_input = st.chat_input(
            "Ask anything",
            key=f"main_input_{st.session_state.active_chat_id}"
        )

        col_u, col_m = st.columns([0.12, 0.88], gap="small")
        with col_u:
            st.markdown('<div class="file-upload-button">+</div>', unsafe_allow_html=True)
        with col_m:
            st.selectbox(
                label="placeholder",
                options=["gpt-4o", "gpt-4.5-preview", "o4-mini", "o4-mini-high"],
                key="model",
                label_visibility="collapsed"
            )

    # Handle input submission 
    if main_user_input:
        # First, check to see if greeting div exists, if so, remove it 
        if "greeting_slot" in locals():
            greeting_slot.empty()

        st.session_state.input_box = main_user_input
        handle_user_input()

main_chat_pos = float_css_helper(
    top="8vh",
    bottom="8vh",
    width="800px",
    border_radius="0.5rem",
    z_index="9997",
    left="23.5%",
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

