from fastapi import FastAPI
from pydantic import BaseModel

from app.chatbot import ChatBot


app = FastAPI()

bot = ChatBot()


class Message(BaseModel):
    text: str


@app.get("/")
def home():
    return {"status": "AI Chatbot is running"}


@app.post("/chat")
def chat(msg: Message):

    reply = bot.get_reply(msg.text)

    return {
        "user": msg.text,
        "bot": reply
    }
