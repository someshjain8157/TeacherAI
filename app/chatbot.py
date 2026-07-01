import asyncio
import json

import ollama

from app.memory import add
from app.question_generator import build_instruction, detect_request
from app.config import OLLAMA_MODEL, TOP_K
from app.rag import retrieve_documents


SHORT_SUBJECTS = {
    "SCIENCE - Exploration",
    "ENGLISH- Kaveri",
    "SOCIAL SCIENCE - Understand Society",
}


def get_answer_length_guidance(subject: str, request_type: str) -> str:
    if request_type == "math":
        return "Keep the answer very short, ideally under 40 words unless the question asks for more detail."

    if subject in SHORT_SUBJECTS:
        return "Keep the answer around 50-60 words max."

    return "Keep the answer to 2-3 sentences and under 60 words."


# -----------------------------
# Async Ask Function (Streaming)
# -----------------------------
async def ask(question: str, subject: str = ""):
    request_type = detect_request(question)
    answer_length_guidance = get_answer_length_guidance(subject, request_type)
    instruction = build_instruction(request_type)

    if request_type == "math":
        chat_options = {
            "temperature": 0.2,
            "num_predict": 96,
        }
        messages = [
            {
                "role": "system",
                "content": f"""
                You are Akanksh AI 1.0.
                You are a concise math helper for students.

                Rules:
                - Solve the math question directly.
                - Do not mention textbooks or retrieval.
                - Keep the answer very short.
                - If a sequence pattern is asked, state the pattern and the next terms.

                Task rules:
                {instruction}
                """,
            },
            {
                "role": "user",
                "content": question,
            },
        ]
        sources = []
        context = ""
    else:
        retrieval_k = 1 if request_type == "normal" else TOP_K

        # Run retrieval in a background thread so the event loop stays responsive.
        retrieval = await asyncio.to_thread(
            retrieve_documents,
            question,
            subject,
            retrieval_k,
        )

        context = retrieval["context"]
        sources = retrieval["sources"]
        context_preview = " ".join(context.split())[:320].encode("ascii", "ignore").decode("ascii")
        print(
            f"[RAG] question={question!r} subject={subject!r} type={request_type} "
            f"k={retrieval_k} chunks={len(retrieval['docs'])} sources={len(sources)} "
            f"context_preview={context_preview!r}"
        )

        if not context.strip():
            yield "I couldn't find that information in the Grade 9 textbooks."
            yield f"\n\n[SOURCES]{json.dumps([])}"
            return

        if request_type in ["mcq", "quiz"]:
            instruction += f"""
            Student Request:
            {question}

            Generate exactly what the student requested.
            Generate only 3 questions unless the student requested more.
            Do not generate extra questions.
            Follow formatting exactly.
            """

        messages = [
            {
                "role": "system",
                "content": f"""
                You are Akanksh AI 1.0.
                You are an AI assistant for Grade 9 students.

                Rules:
                - Use only the TEXTBOOK CONTEXT provided below.
                - Do not use prior knowledge, memory, or outside facts.
                - Answer directly without restating the question or adding an intro.
                - Start with the answer itself.
                - If the context contains relevant information, answer from it even if the exact wording is not present.
                - Only say "I couldn't find that information in the Grade 9 textbooks." when the retrieved context is empty or clearly unrelated.
                - {answer_length_guidance}
                - For MCQ, quiz, true/false, fill-in-the-blank, short answer, long answer, and revision requests, follow the requested format exactly.
                - Prefer the most relevant facts from the first few context chunks.

                Task rules:
                {instruction}
                """,
            },
            {
                "role": "user",
                "content": f"""
                TEXTBOOK CONTEXT
                {context}

                STUDENT REQUEST
                {question}

            Important:
            - Answer using only the TEXTBOOK CONTEXT.
            - If the context is relevant but not perfectly worded, answer with the closest supported textbook meaning.
            - Use the fallback sentence only if the context is empty or unrelated.
            - {answer_length_guidance}
            """,
        },
    ]

        chat_options = {
            "temperature": 0.2,
            "num_predict": 180,
        }

    # -----------------------------
    # Ollama Chat Streaming
    # -----------------------------
    loop = asyncio.get_running_loop()

    def run_chat():
        return ollama.chat(model=OLLAMA_MODEL, messages=messages, stream=True, options=chat_options)

    response_stream = await loop.run_in_executor(None, run_chat)

    answer_chunks = []
    for chunk in response_stream:
        text = chunk["message"]["content"]
        answer_chunks.append(text)
        yield text  # stream each chunk to FastAPI/UI

    answer = "".join(answer_chunks)

    # Save conversation
    add("user", question)
    add("assistant", answer)

    # At the end, yield sources marker as JSON for the frontend.
    yield f"\n\n[SOURCES]{json.dumps(sources)}"
