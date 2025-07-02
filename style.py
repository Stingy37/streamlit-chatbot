import streamlit as st
import base64

def set_custom_css(
        background_image_path, 
        gif_path=None,
        gif_count=1,
        gif_blur="10px"
        ):
    @st.cache_data
    def get_base64_image(image_file):
        with open(image_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()

    img64 = get_base64_image(background_image_path)
    gif64 = get_base64_image(gif_path) if gif_path else None

    custom_css = f"""
    <style>

      body {{
        background: url("data:image/jpg;base64,{img64}") no-repeat center center fixed;
        background-size: 115%;
      }}

      {f'''
      body::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: url("data:image/gif;base64,{gif64}") repeat;
        background-size: calc(100% / {gif_count}) auto;
        filter: blur({gif_blur});
        transform: scaleY(1);
        pointer-events: none;
        z-index: -1;
      }}
      ''' if gif64 else ''}

      .stApp {{
        background-color: transparent !important;
      }}

      /* Transparent bottom input area */
      .stBottom > div {{
        position: absolute;
        background-color: transparent;
      }}

      /* Toggle button */
      .stElementContainer.st-key-toggle_helper .stButton button {{
        height: 10em;
        width: 2rem;
        background-color: rgba(14,17,23,0.6);
        backdrop-filter: blur(10px);
      }}


      html {{
        font-size: 100%;
      }}


      /* Floated MAIN chat panel — same as helper but wider */
      div[id^="float-this-component"][style*="width: 800px"] {{
        position: fixed;
        z-index: 1;
        background-color: rgba(14,17,23,0.5);
        padding: 1rem;
        /* only vertical scroll, no horizontal */
        overflow-y: auto;
        overflow-x: hidden;
        box-shadow: 0 0 40px 20px rgba(14,17,23,0.6);
        border-radius: 0.5rem;
        padding-bottom: 150px;

        scrollbar-width: none;
        -ms-overflow-style: none;
      }}

      /* Subtle inner-shadow fade at edges */
      div[id^="float-this-component"][style*="width: 800px"]::after {{
        content: "";
        position: fixed;           /* stays fixed in viewport */
        pointer-events: none;
        z-index: -1;
        background:
            linear-gradient(
            to right,
            transparent 0%,
            rgba(0,0,0,0.15) 10%,
            rgba(0,0,0,0.15) 90%,
            transparent 100%
            ),
            linear-gradient(
            to left,
            transparent 0%,
            rgba(0,0,0,0.15) 10%,
            rgba(0,0,0,0.15) 90%,
            transparent 100%
            );
        filter: blur(4px);

        top: 8vh;
        left: 23.5%;
        width: 800px;
        height: calc(100vh - 16vh);
        clip-path: inset(0 round 0.5rem);
      }}

      div[id^="float-this-component"][style*="width: 800px"]::before {{
        content: "";
        position: fixed;          
        pointer-events: none;
        z-index: -2;

        top: 8vh;
        left: 23.5%;
        width: 800px;
        height: calc(100vh - 16vh);
        clip-path: inset(0 round 0.5rem);

        backdrop-filter: blur(30px);
      }}

      /* Helper-panel styling: unchanged except no horizontal scroll */
      div[id^="float-this-component"][style*="width: 315px"] {{
        position: relative;
        z-index: 1;
        background-color: rgba(14,17,23,0.5);
        padding: 1rem;
        overflow-y: auto;
        overflow-x: hidden;
        box-shadow: 0 0 40px 20px rgba(14,17,23,0.6);
        border-radius: 0.5rem;
        padding-bottom: 100px;

        scrollbar-width: none;
        -ms-overflow-style: none;
      }}

      div[id^="float-this-component"][style*="width: 315px"]::after {{
        content: "";
        position: fixed;
        pointer-events: none;
        z-index: -1;
        background:
            linear-gradient(
            to right,
            transparent 0%,
            rgba(0,0,0,0.15) 10%,
            rgba(0,0,0,0.15) 90%,
            transparent 100%
            ),
            linear-gradient(
            to left,
            transparent 0%,
            rgba(0,0,0,0.15) 10%,
            rgba(0,0,0,0.15) 90%,
            transparent 100%
            );
        filter: blur(4px);

        top: 8vh;
        right: 0px;
        width: 315px;
        height: calc(100vh - 16vh);
        clip-path: inset(0 round 0.5rem);
      }}

      div[id^="float-this-component"][style*="width: 315px"]::before {{
        content: "";
        position: fixed;
        pointer-events: none;
        z-index: -2;

        top: 8vh;
        right: 0px;
        width: 315px;
        height: calc(100vh - 16vh);
        clip-path: inset(0 round 0.5rem);

        backdrop-filter: blur(30px);
      }}

      /* Clean up the wrapper div (class auto-assigned to st.chat_input) */
      div[id^="float-this-component"][style*="width: 770px"] .stChatInput {{
        background-color: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        box-shadow: none !important;
      }}

      /* Target the entire chat input so that the submit button's position can be controlled as well */
      div[id^="float-this-component"][style*="width: 770px"]
        .stElementContainer > div > div {{
        display: flex !important;
        max-width: 755px !important;   /* ← overall widget width, which is parent width (770) - 15 */
        width: 100% !important;         /* fill its 770px parent */
        gap: 0.25rem !important;        /* space between textarea & button */
      }}


      /* Clear out the internal text input container (usually a child of stChatInput) */
      div[id^="float-this-component"][style*="width: 770px"] .stChatInput > div {{
        background-color: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        box-shadow: none !important;
      }}

        /* Make the chat_input inside our 770px chat input container full-width & transparent */
      div[id^="float-this-component"][style*="width: 770px"] .stChatInput textarea {{
        width: 98% !important;
        background-color: transparent !important;
        border: none !important;
        margin: 0 !important;
      }}

      /* Kill all borders attached to .stChatInput */
      div[id^="float-this-component"][style*="width: 770px"] .stChatInput * {{
        border: none !important;
        border-width: 0px !important;
        border-style: none !important;
        border-color: transparent !important;
        outline: none !important;
        box-shadow: none !important;
      }}

      /* Minimalist file upload "+" button */
      .file-upload-button {{
        position: relative;
        width: 2rem;
        height: 2rem;
        font-size: 1.5rem;
        font-weight: bold;
        color: white;
        border-radius: 0.25rem;
        text-align: center;
        line-height: 2rem !important;
        cursor: pointer;
        z-index: 1;
      }}

      .file-upload-button:hover {{
        background-color: rgba(255,255,255,0.2);
      }}

      div[id^="float-this-component"][style*="width: 770px"] div[data-testid="stSelectbox"] {{
        width: 130px !important;
        max-width: 100% !important;
      }}

      div[id^="float-this-component"][style*="width: 770px"] div[data-testid="stSelectbox"]:hover > div {{
        background-color: rgba(255, 255, 255, 0.2) !important;
        border-radius: 0.25rem;
        cursor: pointer;
      }}

      /* Hide the ▼ arrow icon inside the selectbox */
      div[id^="float-this-component"][style*="width: 770px"] div[data-testid="stSelectbox"] svg {{
        display: none !important;
      }}

      /* Full nuke of streamlit selectbox button container (visual box) */
      div[id^="float-this-component"][style*="width: 770px"] div[data-testid="stSelectbox"] div {{
        background-color: transparent !important;
        border: none !important;
        border-width: 0 !important;
      }}

      /* Kill the float-container’s top/bottom padding, and add a box shadow */
      div[id^="float-this-component"][style*="width: 770px"] {{
        box-shadow: 0 10px 40px 10px rgba(14,17,23,0.9) !important;
        padding-bottom: 5px !important;
      }}

      div[id^="float-this-component"][style*="width: 770px"]div[data-testid="stColumns"] > div:first-child {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;  /* Optional: centers it horizontally too */
      }}

      /* Get rid of extra gaps for the chat input */
      div[id^="float-this-component"][style*="width: 770px"] {{
        gap: 0 !important;
      }}

            /* Make every chat-message a flex container */
      div[id^="float-this-component"][style*="width: 800px"]
        div[data-testid="stChatMessage"] {{
        display: flex !important;
        align-items: flex-start;
      }}

      /* Detect “user” messages by checking for the user’s avatar ALT text, then reverse the ordering of avatar ↔ text */
      div[id^="float-this-component"][style*="width: 800px"] div[data-testid="stChatMessage"]:has(img[alt="user avatar"]) {{
          flex-direction: row-reverse !important;

      }}

      /* Move user text messages to the right side of the main chat, but still keep left alignment */
      div[id^="float-this-component"][style*="width: 800px"]
        div[data-testid="stChatMessage"]:has(img[alt="user avatar"])
        [data-testid="stText"] {{
        text-align: left !important;
        justify-content: flex-end !important;
      }}


      /* Style initial greeting message */
      #greeting {{
        display: flex;
        align-items: center;
        justify-content: center;
        height: 200px;
        color: rgba(255,255,255,0.7);
        font-size: 1.7rem;
      }}



    </style>
    """

    st.markdown(custom_css, unsafe_allow_html=True)

    hide_streamlit_style = """
    <style>
      header { visibility: hidden; }
      #MainMenu { visibility: hidden; }
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
