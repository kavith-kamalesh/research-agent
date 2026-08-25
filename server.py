from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from agent.planner import run
from agent.protocol_picker import suggest_protocol
from agent.voice_output import speak
import threading
import os

app = FastAPI()
sessions = {}

class Message(BaseModel):
    session_id: str
    text: str
    protocol_override: str = None

class ProtocolCheck(BaseModel):
    text: str

@app.post("/check_protocol")
def check_protocol(msg: ProtocolCheck):
    suggestion = suggest_protocol(msg.text)
    return {"suggestion": suggestion}

@app.post("/chat")
def chat(msg: Message):
    history = sessions.get(msg.session_id)
    user_input = msg.text
    if msg.protocol_override:
        user_input = f"[Use protocol {msg.protocol_override}] {user_input}"
    reply, history = run(user_input, history)
    sessions[msg.session_id] = history
    return {"reply": reply}

@app.post("/speak")
def speak_text(msg: Message):
    threading.Thread(target=speak, args=(msg.text,)).start()
    return {"status": "speaking"}

app.mount("/", StaticFiles(directory="web", html=True), name="web")
