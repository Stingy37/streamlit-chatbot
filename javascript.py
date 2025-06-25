# javascript.py
import streamlit as st
import streamlit.components.v1 as components

def set_custom_js():
    components.html(
        """
        <script>
          console.log("iframe JS loaded — injecting full drag & follow logic into parent…");

          const parentScript = window.parent.document.createElement('script');
          parentScript.type = 'text/javascript';
          parentScript.text = `
            // —— Re-center main chat input under .block-container ——
            function centerChat() {
              const bc   = document.querySelector('.block-container');
              const chat = document.querySelector('.stChatFloatingInputContainer');
              if (!bc || !chat) return;
              const bcRect   = bc.getBoundingClientRect();
              const chatRect = chat.getBoundingClientRect();
              const x = bcRect.left + (bcRect.width - chatRect.width) / 2;
              chat.style.left = x + 'px';
            }

            // —— Keep helper input centered ——
            function centerHelperInput() {
              const panel    = document.querySelector('div[id^="float-this-component"][style*="width: 315px"]');
              const helperCh = panel?.querySelector('.stChatFloatingInputContainer');
              if (!panel || !helperCh) return;
              const pR = panel.getBoundingClientRect();
              const cR = helperCh.getBoundingClientRect();
              helperCh.style.left = (pR.left + (pR.width - cR.width)/2) + 'px';
            }

            // —— Draggable for .block-container ——
            function makeMainDraggable() {
              const el = document.querySelector('.block-container');
              if (!el) return;
              const saved = localStorage.getItem('main-container-pos');
              if (saved) {
                try {
                  const { top, left } = JSON.parse(saved);
                  el.style.position = 'fixed';
                  el.style.top  = top;
                  el.style.left = left;
                } catch {}
              }
              let sx, sy, ox, oy, onMove, onUp;
              el.addEventListener('dblclick', e => {
                e.preventDefault();
                const rect = el.getBoundingClientRect();
                sx = e.clientX; sy = e.clientY;
                ox = rect.left; oy = rect.top;
                onMove = ev => {
                  const dx = ev.clientX - sx, dy = ev.clientY - sy;
                  el.style.position = 'fixed';
                  el.style.left  = (ox + dx) + 'px';
                  el.style.top   = (oy + dy) + 'px';
                  centerChat();
                  centerHelperInput();
                };
                onUp = () => {
                  document.removeEventListener('mousemove', onMove);
                  document.removeEventListener('mouseup', onUp);
                  localStorage.setItem('main-container-pos',
                    JSON.stringify({ top: el.style.top, left: el.style.left })
                  );
                };
                document.addEventListener('mousemove', onMove);
                document.addEventListener('mouseup', onUp);
              });
            }

            // —— Helper panel draggable ——
            function makeHelperDraggable() {
              const el = document.querySelector('div[id^="float-this-component"][style*="width: 315px"]');
              if (!el) return;
              const saved = localStorage.getItem('helper-panel-pos');
              if (saved) {
                try {
                  const { top, left } = JSON.parse(saved);
                  el.style.position = 'fixed';
                  el.style.top  = top;
                  el.style.left = left;
                } catch {}
              }
              let sx, sy, ox, oy, onMove, onUp;
              el.addEventListener('dblclick', e => {
                e.preventDefault();
                const rect = el.getBoundingClientRect();
                sx = e.clientX; sy = e.clientY;
                ox = rect.left; oy = rect.top;
                onMove = ev => {
                  el.style.position = 'fixed';
                  el.style.left = (ox + ev.clientX - sx) + 'px';
                  el.style.top  = (oy + ev.clientY - sy) + 'px';
                };
                onUp = () => {
                  document.removeEventListener('mousemove', onMove);
                  document.removeEventListener('mouseup', onUp);
                  localStorage.setItem('helper-panel-pos',
                    JSON.stringify({ top: el.style.top, left: el.style.left })
                  );
                };
                document.addEventListener('mousemove', onMove);
                document.addEventListener('mouseup', onUp);
              });
            }

            // —— Reset logic ——
            function resetPositions() {
              ['main-container-pos','helper-panel-pos'].forEach(k => localStorage.removeItem(k));
              document.querySelectorAll('.block-container, div[id^="float-this-component"]').forEach(e => {
                e.style.removeProperty('position');
                e.style.removeProperty('top');
                e.style.removeProperty('left');
              });
              centerChat();
              centerHelperInput();
            }

            // —— Keybind: R to reset, but ignore Ctrl+R / ⌘+R ——  
            document.addEventListener('keydown', e => {
              if (e.key.toLowerCase() !== 'r') return;
              if (e.ctrlKey || e.metaKey) return;
              const a = document.activeElement;
              if (a && (a.tagName==='INPUT' || a.tagName==='TEXTAREA' || a.isContentEditable)) return;
              resetPositions();
            });

            // —— Click-proxy for your “+” upload button ——
            let lastWiredFileInput = null;
            function wireUploadPlus() {
              const plus = document.querySelector('.file-upload-button');
              const fi   = document.querySelector('input[type="file"]');
              if (plus && fi && fi !== lastWiredFileInput) {
                plus.addEventListener('click', () => fi.click());
                lastWiredFileInput = fi;
              }
            }

            // —— Initialize everything ——
            function initAll() {
              makeMainDraggable();
              makeHelperDraggable();
              centerChat();
              centerHelperInput();
              wireUploadPlus();
            }

            initAll();
            new MutationObserver(initAll).observe(document.body, { childList:true, subtree:true });
          `;
          window.parent.document.body.appendChild(parentScript);
        </script>
        """,
        height=0,
    )
