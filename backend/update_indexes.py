from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

indexes = [
    "CREATE INDEX IF NOT EXISTS idx_txn_portfolio ON transactions(portfolio_id)",
    "CREATE INDEX IF NOT EXISTS idx_txn_symbol ON transactions(symbol)",
    "CREATE INDEX IF NOT EXISTS idx_txn_date ON transactions(transaction_date)",
    "CREATE INDEX IF NOT EXISTS idx_txn_portfolio_symbol ON transactions(portfolio_id, symbol)",
    "CREATE INDEX IF NOT EXISTS idx_alert_user ON alerts(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_alert_active ON alerts(is_active, is_triggered)",
    "CREATE INDEX IF NOT EXISTS idx_alert_user_active ON alerts(user_id, is_active)",
    "CREATE INDEX IF NOT EXISTS idx_paper_user ON paper_trades(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_paper_date ON paper_trades(trade_date)",
    "CREATE INDEX IF NOT EXISTS idx_paper_user_symbol ON paper_trades(user_id, symbol)",
    "CREATE INDEX IF NOT EXISTS idx_watchlist_user ON watchlists(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_watchlist_user_symbol ON watchlists(user_id, symbol)",
    "CREATE INDEX IF NOT EXISTS idx_portfolio_user ON portfolios(user_id)",
]

print("Creating database indexes...")

with engine.connect() as conn:
    for idx_sql in indexes:
        try:
            conn.execute(text(idx_sql))
            print(f"  ✅ {idx_sql.split('idx_')[1].split(' ON')[0]}")
        except Exception as e:
            print(f"  ⚠️ Skipped: {e}")
    
    conn.commit()

print("\n✅ All database indexes created successfully!")