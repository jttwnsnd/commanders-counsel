from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, cast
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy import String
from app.models.card import Card

async def search_relevant_cards(query: str, db: AsyncSession, limit: int = 8) -> list[Card]:
    query_lower = query.lower()

    color_map = {"red": "R", "blue": "U", "black": "B", "green": "G", "white": "W"}
    detected_colors = [v for k, v in color_map.items() if k in query_lower]

    type_keywords = ["instant", "sorcery", "creature", "enchantment", "artifact", "planeswalker"]
    detected_types = [t for t in type_keywords if t in query_lower]

    text_keywords = [
        w for w in query_lower.split()
        if len(w) > 3
        and w not in color_map
        and w not in type_keywords
    ]

    query_stmt = select(Card).where(Card.legality_commander == "legal")

    if detected_colors:
        color_filters = [Card.color_identity.any_() == color for color in detected_colors]
        query_stmt = query_stmt.where(or_(*color_filters))

    if detected_types:
        type_filters = [Card.type_line.ilike(f"%{t}%") for t in detected_types]
        query_stmt = query_stmt.where(or_(*type_filters))

    if text_keywords:
        text_filters = [Card.oracle_text.ilike(f"%{kw}%") for kw in text_keywords[:3]]
        query_stmt = query_stmt.where(or_(*text_filters))

    result = await db.execute(query_stmt.limit(limit))
    cards = result.scalars().all()
    
    print(f"DEBUG - found {len(cards)} cards: {[c.name for c in cards]}")
    
    return cards

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

