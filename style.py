import streamlit as st
import base64

def set_custom_css(background_image_path):
    # Helper to load & encode image
    @st.cache_data
    def get_base64_image(image_file):
        with open(image_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()

    img_base64 = get_base64_image(background_image_path)

    custom_css = f"""
    <style>
      /* 1) Full‑app background */
      .stApp {{
        background: url("data:image/jpg;base64,{img_base64}") 
                    no-repeat center center fixed;
        background-size: 115%;
        background-position: 0px center;
      }}

      /* 2) Main content container: darker tint + scrolling */
      .block-container {{
        position: relative;
        z-index: 0;                 /* <-- establish stacking context */
        background-color: rgba(14,17,23,0.6);
        padding-top: 2rem;
        padding-bottom: 150px;
        overflow: clip;
        box-shadow: 0 0 110px 50px rgba(14,17,23,0.40);             /* outer shadow */
      }}

      .block-container::after {{
        content: "";
        position: absolute;
        inset: 0;
        pointer-events: none;
        z-index: -1;

        /* Stronger, tighter rectangular fade */
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

        /* optional: soften with a tiny blur */
        filter: blur(4px);
        
      }}
        
      /* 3) Frosted‑glass: 30px blur behind the container */
      .block-container::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        pointer-events: none;
        backdrop-filter: blur(30px);
        z-index: -2;                /* <-- push behind everything in .block-container */
      }}

      /* 5) Transparent bottom input area */
      .stBottom > div {{
        position: absolute;
        background-color: transparent;
      }}

      /* 6) Disable auto‑scroll anchoring in chat */
      [data-testid="stChatMessages"] {{
        overflow-anchor: none;
      }}

      /* 7) Style only the helper chat button */
     .element-container:nth-of-type(1) .stButton:nth-of-type(1) button {{
        height: 10em;
        background-color: rgba(14,17,23,0.6);
        backdrop-filter: blur(10px);
      }}

      html {{
        font-size: 90%;
      }}

      
    /* helper-panel styling: same as .block-container, applied to the float wrapper */
    div[id^="float-this-component"][style*="width: 350px"] {{
    position: relative;
    z-index: 1;
    background-color: rgba(14,17,23,0.5);
    padding: 1rem;
    overflow: auto;
    box-shadow: 0 0 70px 40px rgba(14,17,23,0.35);
    border-radius: 0.5rem;
    padding-bottom: 100px;

    scrollbar-width: none;          /* Firefox */
    -ms-overflow-style: none;       /* Internet Explorer 10+ */

    }}

    /* Stronger, tighter fade around the edges */
    div[id^="float-this-component"][style*="width: 350px"]::after {{
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

    /* Match helper panel position — hardcoded if needed */
    top: 12vh;
    right: 0px;
    width: 350px;
    height: calc(100vh - 24vh);  /* same as bottom: 12vh */

    /* Clip to rounded panel shape */
    clip-path: inset(0 round 0.5rem);
    }}

    /* Frosted-glass blur behind the panel */
    div[id^="float-this-component"][style*="width: 350px"]::before {{
    content: "";
    position: fixed;
    pointer-events: none;
    z-index: -2;

    /* Match helper panel position — hardcoded if needed */
    top: 12vh;
    right: 0px;
    width: 350px;
    height: calc(100vh - 24vh);  /* same as bottom: 12vh */

    /* Clip to rounded panel shape */
    clip-path: inset(0 round 0.5rem);
    

    backdrop-filter: blur(30px);
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

