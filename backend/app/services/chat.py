from groq import Groq
# import anthropic
from app.core.config import settings

# client = anthropic.Client(settings.ANTHROPIC_API_KEY)
client = Groq(api_key=settings.GROQ_API_KEY)

SYSTEM_PROMPT = """You are Commander's Counsel, an expert Magic: The Gathering assistant 
specializing in Commander and Oathbreaker formats.

When starting a new conversation, guide the user through these steps:
1. Ask what format they are playing (Commander or Oathbreaker)
2. Ask for their Commander name (or Oathbreaker + Signature Spell)
3. Once you have that context, help them build their deck

When deck context is provided, always use it to tailor your recommendations.
Only recommend cards that appear in the provided card database results.
If provided cards don't match the query, say so clearly and ask the user to rephrase.
Always confirm Commander and Oathbreaker legality when recommending cards.
Be concise and direct. Never hallucinate card names or details."""

def build_messages(history: list[dict], user_message: str, card_context: str, deck_context: str = "") -> list[dict]:
    messages = history.copy()
    content = ""
    
    if deck_context:
        content += f"Player's deck context:\n{deck_context}\n\n"
    
    if card_context:
        content += f"Relevant cards from database:\n\n{card_context}\n\n"
    
    content += f"User question: {user_message}"
    
    messages.append({"role": "user", "content": content})
    return messages

async def stream_chat_response(messages: list[dict]):
    # Using Anthropic's streaming API
    # with client.messages.stream(
    #     model="claude-opus-4-6",
    #     max_tokens=1024,
    #     system=SYSTEM_PROMPT,
    #     messages=messages
    # ) as stream:
    #     for text in stream.text_stream:
    #         yield text

    # Using Groq's streaming API
    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        stream=True,
        max_tokens=1024
    )
    for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            yield text