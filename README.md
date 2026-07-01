# TeacherAI

TeacherAI is a FastAPI-based educational assistant for Grade 9 students. It lets users ask questions about textbook content, get answers with retrieval-augmented generation (RAG), and receive quiz-style or study-help responses grounded in local PDF books.

## 1. Setup

### Prerequisites
- Python 3.10+ (the project is currently running with Python 3.14 in this environment)
- Ollama installed and running locally
- A local virtual environment recommended

### Windows setup
```powershell
cd C:\TeacherAI
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Install and run Ollama
If Ollama is not installed yet, install it from https://ollama.com and then pull the model used by the app:

```powershell
ollama pull phi3:mini
ollama serve
```

### Prepare the textbook data
Place your PDF textbooks inside the books folder using this structure:

```text
books/
  SCIENCE - Exploration/
    chapter1.pdf
    chapter2.pdf
  ENGLISH- Kaveri/
    chapter1.pdf
```

### Build the vector database
The app uses Chroma with embeddings from local PDFs. Build the knowledge base once before first use:

```powershell
python -m app.rag
```

### Start the app
```powershell
uvicorn app.server:app --reload
```

Open http://127.0.0.1:8000 in your browser.

## 2. File overview

### Core app files
- app/server.py
  - Starts the FastAPI app.
  - Serves the frontend HTML, exposes the /subjects endpoint, and handles the /ask streaming API.

- app/chatbot.py
  - Main conversation logic.
  - Detects the request type, retrieves relevant textbook context, and streams the answer from Ollama.

- app/rag.py
  - Implements the retrieval layer.
  - Reads PDFs, splits them into chunks, stores them in Chroma, and retrieves the most relevant chunks for a student question.

- app/config.py
  - Central configuration for project paths, model names, chunk size, overlap, and retrieval count.

- app/question_generator.py
  - Converts student requests into prompt instructions.
  - Detects whether the user wants a normal answer, math help, MCQ, quiz, true/false, or revision notes.

- app/memory.py
  - Stores recent conversation history in memory for the active session.

- app/quiz.py
  - Tracks the current in-memory quiz state.

### Frontend files
- app/static/app.js
  - Browser-side logic for sending questions, handling streaming responses, and speaking the answer aloud.

- app/templates/index.html
  - Main web page UI for the chatbot.

- app/static/style.css
  - Styles for the app interface.

### Data and utilities
- books/
  - Folder containing subject-wise textbook PDFs.

- chromadb/
  - Persisted vector database created by Chroma.

- app/index_books.py
  - Small utility that scans PDFs and reports their text size; useful for inspection and validation.

- requirements.txt
  - Python dependencies for the project.

## 3. How the project works end to end

1. The user opens the web app in the browser.
2. The frontend loads the available subject folders from the backend.
3. When the user asks a question, the browser sends it to the FastAPI /ask endpoint.
4. The backend identifies the type of request (normal answer, math, quiz, MCQ, etc.).
5. For most requests, the app retrieves the most relevant textbook passages from the local PDF knowledge base using RAG.
6. The retrieved textbook context is passed to Ollama along with the user question and task-specific instructions.
7. The model answers using the supplied context, and the response is streamed back to the UI in real time.
8. The frontend displays the answer, shows the source book/chapter/page metadata, and optionally speaks the answer aloud.
9. The conversation is saved in memory for the current session.

## 4. Notes
- The app is designed to work locally and does not depend on a cloud API for answering.
- The quality of responses depends on the quality of the PDF content and the Ollama model selected.
- If you add or replace textbook PDFs, rebuild the Chroma database so the new content is searchable.
