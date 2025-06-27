# javascript.py
import streamlit as st
import streamlit.components.v1 as components

def set_dragging_resizing_js():
    components.html(
        """
        <script>
          console.log("iframe JS loaded — injecting full drag & follow logic into parent…");

          const parentScript = window.parent.document.createElement('script');
          parentScript.type = 'text/javascript';
          parentScript.text = `

          
            // Re-center main chat input under .block-container ——
            function centerChat() {
              // 1) Get your top-level floated panel by key
              const panel = document.querySelector('[data-st-key="main_chat_panel"]');
              if (!panel) return;

              // 2) Find the nested input wrapper div that float-css-helper created
              const inputWrap = panel.querySelector('div[id^="float-this-component-"]');
              if (!inputWrap) return;

              // 3) Measure them
              const pR = panel.getBoundingClientRect();
              const iR = inputWrap.getBoundingClientRect();

              // 4) Compute center X
              const x = pR.left + (pR.width - iR.width) / 2;

              // 5) Override any existing left/transform with !important
              inputWrap.style.setProperty('left', x + 'px', 'important');
              inputWrap.style.removeProperty('transform');
            }


            let mainBefore, mainAfter, helperBefore, helperAfter;
            function cacheShadowRules() {
              for (const sheet of document.styleSheets) {
                try {
                  for (const rule of sheet.cssRules) {
                    switch (rule.selectorText) {
                      case 'div[id^="float-this-component"][style*="width: 800px"]::before':
                        mainBefore   = rule; break;
                      case 'div[id^="float-this-component"][style*="width: 800px"]::after':
                        mainAfter    = rule; break;
                      case 'div[id^="float-this-component"][style*="width: 315px"]::before':
                        helperBefore = rule; break;
                      case 'div[id^="float-this-component"][style*="width: 315px"]::after':
                        helperAfter  = rule; break;
                    }
                  }
                } catch {}
              }
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

            
            // —— Draggable for main_chat_panel ——
            function makeMainDraggable() {
              const el = document.querySelector(
                'div[id^="float-this-component"][style*="width: 800px"]'
              );
              if (!el) return;

              // restore saved position...
              const saved = localStorage.getItem('main-container-pos');
              if (saved) {
                try {
                  const { top, left } = JSON.parse(saved);
                  el.style.position = 'fixed';
                  el.style.top      = top;
                  el.style.left     = left;
                  // also update the shadows once on load:
                  if (mainBefore) {
                      mainBefore.style.top  = top;
                      mainBefore.style.left = left;
                  }
                  if (mainAfter) {
                      mainAfter.style.top   = top;
                      mainAfter.style.left  = left;
                  }
                } catch {}
              }

              let sx, sy, ox, oy, onMove, onUp;
              el.addEventListener('dblclick', e => {
                e.preventDefault();
                const rect = el.getBoundingClientRect();

                // pin it fixed at that spot
                el.style.position = 'fixed';
                el.style.left     = rect.left + 'px';
                el.style.top      = rect.top  + 'px';
                el.style.removeProperty('margin-left');
                el.style.removeProperty('transform');

                // record drag start
                sx = e.clientX; sy = e.clientY;
                ox = rect.left; oy = rect.top;

                onMove = ev => {
                  const dx = ev.clientX - sx;
                  const dy = ev.clientY - sy;
                  const newLeft = ox + dx;
                  const newTop  = oy + dy;

                  // move the panel
                  el.style.left = newLeft + 'px';
                  el.style.top  = newTop  + 'px';

                  // **also move the fixed pseudos**
                  if (mainBefore) {
                    mainBefore.style.top  = newTop  + 'px';
                    mainBefore.style.left = newLeft + 'px';
                  }
                  if (mainAfter) {
                    mainAfter.style.top  = newTop  + 'px';
                    mainAfter.style.left = newLeft + 'px';
                  }

                  centerChat();
                  centerHelperInput();
                };

                onUp = () => {
                  document.removeEventListener('mousemove', onMove);
                  document.removeEventListener('mouseup', onUp);
                  localStorage.setItem(
                    'main-container-pos',
                    JSON.stringify({ top: el.style.top, left: el.style.left })
                  );
                };

                document.addEventListener('mousemove', onMove);
                document.addEventListener('mouseup', onUp);
              });
            }

            
            function makeHelperDraggable() {
              const el = document.querySelector(
                'div[id^="float-this-component"][style*="width: 315px"]'
              );
              if (!el) return;

              // restore saved helper position
              const saved = localStorage.getItem('helper-panel-pos');
              if (saved) {
                try {
                  const { top, left } = JSON.parse(saved);
                  el.style.position = 'fixed';
                  el.style.top      = top;
                  el.style.left     = left;
                  // also push the helper pseudos into place
                  if (helperBefore) {
                    helperBefore.style.top  = top;
                    helperBefore.style.left = left;
                  }
                  if (helperAfter) {
                    helperAfter.style.top   = top;
                    helperAfter.style.left  = left;
                  }
                } catch {}
              }

              let sx, sy, ox, oy, onMove, onUp;
              el.addEventListener('dblclick', e => {
                e.preventDefault();
                const rect = el.getBoundingClientRect();

                // pin it
                el.style.position = 'fixed';
                el.style.left     = rect.left + 'px';
                el.style.top      = rect.top  + 'px';

                sx = e.clientX; sy = e.clientY;
                ox = rect.left; oy = rect.top;

                onMove = ev => {
                  const newLeft = ox + (ev.clientX - sx);
                  const newTop  = oy + (ev.clientY - sy);

                  el.style.left = newLeft + 'px';
                  el.style.top  = newTop  + 'px';

                  // move helper pseudos
                  if (helperBefore) {
                    helperBefore.style.top  = newTop  + 'px';
                    helperBefore.style.left = newLeft + 'px';
                  }
                  if (helperAfter) {
                    helperAfter.style.top   = newTop  + 'px';
                    helperAfter.style.left  = newLeft + 'px';
                  }
                };
                onUp = () => {
                  document.removeEventListener('mousemove', onMove);
                  document.removeEventListener('mouseup', onUp);
                  localStorage.setItem(
                    'helper-panel-pos',
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
              // Target only two floated panels by their width markers
              document
                .querySelectorAll(
                  'div[id^="float-this-component"][style*="width: 800px"], ' +
                  'div[id^="float-this-component"][style*="width: 315px"]'
                )
                .forEach(e => {
                  e.style.removeProperty('position');
                  e.style.removeProperty('top');
                  e.style.removeProperty('left');
                });

              // restore main pseudos to original css
              if (mainBefore) { mainBefore.style.top = '8vh';    mainBefore.style.left = '23.5%'; }
              if (mainAfter)  { mainAfter.style.top  = '8vh';    mainAfter.style.left  = '23.5%'; }

              // restore helper pseudos to original css
              if (helperBefore) { helperBefore.style.top = '8vh';  helperBefore.style.left = 'auto'; helperBefore.style.right = '0'; }
              if (helperAfter)  { helperAfter.style.top  = '8vh';  helperAfter.style.left = 'auto'; helperAfter.style.right = '0'; }

              // Re‐center inputs
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
              cacheShadowRules();
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


def set_styling_js():
    pass
