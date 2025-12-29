from fastapi import FastAPI
from agent import get_response, speak

app = FastAPI()

@app.post("/talk")
def talk(text: str):
    reply = get_response(text)
    speak(reply)
    return {"response": reply}
