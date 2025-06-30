from openai import OpenAI

import streamlit as st
import requests
import streamlit.components.v1 as components


################################################################################## CONSTANTS ###########################################################################################


client = OpenAI()

emotion_choices = ["f00", "f01", "f02", "f03", "f04", "f05", "f06", "f07"]

emotion_meaning = [
    "[ happy ]", 
    "[ very happy ]", 
    "[ shocked (but recoiling type), disagreement, unhappy ]",
    "[ sad, melancholy, worried]",
    "[ happy neutral]",
    "[ slightly shocked ]",
    "[ embarrassed ]",
    "[ sad neutral ]"
    ]

system_instructions = (
    f"You are a helper that estimates the mood of user in a given conversation. You must choose one phrase from this following list: \n"
    f"{emotion_choices} \n"
    f"You MUST choose exactly one of these phrases and output NOTHING else in your response. Your response should be a one phrase answer, where the f and digits is NOT seperated by a space. \n"
    f"Each phrase represents a different mood. For example, f00 could mean 'happy', and if you think the user's mood is happy, then you should output f00. Here is the specific mood of each phrase: \n"
    f"{emotion_meaning} \n"
    f"Notice that the list is separated by brackets. The first set of brackets describe f00, the second set describe f01, and so on. \n"
    f"This list is linked with the phrases list you are to return, so the corresponding set of brackets describe the corresponding phrase.\n"
    f"Your response will be used programatically to determine a Live2D model's reaction to the chat, where the Live2D model is acting as a avatar for the assistant. Keep that in mind when choosing.\n"
    f"Here is the conversation you are to summarize: \n"
)


####################################################################################################################################################################################


def set_live_2d_emotion(chat_history, post_slot): # Where chat_history is st.session_state.messages
    convo = chat_history[-2:]
    prompt = system_instructions + "\n".join(
        f"{msg['role']}: {msg['content']}" for msg in convo
    )

    response = client.chat.completions.create(
        model="gpt-4.1-mini",       
        messages=[{"role":"system","content":prompt}],
    )

    emotion = response.choices[0].message.content.strip().lower()

    if emotion not in emotion_choices:
        emotion = "f04"

    # Send emotion to ws server
    try:
        requests.post(
            "http://localhost:8000/broadcast",
            json={"emotion": emotion},
            timeout=0.5
        )
    except requests.exceptions.RequestException as e:
        print("Failed to broadcast emotion:", e)



live_2d_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>Live2D Avatar</title>
  <style>
    html, body {
      margin: 0;
      padding: 0;
      overflow: hidden;
      background: transparent;    /* ← make the page background transparent */
    }
    canvas {
      display: block;
      background: transparent;    /* ← ensure the canvas itself is transparent */
    }
  </style>
  <script src="https://cubism.live2d.com/sdk-web/cubismcore/live2dcubismcore.min.js"></script>
  <script src="https://cdn.jsdelivr.net/gh/dylanNew/live2d/webgl/Live2D/lib/live2d.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/pixi.js@6.5.2/dist/browser/pixi.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/pixi-live2d-display/dist/index.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/pixi-live2d-display/dist/extra.min.js"></script>
</head>
<body>
  <canvas id="live2d-canvas"></canvas>
  <script>
    PIXI.Renderer.registerPlugin(
        'interaction',
        PIXI.InteractionManager
    );


     console.log(
      '[Debug] Before app creation – interaction plugin:',
      Boolean(PIXI.Renderer?.plugins?.interaction)
    );

    const app = new PIXI.Application({
      view: document.getElementById('live2d-canvas'),
      resizeTo: window,
      backgroundAlpha: 0,  // ← keep model background fully transparent
    });

    console.log(
      '[Debug] After app creation – interaction plugin:',
      Boolean(app.renderer.plugins.interaction),
      app.renderer.plugins.interaction
    );


    // Declare model in the outer scope
    let model = null;

    // Open the WS
    const socket = new WebSocket("ws://localhost:8000/ws");

    socket.addEventListener("open", () => {
        console.log("[Live2D iframe] WebSocket connected");
    });
    socket.addEventListener("message", ev => {
        const { emotion } = JSON.parse(ev.data);
        console.log("[Live2D iframe] got emotion:", emotion);
        if (model) {
            model.expression(emotion, 0);
            console.log("[Live2D iframe] applied:", emotion);
        } else {
            console.log("Emotion not applied")
        }
    });

    socket.addEventListener("close", () => {
        console.warn("[Live2D iframe] WebSocket closed—will not receive updates");
    });

    (async () => {
        // 1. fetch the raw model JSON
        const MODEL_URL = 'https://cdn.jsdelivr.net/gh/guansss/pixi-live2d-display/test/assets/haru/haru_greeter_t03.model3.json';
        const resp = await fetch(MODEL_URL);
        if (!resp.ok) {
            console.error(`Failed to load model JSON: ${resp.status}`);
            return;
        }
        const modelJson = await resp.json();
        modelJson.url = MODEL_URL;

        // Wrap in the Cubism4 settings class, and load from settings object
        const settings = new PIXI.live2d.Cubism4ModelSettings(modelJson);
        const loadedModel = await PIXI.live2d.Live2DModel.from(settings);
        model = loadedModel;

        // Grab the ExpressionManager and load expressions
        const mgr = model.internalModel.motionManager.expressionManager;
        if (mgr && mgr.definitions.length) {
            // kick off loads for each definition
            mgr.definitions.forEach((_, idx) => {
            mgr.loadExpression(idx).then(expr => {
                console.log(`[Live2D] expression #${idx} loaded`, expr);
            });
            });
        }

        // Print expressions 
        const defs = model.internalModel.settings.expressions;
        defs.forEach((expDef, i) => {
            console.log(`Definition #${i}:`, expDef.Name, "→", expDef.File);
        });

        // Build a name -> index lookup
        const nameToIndex = Object.fromEntries(
            model.internalModel.settings.expressions.map((def, i) => [def.Name, i])
        );

        // Print entire model settings
        console.log(
            "[Live2D DEBUG] settings keys:",
            Object.keys(model.internalModel.settings)
        );

        console.log(
            '[Debug] Before model.addChild – interaction plugin:',
            Boolean(app.renderer.plugins.interaction),
            app.renderer.plugins.interaction
        );

        // Place the model
        model.scale.set(0.16);
        model.anchor.set(0.5, 0.5);
        model.x = app.renderer.width / 2;
        model.y = app.renderer.height / 2;
        app.stage.addChild(model);

    })().catch(console.error);

  </script>
</body>
</html>
"""