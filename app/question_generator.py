def detect_request(question: str):

    text = question.lower()

    math_signals = [
        "what do these numbers have in common",
        "next three numbers",
        "sequence",
        "pattern",
        "prime",
        "math",
        "arithmetic",
        "sum",
        "difference",
        "multiply",
        "divide",
    ]

    if any(signal in text for signal in math_signals):
        return "math"

    if "mcq" in text or "multiple choice" in text:
        return "mcq"

    if "true or false" in text or "true/false" in text:
        return "true_false"

    if "fill in the blank" in text or "fill in the blanks" in text:
        return "fill_blank"

    if "short answer" in text:
        return "short"

    if "long answer" in text:
        return "long"

    if "revision" in text or "notes" in text:
        return "revision"
    
    if "quiz me" in text:
        return "quiz"

    return "normal"


def build_instruction(request_type: str):

    prompts = {

        "normal":
        """
Answer ONLY from the textbook context.

Use simple language.

If the context contains relevant textbook information, answer from that information even if the exact wording is not present.

Only say:

I couldn't find that information in the Grade 9 textbooks.

if the retrieved context is empty or clearly unrelated to the question.
""",

        "math":
        """
Solve the question directly and concisely.

If the question asks for a pattern or sequence, identify the pattern first, then give the answer.

Keep the answer to 1-3 short sentences.

If the question cannot be solved from the information given, say so briefly.
""",

        "mcq":
"""
Create EXACTLY the number of MCQs requested by the student.

Rules:

- Every question MUST contain exactly 4 options.
- Format options exactly as:
A)
B)
C)
D)

- Only ONE option may be correct.
- Do NOT reveal the correct answer inside options.
- Do NOT write explanations.
- After each question write:

Answer: <correct option>

Example:

1. Question text

A) Option 1
B) Option 2
C) Option 3
D) Option 4

Answer: B

Generate questions ONLY from textbook context.
If the exact answer is not stated verbatim, use the closest supported textbook facts.
""",

        "true_false":
        """
Create 10 True/False questions.

Give answers at the end.

Use ONLY textbook information.
If the text is relevant but not exact, still use the best supported statement from the context.
""",

        "fill_blank":
        """
Create 10 fill in the blanks.

Provide answers at the end.

Use ONLY textbook information.
If the text is relevant but not exact, still use the best supported statement from the context.
""",

        "short":
        """
Create 5 short answer questions.

Provide answers.

Use ONLY textbook information.
If the text is relevant but not exact, still use the best supported statement from the context.
""",

        "long":
        """
Create 3 long answer questions.

Provide answers.

Use ONLY textbook information.
If the text is relevant but not exact, still use the best supported statement from the context.
""",

        "revision":
        """
Create revision notes.

Use bullet points.

Highlight important concepts.

Use ONLY textbook information.
If the text is relevant but not exact, still use the best supported statement from the context.
""",
        "quiz":
"""
Create a quiz using ONLY textbook information.

Rules:

- Generate AT LEAST 3 questions.
- Generate more only if requested.
- Every question MUST have exactly 4 options.

Format:

Question 1

A)
B)
C)
D)

Question 2

A)
B)
C)
D)

Question 3

A)
B)
C)
D)

After all questions:

Answers

1.
2.
3.

Do not explain.
Do not reveal answers before the end.
If the exact answer is not stated verbatim, use the closest supported textbook facts.
"""
    }

    return prompts.get(request_type, prompts["normal"])
