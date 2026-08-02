from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.ai_service import generate_response
app = FastAPI()
# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class ChatRequest(BaseModel):
    message: str
@app.get("/")
def home():
    return {"message": "Chatbot Backend Running"}
@app.post("/chat")
def chat(request: ChatRequest):
    return generate_response(request.message)
    