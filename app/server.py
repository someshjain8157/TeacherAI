from pathlib import Path
from app.config import BOOKS_DIR

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from app.chatbot import ask

BASE_DIR = Path(__file__).parent

app = FastAPI(title="Akanksh AI 1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)


class Question(BaseModel):

    question: str

    subject: str = ""


@app.get("/", response_class=HTMLResponse)
def home():

    html_file = BASE_DIR / "templates" / "index.html"

    return html_file.read_text(encoding="utf-8")

@app.get("/subjects")
def get_subjects():

    subjects = []

    for folder in sorted(BOOKS_DIR.iterdir()):

        if folder.is_dir():
            subjects.append(folder.name)

    return {
        "subjects": subjects
    }

@app.post("/ask")
async def ask_api(data: Question):
    async def event_stream():
        async for chunk in ask(data.question, data.subject):
            yield chunk

    return StreamingResponse(event_stream(), media_type="text/plain")
