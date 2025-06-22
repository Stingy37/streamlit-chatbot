import streamlit as st

def set_custom_js():
    js = """
    <script>
        document.addEventListener('keydown', function(e) {
        const inChatInput = e.target.closest('[data-testid="stTextInput"]');
        if (inChatInput && e.key === 'Enter') {
            // after your message is added, jump to bottom
            setTimeout(() => {
            const chat = document.querySelector('[data-testid="stChatMessages"]');
            if (chat) chat.scrollTop = chat.scrollHeight;
            }, 50);
        }
        });

        // track helper state
        window.helperVisible = {str(st.session_state.helper_visible).lower()};

        function centerChat() {{
          const bc = document.querySelector('.block-container');
          const chat = document.querySelector('.stChatFloatingInputContainer');
          if (!bc || !chat) return;
          const bcRect = bc.getBoundingClientRect();
          const chatRect = chat.getBoundingClientRect();
          // compute left such that chat is centered in bc
          const x = bcRect.left + (bcRect.width - chatRect.width)/2;
          chat.style.left = x + 'px';
        }}

        // re-center whenever helper toggles or window resizes
        window.addEventListener('resize', centerChat);

        // assume your toggle button flips a CSS class or triggers a Streamlit re-render;
        // we re-run centerChat on a small delay
        const observer = new MutationObserver(() => {{
          centerChat();
        }});
        observer.observe(document.body, {{ childList: true, subtree: true }});

        // initial centering
        setTimeout(centerChat, 100);

        // 2) center the helper‐chat input in its floating panel
        function centerHelperInput() {{
        // select the 315px‐wide float panel (your helper panel)
        const panel = document.querySelector('div[id^="float-this-component"][style*="width: 315px"]');
        if (!panel) return;

        // inside that panel, grab its .stChatFloatingInputContainer
        const helperChat = panel.querySelector('.stChatFloatingInputContainer');
        if (!helperChat) return;

        const pR = panel.getBoundingClientRect();
        const cR = helperChat.getBoundingClientRect();
        const x = pR.left + (pR.width - cR.width) / 2;
        helperChat.style.left = x + 'px';
        }}

        // re-center on resize
        window.addEventListener('resize', () => {{
        centerChat();
        centerHelperInput();
        }});

        // re-center whenever Streamlit mutates the DOM
        const observer = new MutationObserver(() => {{
        centerChat();
        centerHelperInput();
        }});
        observer.observe(document.body, {{ childList: true, subtree: true }});

        // initial centering after Streamlit renders
        setTimeout(() => {{
        centerChat();
        centerHelperInput();
        }}, 100);


    </script>
    """
    st.markdown(js, unsafe_allow_html=True)
