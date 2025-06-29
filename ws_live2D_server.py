from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List
import json

app = FastAPI()

class Emotion(BaseModel):
    emotion: str

# keep track of all connected websocket clients
clients: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
    try:
        # we don’t expect clients to send us anything,
        # so just stall forever until disconnect:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        clients.remove(ws)

async def broadcast(emotion: str):
    data = json.dumps({"emotion": emotion})
    to_remove = []
    for ws in clients:
        try:
            await ws.send_text(data)
        except:
            to_remove.append(ws)
    for ws in to_remove:
        clients.remove(ws)

@app.post("/broadcast")
async def broadcast_endpoint(msg: Emotion):
    # called by Streamlit app to push new emotion
    await broadcast(msg.emotion)
    return {"status": "ok"}
