from openai import OpenAI

import streamlit as st
import requests
import streamlit.components.v1 as components


################################################################################## PYTHON ###########################################################################################


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
    f"You are a helper that estimates the mood in a given conversation. You must choose one phrase from this following list: \n"
    f"{emotion_choices} \n"
    f"You MUST choose exactly one of these phrases and output NOTHING else in your response. Your response should be a one phrase answer, where the f and digits is NOT seperated by a space. \n"
    f"Each phrase represents a different mood. For example, f00 could mean 'happy', and if you think the user's mood is happy, then you should output f00. Here is the specific mood of each phrase: \n"
    f"{emotion_meaning} \n"
    f"Notice that the list is separated by brackets. The first set of brackets describe f00, the second set describe f01, and so on. \n"
    f"This list is linked with the phrases list you are to return, so the corresponding set of brackets describe the corresponding phrase.\n"
    f"Your response will be used programatically to determine a Live2D model's reaction to the chat, where the Live2D model is acting as a avatar for the assistant. Keep that in mind when choosing.\n"
    f"Here is the conversation you are to estimate the mood of: \n"
)


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


################################################################################## HTML / JS ######################################################################################


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
  <script src="https://cdn.jsdelivr.net/npm/pixi-particles/dist/pixi-particles.min.js"></script>
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

    
    // ####################################################################################################################################################################################

    
    // Particle container & textures 
    const particleContainer = new PIXI.ParticleContainer(500, {
      scale: true,
      position: true,
      rotation: true,
      uvs: true,
      alpha: true
    });

    // Add it before adding the model, so particles appear behind
    app.stage.addChild(particleContainer); 

    // Default Emitter config 
    const emitterConfig = {
      // Keyframed fade in / out
      alpha: { 
            list: [
            { time: 0.0, value: 0.0 },   // at birth: invisible
            { time: 0.2, value: 1.0 },   // at 20% of lifespan: fully opaque
            { time: 1.0, value: 0.2 }    // at death (100%): fade down to 20%
            ],
            isStepped: false              // smooth interpolation
        },

        scale: { start: .4, end: .4 },          
        color: { start: "#ffffff", end: "#ffffff" }, // keep emoji colors intact
        speed: { start: 50, end: 25 },          // slower overall
        rotationSpeed: { min: 0, max: 20 },      // gentle spin
        lifetime: { min: .7, max: 1.2 },        // each lasts 1–1.5s
        frequency: 0.6,                         // one every 50ms → fewer particles
        emitterLifetime: 0,                      // infinite until toggled off
        maxParticles: 50,                       // cap at 100 total particles

        pos: { x: app.renderer.width * (2/3), y: app.renderer.height * (1/5) },
        addAtBack: false,
        spawnType: "point", 

        // Add an upward acceleration so they “float” up
        acceleration: { x: 0, y: -50 },
    };

    // Link the emitter config with a emoji
    const effectPresets = {
        f00: { 
            // 😊 happy
            textures: [
            PIXI.Texture.from('https://cdn.jsdelivr.net/gh/realityripple/emoji/joypixels/1f60a.png')
            ],
            config: emitterConfig,
        },
        f01: {
            // 🤩 very happy
            textures: [
            PIXI.Texture.from('https://cdn.jsdelivr.net/gh/realityripple/emoji/joypixels/1f929.png')
            ],
            config: emitterConfig,
        },
        f02: {
            // 😱 shocked (recoiling type)
            textures: [
            PIXI.Texture.from('https://cdn.jsdelivr.net/gh/realityripple/emoji/joypixels/1f631.png')
            ],
            config: emitterConfig,
        },
        f03: {
            // 😔 sad, melancholy, worried
            textures: [
            PIXI.Texture.from('https://cdn.jsdelivr.net/gh/realityripple/emoji/joypixels/1f614.png')
            ],
            config: emitterConfig,
        },
        f04: {
            // 🙂 happy neutral
            textures: [
            PIXI.Texture.from('https://cdn.jsdelivr.net/gh/realityripple/emoji/joypixels/1f642.png')
            ],
            config: emitterConfig,
        },
        f05: {
            // 😯 slightly shocked
            textures: [
            PIXI.Texture.from('https://cdn.jsdelivr.net/gh/realityripple/emoji/joypixels/1f62f.png')
            ],
            config: emitterConfig,
        },
        f06: {
            // 😳 embarrassed
            textures: [
            PIXI.Texture.from('https://cdn.jsdelivr.net/gh/realityripple/emoji/joypixels/1f633.png')
            ],
            config: emitterConfig,
        },
        f07: {
            // 😐 sad neutral
            textures: [
            PIXI.Texture.from('https://cdn.jsdelivr.net/gh/realityripple/emoji/joypixels/1f610.png')
            ],
            config: emitterConfig,
        }
    };


    const emitters = {};
    for (const [key, {textures, config}] of Object.entries(effectPresets)) {
    const e = new PIXI.particles.Emitter(
        particleContainer,
        textures,
        config
    );
    e.emit = false;
    emitters[key] = e;
    }

    // Ticker (shared) updates all emitters each frame
    let last = Date.now();
    app.ticker.add(() => {
    const now = Date.now();
    const dt  = (now - last) * 0.001;
    last = now;
    for (const e of Object.values(emitters)) {
        e.update(dt);
    }
    });

    
    // ####################################################################################################################################################################################


    // Open the WS
    const socket = new WebSocket("ws://localhost:8000/ws");

    socket.addEventListener("open", () => {
        console.log("[Live2D iframe] WebSocket connected");
    });
    socket.addEventListener("message", ev => {
        const { emotion } = JSON.parse(ev.data);
        console.log("[Live2D iframe] got emotion:", emotion);

        // Pick the matching emitter (or fallback)
        const chosen = emitters[emotion] || emitters.f04;  
        chosen.emit = true;

        // Stop it after 1s so it’s just a burst
        setTimeout(() => {
            chosen.emit = false;
        }, 1000);

        // Display the expression on the model
        if (model) {
            model.expression(emotion, 0);
            console.log('active emitters:', Object.keys(emitters), 'got emotion→', emotion);
        } else {
            console.log("Emotion not applied")
        }
    });

    socket.addEventListener("close", () => {
        console.warn("[Live2D iframe] WebSocket closed—will not receive updates");
    });

    
    // ####################################################################################################################################################################################

    
    // Build the model 
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