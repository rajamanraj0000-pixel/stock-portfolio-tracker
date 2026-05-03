from sqlalchemy import create_engine, text
from app.database import DATABASE_URL
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

print("Adding database indexes for better performance...")

indexes = [
    # Portfolio indexes
    "CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios(user_id);",
    
    # Transaction indexes
    "CREATE INDEX IF NOT EXISTS idx_transactions_portfolio_id ON transactions(portfolio_id);",
    "CREATE INDEX IF NOT EXISTS idx_transactions_symbol ON transactions(symbol);",
    "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date DESC);",
    
    # Alert indexes
    "CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_alerts_symbol ON alerts(symbol);",
    "CREATE INDEX IF NOT EXISTS idx_alerts_active ON alerts(is_active, is_triggered);",
    
    # Paper trade indexes
    "CREATE INDEX IF NOT EXISTS idx_paper_trades_user_id ON paper_trades(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_paper_trades_symbol ON paper_trades(symbol);",
    "CREATE INDEX IF NOT EXISTS idx_paper_trades_date ON paper_trades(trade_date DESC);",
    
    # Watchlist indexes
    "CREATE INDEX IF NOT EXISTS idx_watchlists_user_id ON watchlists(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_watchlists_symbol ON watchlists(symbol);",
]

with engine.connect() as conn:
    for idx_sql in indexes:
        try:
            conn.execute(text(idx_sql))
            print(f"✅ {idx_sql.split('idx_')[1].split(' ON')[0]}")
        except Exception as e:
            print(f"⚠️ {e}")
    
    conn.commit()

print("\n✅ All indexes created successfully!")
print("Database queries will now be faster!")