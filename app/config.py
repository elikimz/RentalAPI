import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET= os.getenv("STRIPE_PUBLIC_KEY")
class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))



    
  
   


    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")

# Create a settings instance
settings = Settings()




