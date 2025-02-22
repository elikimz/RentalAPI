from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Property, Unit, User
from app.schemas import UnitCreate, UnitResponse
from app.routers.auth import get_current_user, require_role

router = APIRouter()


# Create a Unit (Admin only)
# Create a Unit
@router.post("/units", response_model=UnitResponse)
def create_unit(
    unit: UnitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch the property linked to the current user
    property = db.query(Property).filter(Property.id == current_user.id).first()
    if not property:
        raise HTTPException(status_code=404, detail="No property found for the current user")

    new_unit = Unit(
        name=unit.name,
        status=unit.status,
        property_id=property.id  # Assign the property ID automatically
    )

    db.add(new_unit)
    db.commit()
    db.refresh(new_unit)
    return new_unit



# Get All Units (Protected)
@router.get("/units", response_model=List[UnitResponse])
async def get_units(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return db.query(Unit).all()


# Get Unit by ID (Protected)
@router.get("/units/{unit_id}", response_model=UnitResponse)
async def get_unit(unit_id: int, db: Session = Depends(get_db)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit


# Update Unit (Admin only)
@router.put("/units/{unit_id}", response_model=UnitResponse)
async def update_unit(
    unit_id: int,
    unit_data: UnitCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["Admin"]))
):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    for key, value in unit_data.dict().items():
        setattr(unit, key, value)
    db.commit()
    db.refresh(unit)
    return unit


# Delete Unit (Admin only)
@router.delete("/units/{unit_id}")
async def delete_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["Admin"]))
):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    db.delete(unit)
    db.commit()
    return {"message": "Unit deleted successfully"}


# Let me know if you want any adjustments or more features! 🚀
