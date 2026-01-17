from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os 

# Ensure data folder exists inside container
DB_DIR = "/app/data"
os.makedirs(DB_DIR, exist_ok=True)

# SQLite URL pointing inside container
DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'terroir.db')}"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()