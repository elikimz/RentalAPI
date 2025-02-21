from fastapi import FastAPI
from app.database import engine, Base
import app.models  # Ensure all models are imported
from app.routers import auth, user

# ✅ Create tables
Base.metadata.create_all(bind=engine)

# ✅ Initialize FastAPI app
app = FastAPI()

# ✅ Include Routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(user.router, prefix="/users", tags=["Users"])

@app.get("/")
def home():
    return {"message": "Property Management API is running"}
