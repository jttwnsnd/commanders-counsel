import anthropic
from app.core.config import settings

client = anthropic.Client(settings.ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are Commander's Counsel, an expert Magic: The Gathering assistant 
specializing in Commander and Oathbreaker formats. You help players with deck building, 
card suggestions, and rules interactions.

When relevant card data is provided, use it to ground your answers in accurate card text.
Always clarify legality for Commander and Oathbreaker formats when relevant.
Be concise but thorough. If you're unsure about a ruling, say so."""

def build_messages(history: list[dict], user_message: str, card_context: str) -> list[dict]:
    messages = history.copy()
    content = user_message
    if card_context:
        content = f"Relevant cards from the database: \n\n{card_context}\n\nUser question: {user_message}"
    messages.append({"role": "user", "content": content})
    return messages

async def stream_chat_response(messages: list[dict]):
    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages
    ) as stream:
        for text in stream.text_stream:
            yield text