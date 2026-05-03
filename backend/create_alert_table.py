from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, MetaData, Table
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define Alert table
alerts = Table(
    'alerts',
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('user_id', Integer),
    Column('symbol', String, index=True),
    Column('alert_type', String),
    Column('target_value', Float),
    Column('current_value', Float, nullable=True),
    Column('is_active', Boolean, default=True),
    Column('is_triggered', Boolean, default=False),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('triggered_at', DateTime, nullable=True)
)

# Create table
print("Creating alerts table...")
metadata.create_all(engine)
print("Alerts table created successfully!")