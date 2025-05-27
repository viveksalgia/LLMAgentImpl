from Agents.agent_teams import invoke_agents
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from VectorDB.vector import create_vectordb
from phi.knowledge.csv import CSVKnowledgeBase
from phi.embedder.openai import OpenAIEmbedder
from phi.vectordb.chroma import ChromaDb
from dotenv import load_dotenv
import os
import uuid


load_dotenv()


class Message(BaseModel):
    question: str
    sessionid: str


app = FastAPI()

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    # Load initialization parameters
    data_file = os.getenv("VECTOR_DB_DATA")

    if os.path.exists(data_file):
        knowledge_base = create_vectordb(data_file)

        print("Knowledge base loaded successfully - " + os.getcwd())
    else:
        print("Unable to laod the knowledge base loaded successfully")

except Exception as e:
    print(f"Error loading knowledge base: {e}")


@app.get("/")
def root():
    return "Hi! This is Broadie. I am happy to hear from you. How may I help you today?"


@app.get("/getsessionid/")
def session():
    print("Inside sessionid")
    return uuid.uuid4()


@app.post("/ask/")
def ask(message: Message):
    # print(f"Sessionid - {message.sessionid}")

    def generate():
        for chunk in invoke_agents(
            message.question, knowledge_base, "N", message.sessionid
        ):
            print(f"Chunk = {chunk}")
            yield chunk

    return StreamingResponse(generate())
