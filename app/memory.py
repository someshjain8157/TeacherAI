"""
Simple in-memory conversation history.

For Akanksh AI 1.0 we keep only the latest conversation.
No database is required.
"""

MAX_MESSAGES = 10

conversation = []


def add(role: str, content: str):

    conversation.append(
        {
            "role": role,
            "content": content
        }
    )

    while len(conversation) > MAX_MESSAGES:
        conversation.pop(0)


def get():

    return conversation.copy()


def clear():

    conversation.clear()