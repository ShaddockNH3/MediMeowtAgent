import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add current directory to path to find app module if needed, 
# but for simple SQL we might just use the database URL directly if known.
# Assuming sqlite based on file list or common patterns, but let's check config/env.
# Actually, I can use app.database.

sys.path.append(os.getcwd())
try:
    from app.database import SessionLocal
    from app.models.user import User
    
    db = SessionLocal()
    users = db.query(User).all()
    
    print(f"{'Username':<20} | {'Gender':<10} | {'Birth':<20}")
    print("-" * 50)
    for u in users:
        print(f"{u.username or 'None':<20} | {u.gender or 'None':<10} | {u.birth or 'None':<20}")
        
    db.close()
except Exception as e:
    print(f"Error: {e}")
