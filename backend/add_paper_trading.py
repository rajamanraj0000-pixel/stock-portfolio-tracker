from sqlalchemy import create_engine, text
from app.database import DATABASE_URL
from app.models import PaperTrade
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

print("Dropping old paper_trades table if exists...")
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS paper_trades CASCADE"))
    conn.commit()
    print("Old table dropped!")

print("Creating paper_trades table...")
PaperTrade.__table__.create(engine, checkfirst=True)
print("✅ Paper trades table created successfully!")