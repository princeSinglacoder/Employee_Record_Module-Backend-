from app.config import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")).fetchall()
    tables = [r[0] for r in result]
    print("Existing tables:", tables)