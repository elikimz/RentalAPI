from fastapi import FastAPI
from app.database import engine, Base
import app.models  # Ensure all models are imported
from app.routers import auth, user,properties,units,tenant,lease,payments

# ✅ Create tables
Base.metadata.create_all(bind=engine)

# ✅ Initialize FastAPI app
app = FastAPI()

# ✅ Include Routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(properties.router, prefix="/properties", tags=["Properties"])
app.include_router(units.router, prefix="/units", tags=["Units"])
app.include_router(tenant.router, prefix="/tenant", tags=["Tenants"])
app.include_router(lease.router, prefix="/leases", tags=["Lease"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])

@app.get("/")
def home():
    return {"message": "Property Management API is running"}
