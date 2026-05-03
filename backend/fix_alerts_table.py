from sqlalchemy import create_engine, text
from app.database import DATABASE_URL
from app.models import Alert
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

print("Dropping old alerts table...")
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS alerts CASCADE"))
    conn.commit()
    print("Old table dropped!")

print("Creating new alerts table with correct structure...")
Alert.__table__.create(engine, checkfirst=True)
print("✅ Alerts table created successfully with all columns!")