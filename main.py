import streamlit as st
import random
import helper_chat
import streamlit.components.v1 as components
import time

from live2D import live_2d_html, set_live_2d_emotion
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

if "customize_mode" not in st.session_state:
    st.session_state.customize_mode = False

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

# Initialize the active chat 
if st.session_state.active_chat_id:
    st.session_state.messages = load_chat_messages(
        st.session_state.active_chat_id
    )
else:
    st.session_state.messages = []


############################################################################## INITIAL SIDEBAR LAYOUT ###########################################################################################


with st.sidebar:
    # Non-customization mode sidebar
    if not st.session_state.customize_mode:
        sidebar_chat_sessions() # Add all the chat session sidebar items

        st.divider()
        st.title("Settings")
         
        if st.button("Customize Style"):
            st.session_state.customize_mode = True
            st.rerun()


############################################################################# CUSTOMIZATION SIDEBAR LAYOUT ###########################################################################################


    # Customization mode sidebar (upon first opening, all of these values should be from style already present—except for those that rely on file uploads, like gif and background image)
    if st.session_state.customize_mode: 
        if st.button("Back"):
            st.session_state.customize_mode = False
            st.rerun()
        

        #############################################################################

        st.divider()
        st.title("Manage Styles")
        
        current_style_name = st.sidebar.text_input("Current Style Name:")
        if st.sidebar.button("Save Style"):
            # Stip the input in current_style_name and use a module function to handle saving the input (and the current CSS) to a database, 
            # linking CSS with a name to create the effect of "saving" a style. Ideally, this grabs EACH parameterized CSS value and saves it. 
            pass

        styles = ["style_one", "style_two"] # Placeholder to visualize UI, in practice we would load from aforementioned database 
        if styles:
            selected_style_index = st.sidebar.selectbox(
                "Select a saved style:",
                range(len(styles)),
                format_func=lambda idx: styles[idx],
            )
            # Then, use a handler function where the handler function injects the associated CSS with what the user chooses   
        else:
            st.sidebar.info("No styles. Create a new one below.")

        #############################################################################


        st.divider()
        st.title("Background")

        background_image = st.file_uploader(
            label="Background image",                     
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=False,
            key=f"background_image_uploader",
            label_visibility="visible"
        )
        if background_image:
            # 1st, some handler function that immediately changes the CSS to reflect the uploaded image

            # 2nd, add ability to adjust position, blur, and scaling (and these should apply to the CSS as they are being adjusted, ideally)
            image_x_pos       = st.slider("X Position",   min_value=0,   max_value=100,   value=50,   help="Horizontal offset (%)",  key="image_x_pos")
            image_y_pos       = st.slider("Y Position",   min_value=0,   max_value=100,   value=50,   help="Vertical offset (%)",    key="image_y_pos")
            image_scaling     = st.slider("Scaling",      min_value=0.1, max_value=3.0,   value=1.0, step=0.1, help="Scale factor",  key="image_scaling")
            image_blur        = st.slider("Blur strength",min_value=0,   max_value=50,    value=0,             help="Blur Strength", key="image_blur")
        
        gif = st.file_uploader(
            label="Optional animated effects",                     
            type=["gif"],
            accept_multiple_files=False,
            key=f"gif_uploader",
            label_visibility="visible"
        )
        if gif:
            # 1st, some handler function that immediately changes the CSS to reflect the uploaded gif

            gif_flip       = st.checkbox("Flip vertically", value=False,  help="Flip the gif vertically",                      key="gif_flip")
            smooth_looping = st.checkbox("Smooth looping",  value=True,   help="Enable fade in / fade out for seamless loops", key="smooth_looping")
            gif_count      = st.slider("Size",          min_value=1, max_value=3,  value=1, step = 1, help="How many copies of the GIF to fill the screen width", key="gif_count" )
            gif_blur       = st.slider("Blur strength", min_value=0, max_value=50, value=0,           help="How strong the blur is",                              key="gif_blur")


        #############################################################################

        st.divider()
        st.title("Chat Panels")

        chat_primary_background_color = st.color_picker(
            label="Chat primary background color",
            value="#ffffff",              # default color should be whatever the current style is
            help="Primary background color for chat panels",
            key="chat_primary_background_color"
        )
        chat_secondary_background_color = st.color_picker(
            label="Chat secondary background color",
            value="#ffffff",              # default color should be whatever the current style is
            help="Secondary background color for chat panels",
            key="chat_secondary_background_color"
        )
        chat_blur           = st.slider("Blur strength", min_value=0,   max_value=50,    value=0,    help="How strong the blur is",   key="chat_blur") 
        chat_glow_strength  = st.slider("Glow strength", min_value=0,   max_value=50,    value=0,    help="How strong the glow is",   key="chat_glow_strength") 
        chat_glow_radius    = st.slider("Glow size",     min_value=0,   max_value=50,    value=0,    help="How far the glow extends", key="chat_glow_radius") 
        chat_glow_color = st.color_picker(
            label="Chat glow color",
            value="#ffffff",              # default color should be whatever the current style is
            help="Color for the glow effect behind chat panels",
            key="chat_glow_color"
        )

        #############################################################################

        st.divider()
        st.title("Chat Input")
        
        chat_input_color = st.color_picker(
            label="Chat input color",
            value="#ffffff",              # default color should be whatever the current style is
            help="Primary color for chat input area",
            key="chat_input_color"
        )
        chat_input_glow_color = st.color_picker(
            label="Chat input glow color",
            value="#ffffff",              # default color should be whatever the current style is
            help="Color for the glow effect behind chat input area",
            key="chat_input_glow_color"
        )
        chat_input_glow_strength  = st.slider("Glow strength", min_value=0,   max_value=50,    value=0,    help="How strong the glow is",   key="chat_input_glow_strength") 
        chat__input_glow_radius    = st.slider("Glow size",     min_value=0,   max_value=50,    value=0,    help="How far the glow extends", key="chat__input_glow_radius") 

        #############################################################################

        st.divider()
        st.title("Live2D Model")

        models = ["model_one", "model_two"] # Placeholder to visualize UI, in practice we would load from a predefined list. 
                                            # Each model in the list will have a corresponding live_2d_html, which we then load accordingly. 
                                            # Also, emotion_choices and emotion_meaning will be different per model. 
        if models:
            selected_model_index = st.sidebar.selectbox(
                "Select a model:",
                range(len(models)),
                format_func=lambda idx: models[idx],
            )
            model_scaling     = st.slider("Model scaling",      min_value=0.01, max_value=.30,   value=.18, step=0.01, help="Scale factor",  key="model_scaling")

        #############################################################################

        st.divider()
        st.title("Global Settings")

        fonts = ["font_one", "font_two"] # Placeholders, replace this with popular / stylish looking fonts that can be passed as a CSS parameter
        if fonts:
            selected_font_index = st.sidebar.selectbox(
                "Select a font:",
                range(len(fonts)),
                format_func=lambda idx: fonts[idx],
            )
        # Either way, have the ability to choose a font size (if no font selected, then we can STILL apply this as a CSS parameter)
        font_scale  = st.slider("Font scale", min_value=.5,   max_value=1.5,    value=.1,    help="How large the font is",   key="font_scale") 
        
################################################################################### LIVE 2D FLOATED PANEL ###########################################################################################

post_slot = st.empty()
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

@st.fragment
def main_fragment():
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
            set_live_2d_emotion(st.session_state.messages, post_slot)


    main_chat_pos = float_css_helper(
        top="8vh",
        bottom="8vh",
        width="800px",
        border_radius="0.5rem",
        z_index="9997",
        left="23.5%",
    )
    main_chat.float(main_chat_pos)

main_fragment()

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


