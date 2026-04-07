from sqlalchemy import Column, String, Float, ARRAY, Text
from app.db.database import Base

class Card(Base):
    __tablename__ = "cards"

    id = Column(String, primary_key=True, index=True)
    oracle_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    mana_cost = Column(String, nullable=True)
    cmc = Column(Float, nullable=True)
    type_line = Column(String, nullable=False)
    oracle_text = Column(Text, nullable=True)
    colors = Column(ARRAY(String))
    color_identity = Column(ARRAY(String))
    keywords = Column(ARRAY(String))
    legality_commander = Column(String, nullable=True)
    legality_oathbreaker = Column(String, nullable=True)
    image_uri_normal = Column(String, nullable=True)
    flavor_text = Column(Text, nullable=True)
    rulings_uri = Column(String, nullable=True)