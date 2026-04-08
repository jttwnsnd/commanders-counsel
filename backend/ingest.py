import asyncio
from app.db.database import AsyncSessionLocal
from app.services.scryfall import download_oracle_cards_json, load_oracle_cards_into_db

async def main():
    print("Downloading Oracle Cards from Scryfall...")
    await download_oracle_cards_json()
    print("Download complete. Loading cards into database...")
    async with AsyncSessionLocal() as session:
        await load_oracle_cards_into_db(session)

if(__name__ == "__main__"):
    asyncio.run(main())