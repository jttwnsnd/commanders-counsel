from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.card import Card

# RAG (Retrieval-Augmented Generation) service for fetching relevant card data based on user queries
# This helps prevent hallucinations by grounding the AI's responses in actual card data from the database

async def search_relevant_cards(query: str, db: AsyncSession, limit: int = 5) -> list[Card]:
    result = await db.execute(
        select(Card).where(
            Card.oracle_text.ilike(f"%{query}%") |
            Card.name.ilike(f"%{query}%") |
            Card.type.ilike(f"%{query}%")
        ).limit(limit)
    )
    return result.scalars().all()

def format_cards_for_prompt(cards: list[Card]) -> str:
    if not cards:
        return "No relevant cards found."
    formatted = []
    for card in cards:
        formatted.append(
            f"Name: {card.name}\n"
            f"Mana Cost: {card.mana_cost}\n"
            f"Type: {card.type_line}\n"
            f"Text: {card.oracle_text}\n"
            f"Colors: {', '.join(card.colors) if card.colors else 'Colorless'}\n"
            f"Commander Legal: {card.legality_commander}\n"
            f"Oathbreaker Legal: {card.legality_oathbreaker}\n"
        )
    return "\n---\n".join(formatted)

