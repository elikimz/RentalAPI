from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

DATABASE_URL = os.getenv("DATABASE_URL")  # Load from .env

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ✅ Ensure this function exists!
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
