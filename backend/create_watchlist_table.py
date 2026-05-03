from sqlalchemy import create_engine, text
from app.database import DATABASE_URL
from app.models import Watchlist
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

print("Dropping old watchlists table if exists...")

with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS watchlists CASCADE"))
    conn.commit()

print("Old watchlists table dropped.")

print("Creating new watchlists table with correct structure...")
Watchlist.__table__.create(engine, checkfirst=True)

print("✅ Watchlists table created successfully!")