from typing import NamedTuple

class ChatMessage(NamedTuple):
    content: str

def chat_message(content: str) -> ChatMessage:
    return ChatMessage(content)

def get_content(message: ChatMessage) -> str:
    return message.content
