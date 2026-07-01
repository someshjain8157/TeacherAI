# TeacherAI

TeacherAI is a FastAPI-based educational assistant for Grade 9 students. It lets users ask questions about textbook content, get answers with retrieval-augmented generation (RAG), and receive quiz-style or study-help responses grounded in local PDF books.

## 1. Setup

### Prerequisites
- Python 3.10+ (the project is currently running with Python 3.14 in this environment)
- Ollama installed and running locally
- A local virtual environment recommended
- Internet access for the first install of Python packages and Ollama model download

### 1.1 Create a virtual environment
```powershell
cd C:\TeacherAI
python -m venv .venv
.\.venv\Scripts\activate
```

### 1.2 Install project libraries
```powershell
pip install -r requirements.txt
```

### 1.3 Install and run Ollama
If Ollama is not installed yet, install it from https://ollama.com and then pull the model used by the app:

```powershell
ollama pull phi3:mini
ollama serve
```

### 1.4 Project folder structure
```text
TeacherAI/
  app/
    chatbot.py
    config.py
    memory.py
    question_generator.py
    quiz.py
    rag.py
    server.py
    static/
      app.js
      style.css
      avatar/
    templates/
      index.html
  books/
    SCIENCE - Exploration/
    ENGLISH- Kaveri/
    HINDI - Ganga/
    MATH - Ganita Manjari/
    SANSKRIT - Sarada/
    SOCIAL SCIENCE - Understand Society/
  chromadb/
  requirements.txt
  README.md
```

### 1.5 Add PDF textbooks
Place your textbook PDFs inside the subject folders under books/. Example:

```text
books/
  SCIENCE - Exploration/
    chapter1.pdf
    chapter2.pdf
  ENGLISH- Kaveri/
    chapter1.pdf
```

### 1.6 Create the RAG knowledge base
The app uses Chroma and sentence embeddings to retrieve relevant textbook content. Build the knowledge base once before first use:

```powershell
python -m app.rag
```

This will:
- read the PDFs from the books folder
- split them into chunks
- create or update the vector database in chromadb/

### 1.7 Start the server
```powershell
uvicorn app.server:app --reload
```

Then open:
```text
http://127.0.0.1:8000
```

## 2. Files to create or update

### Required files
- requirements.txt
  - Python dependencies for the project
- .venv/
  - Local virtual environment for the app
- chromadb/
  - Created automatically when the RAG database is built

### Optional files you may create
- .gitignore
  - Recommended to ignore .venv/, __pycache__/, and chromadb/ if you do not want to commit them
- logs/
  - Optional folder for debugging or runtime logs

## 3. How to convert PDFs into RAG content

The app does not use a manual PDF-to-RAG conversion step. Instead, it automatically processes PDFs when you run:

```powershell
python -m app.rag
```

That command will:
1. scan all PDF files inside the books/ folder
2. extract text from each page
3. split the text into chunks
4. generate embeddings
5. store the vector database in chromadb/

If you add new books or replace existing PDFs, run the same command again so the search index is updated.

## 4. File overview

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
  - Styles for the app interface, including the avatar layout and image states.

- app/static/avatar/
  - Contains the avatar images used for idle, listening, thinking, and speaking states.

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
