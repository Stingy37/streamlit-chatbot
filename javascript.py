# javascript.py
import streamlit as st
import streamlit.components.v1 as components

def set_dragging_resizing_js():
    components.html(
        r"""
        <script>
          console.log("iframe JS loaded — injecting full drag & follow logic into parent…");

          const parentScript = window.parent.document.createElement('script');
          parentScript.type = 'text/javascript';
          parentScript.text = `

            // Capture the original defaults so that reset logic still works  
            const DEFAULT_TOP  = '8vh';  
            const DEFAULT_LEFT = '23.5%';
            const DEFAULT_L2D_TOP   = '3vh';
            const DEFAULT_L2D_LEFT  = '-100px';


            // Helper to inject/override default CSS, so that no jumping happens on st.reruns ——  
            function updateDefaultCSS(top, left) {
              let style = document.getElementById('main-pos-override');
              if (!style) {
                style = document.createElement('style');
                style.id = 'main-pos-override';
                document.head.appendChild(style);
              }
              style.textContent = \`
                div[id^="float-this-component"][style*="width: 800px"] {
                  position: fixed !important;
                  top: \${top} !important;
                  left: \${left} !important;
                }
                div[id^="float-this-component"][style*="width: 800px"]::before,
                div[id^="float-this-component"][style*="width: 800px"]::after {
                  position: fixed !important;
                  top: \${top} !important;
                  left: \${left} !important;
                }
              \`;
            }

            // Helper to inject/override Live2D’s default CSS so no jump on reruns   
            function updateLive2DDefaultCSS(top, left) {
              let style = document.getElementById('live2d-pos-override');
              if (!style) {
                style = document.createElement('style');
                style.id = 'live2d-pos-override';
                document.head.appendChild(style);
              }
              style.textContent = \`
                /* target the same wrapper your drag code uses */
                div[id^="float-this-component"][style*="width: 400px"] {
                  position: fixed !important;
                  top: \${top} !important;
                  left: \${left} !important;
                }
              \`;
            }


            // Disable clicks on the iframe so that parent div is draggable 
            function disableLive2DPointerEvents(){
              // 1) find the float wrapper by its inline width:400px
              const wrapper = document.querySelector(
                'div[id^="float-this-component"][style*="width: 400px"]'
              );
              if (!wrapper) return;

              // 2) find the actual iframe inside it
              const live2dIframe = wrapper.querySelector('iframe');
              if (live2dIframe) {
                live2dIframe.style.pointerEvents = 'none';
              }
            }


          
            // Re-center main chat input under .block-container ——
            function centerChat() {
              const panel = document.querySelector('[data-st-key="main_chat_panel"]');
              if (!panel) return;
              const inputWrap = panel.querySelector('div[id^="float-this-component-"]');
              if (!inputWrap) return;
              const pR = panel.getBoundingClientRect();
              const iR = inputWrap.getBoundingClientRect();
              const x = pR.left + (pR.width - iR.width) / 2;
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

              // restore saved position and override defaults...
              const saved = localStorage.getItem('main-container-pos');
              if (saved) {
                try {
                  const { top, left } = JSON.parse(saved);
                  // apply via CSS override
                  updateDefaultCSS(top, left);
                  // also position any existing element immediately
                  el.style.position = 'fixed';
                  el.style.top      = top;
                  el.style.left     = left;
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

                // Remove the position pinning if the user if dragging again
                const override = document.getElementById('main-pos-override');
                if (override) override.remove();

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

                  // persist & override via CSS
                  const finalTop  = el.style.top;
                  const finalLeft = el.style.left;
                  localStorage.setItem(
                    'main-container-pos',
                    JSON.stringify({ top: finalTop, left: finalLeft })
                  );
                  updateDefaultCSS(finalTop, finalLeft);
                };

                document.addEventListener('mousemove', onMove);
                document.addEventListener('mouseup', onUp);
              });
            }

            // Immediately restore override on load
            (function restoreOnLoad(){
              const saved = localStorage.getItem('main-container-pos');
              if (saved) {
                try {
                  const { top, left } = JSON.parse(saved);
                  updateDefaultCSS(top, left);
                } catch {}
              }
            })();

            // Immediately restore Live2D override on load
            (function restoreLive2DOnLoad(){
              const saved = localStorage.getItem('live2d-pos');
              if (saved) {
                try {
                  const { top, left } = JSON.parse(saved);
                  updateLive2DDefaultCSS(top, left);
                } catch {}
              }
            })();

            // NOTE -> NOT implemented currently
            function makeHelperDraggable() {
              const el = document.querySelector(
                'div[id^="float-this-component"][style*="width: 315px"]'
              );
              if (!el) return;

              const toggleEl = document.querySelector(
                'div[id^="float-this-component"][style*="width: 2rem"]'
              );

              // restore saved helper position
              const saved = localStorage.getItem('helper-panel-pos');
              if (saved) {
                try {
                  const { top, left } = JSON.parse(saved);
                  el.style.position = 'fixed';
                  el.style.top      = top;
                  el.style.left     = left;
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

                // record how far the toggle sits from the panel’s top-left
                let toggleOffsetX = 0, toggleOffsetY = 0;
                if (toggleEl) {
                  const tR = toggleEl.getBoundingClientRect();
                  toggleOffsetX = tR.left - rect.left;
                  toggleOffsetY = tR.top  - rect.top;
                }

                // pin it
                el.style.position = 'fixed';
                el.style.left     = rect.left + 'px';
                el.style.top      = rect.top  + 'px';

                sx = e.clientX; sy = e.clientY;
                ox = rect.left; oy = rect.top;

                onMove = ev => {
                  const newLeft = ox + (ev.clientX - sx);
                  const newTop  = oy + (ev.clientY - sy);

                  // Move panel
                  el.style.left = newLeft + 'px';
                  el.style.top  = newTop  + 'px';

                  // also move the toggle by the same offset
                  if (toggleEl) {
                    toggleEl.style.position = 'fixed';
                    toggleEl.style.left     = (newLeft + toggleOffsetX) + 'px';
                    toggleEl.style.top      = (newTop  + toggleOffsetY) + 'px';
                  }

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

            // —— Draggable for Live2D avatar ——
            function makeLive2DDraggable() {
              // 1) find your floated container
              const container = document.querySelector(
                'div[id^="float-this-component"][style*="width: 400px"]'
              );
              if (!container) {
                console.warn('Live2D container not found');
                return;
              }

              // 2) find its iframe
              const iframe = container.querySelector('iframe');
              if (!iframe) {
                console.warn('Live2D iframe not found');
                return;
              }

              // 3) restore saved position on load
              const saved = localStorage.getItem('live2d-pos');
              if (saved) {
                try {
                  const { top, left } = JSON.parse(saved);
                  container.style.position = 'fixed';
                  container.style.top = top;
                  container.style.left = left;
                  // re‑apply your CSS override so pseudo‑elements track
                  updateLive2DDefaultCSS(top, left);
                } catch {}
              }

              // 4) when the iframe’s document is ready, grab the canvas
              function setupDragOnCanvas() {
                const cw = iframe.contentWindow;
                const doc = cw.document;
                const canvas = doc.getElementById('live2d-canvas');
                if (!canvas) {
                  console.warn('Canvas inside iframe not found');
                  return;
                }

                let startX, startY, origX, origY;

                canvas.addEventListener('dblclick', e => {
                  e.preventDefault();

                  // remove any previous override so we can use free positioning
                  const override = document.getElementById('live2d-pos-override');
                  if (override) override.remove();

                  // pin container exactly where it is
                  const rect = container.getBoundingClientRect();
                  container.style.position = 'fixed';
                  container.style.top = rect.top + 'px';
                  container.style.left = rect.left + 'px';
                  container.style.removeProperty('transform');

                  // record start coords
                  startX = e.clientX;
                  startY = e.clientY;
                  origX = rect.left;
                  origY = rect.top;

                  // add a full‑screen blocker to capture mouse events
                  const blocker = document.createElement('div');
                  blocker.id = 'iframe-drag-blocker';
                  Object.assign(blocker.style, {
                    position: 'fixed',
                    top: '0', left: '0',
                    width: '100vw', height: '100vh',
                    zIndex: '9999',
                    cursor: 'grabbing',
                    background: 'transparent'
                  });
                  document.body.appendChild(blocker);

                  // drag logic
                  function onMove(ev) {
                    const dx = ev.clientX - startX;
                    const dy = ev.clientY - startY;
                    container.style.left = (origX + dx) + 'px';
                    container.style.top = (origY + dy) + 'px';
                  }

                  function onUp() {
                    document.removeEventListener('mousemove', onMove);
                    document.removeEventListener('mouseup', onUp);
                    const b = document.getElementById('iframe-drag-blocker');
                    if (b) b.remove();

                    // persist and re‑apply CSS override
                    const top = container.style.top;
                    const left = container.style.left;
                    localStorage.setItem('live2d-pos', JSON.stringify({ top, left }));
                    updateLive2DDefaultCSS(top, left);
                  }

                  document.addEventListener('mousemove', onMove);
                  document.addEventListener('mouseup', onUp);
                });
              }

              // hook iframe load (or run immediately if already loaded)
              iframe.addEventListener('load', setupDragOnCanvas);
              if (iframe.contentWindow.document.readyState === 'complete') {
                setupDragOnCanvas();
              }
            }

            

            // —— Reset logic ——
            function resetPositions() {
              // 1) Clear stored positions
              localStorage.removeItem('main-container-pos');
              localStorage.removeItem('helper-panel-pos');
              localStorage.removeItem('live2d-pos');


              // 2) Remove our injected override stylesheet
              const style = document.getElementById('main-pos-override');
              if (style) style.remove();
              const l2dStyle = document.getElementById('live2d-pos-override');
              if (l2dStyle) l2dStyle.remove();

              // 3) Restore any inline positioning so the new panels render with pure CSS defaults
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

              // 4) **Re‑apply your original pseudo‑element positions** (the part we missed)
              if (mainBefore) {
                mainBefore.style.top  = DEFAULT_TOP;
                mainBefore.style.left = DEFAULT_LEFT;
              }
              if (mainAfter) {
                mainAfter.style.top   = DEFAULT_TOP;
                mainAfter.style.left  = DEFAULT_LEFT;
              }
              if (helperBefore) {
                helperBefore.style.top   = DEFAULT_TOP;
                helperBefore.style.left  = 'auto';
                helperBefore.style.right = '0';
              }
              if (helperAfter) {
                helperAfter.style.top    = DEFAULT_TOP;
                helperAfter.style.left   = 'auto';
                helperAfter.style.right  = '0';
              }

              // 6) restore Live2D to its original CSS defaults
              const live2d = document.querySelector(
                'div[id^="float-this-component"][style*="width: 400px"]'
              );
              if (live2d) {
                live2d.style.removeProperty('position');
                live2d.style.removeProperty('top');
                live2d.style.removeProperty('left');
              }

              // 5) Finally, re‑center your inputs under the freshly‑reset panels
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

            // Change this so that we are changing BOTH positions of the toggle 
            // NOTE -> NOT IMPLEMENTED currently
            function positionToggle() {
              const panel    = document.querySelector(
                'div[id^="float-this-component"][style*="width: 315px"]'
              );
              const toggleEl = document.querySelector(
                'div[id^="float-this-component"][style*="width: 2rem"]'
              );
              if (!panel || !toggleEl) return;

              const pR = panel.getBoundingClientRect();
              const tW = toggleEl.getBoundingClientRect().width;
              const onRight = (pR.left + pR.width / 2) > window.innerWidth / 2;

              toggleEl.style.position = 'fixed';
              toggleEl.style.top      = pR.top + 'px';

              // compute exactly where it should go
              const newRight = onRight
                ? (window.innerWidth - (pR.left) - tW) + 'px'
                : (window.innerWidth - (pR.left + pR.width)) + 'px';

              // **this will override your Python‐injected right with !important**
              toggleEl.style.setProperty('right', newRight, 'important');
            }

            // —— Initialize everything ——
            function initAll() {
              cacheShadowRules();
              makeMainDraggable();
              centerChat();
              centerHelperInput();
              wireUploadPlus();
              disableLive2DPointerEvents();
              makeLive2DDraggable();
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
