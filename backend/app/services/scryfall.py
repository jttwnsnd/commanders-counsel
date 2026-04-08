import httpx
import json
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.constants import APP_VERSION
from app.models.card import Card

SCRYFALL_BULK_DATA_URL = "https://api.scryfall.com/bulk-data"

SCRYFALL_HEADERS = {
    "User-Agent": f"Commanders Counsel/{APP_VERSION}",
    "Accept": "application/json"
}

DATA_DIR = Path(__file__).parent.parent.parent / "data"

async def get_oracle_cards_download_url() -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(SCRYFALL_BULK_DATA_URL, headers=SCRYFALL_HEADERS)
        response.raise_for_status()
        data = response.json()

    oracle_cards_data = next((item for item in data["data"] if item["type"] == "oracle_cards"), None)

    if not oracle_cards_data:
        raise ValueError("Could not find oracle_cards bulk data from Scryfall")
    
    return oracle_cards_data["download_uri"]

async def download_oracle_cards_json() -> Path:
    
    download_url = await get_oracle_cards_download_url()

    async with httpx.AsyncClient() as client:
        async with client.stream("GET", download_url, headers=SCRYFALL_HEADERS) as response:
            response.raise_for_status()
            DATA_DIR.mkdir(exist_ok=True)
            file_path = DATA_DIR / "oracle_cards.json"
            with open(file_path, "wb") as f:
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    f.write(chunk)
    
    return file_path

async def load_oracle_cards_into_db(session: AsyncSession) -> None:
    with open(DATA_DIR / "oracle_cards.json", "r", encoding="utf-8") as f:
        cards_data = json.load(f)
    batch = []
    BATCH_SIZE = 500
    total = 0
    for card in cards_data:
        # double faced cards are handled different in Scryfall, so this checks for that
        if "card_faces" in card:
            dbl_card = card["card_faces"][0]
            oracle_text = dbl_card.get("oracle_text", "")
            mana_cost = dbl_card.get("mana_cost", "")
            image_uri_normal = dbl_card.get("image_uris", {}).get("normal")
        else:
            oracle_text = card.get("oracle_text", "")
            mana_cost = card.get("mana_cost", "")
            image_uri_normal = card.get("image_uris", {}).get("normal")

        card_obj = Card(
            id=card["id"],
            name=card["name"],
            oracle_id=card.get("oracle_id"),
            mana_cost=mana_cost,
            cmc=card.get("cmc"),
            type_line=card.get("type_line", ""),
            oracle_text=oracle_text,
            colors=card.get("colors", []),
            color_identity=card.get("color_identity", []),
            keywords=card.get("keywords", []),
            legality_commander=card.get("legalities", {}).get("commander"),
            legality_oathbreaker=card.get("legalities", {}).get("oathbreaker"),
            image_uri_normal=image_uri_normal,
            flavor_text=card.get("flavor_text", ""),
            rulings_uri=card.get("rulings_uri", "")
        )

        batch.append(card_obj)

        if len(batch) >= BATCH_SIZE:
            session.add_all(batch)
            await session.commit()
            total += len(batch)
            print(f"Inserted {total} cards...")
            batch = []
        
    if batch:
        session.add_all(batch)
        await session.commit()
        total += len(batch)
        print(f"DONE! Loaded {total} cards total.")
