

def get_emotion_from_chat(chat_history):
    pass


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
</head>
<body>
  <canvas id="live2d-canvas"></canvas>
  <script>
    const app = new PIXI.Application({
      view: document.getElementById('live2d-canvas'),
      resizeTo: window,
      backgroundAlpha: 0,  // ← keep model background fully transparent
    });
    const MODEL_URL = 'https://cdn.jsdelivr.net/gh/guansss/pixi-live2d-display/test/assets/haru/haru_greeter_t03.model3.json';
    PIXI.live2d.Live2DModel.from(MODEL_URL)
      .then(model => {
        model.scale.set(0.16);
        model.anchor.set(0.5, 0.5);
        model.x = app.renderer.width / 2;
        model.y = app.renderer.height / 2;
        app.stage.addChild(model);
        model.internalModel.motionManager.startAnimation('Idle');
      })
      .catch(console.error);
  </script>
</body>
</html>
"""



