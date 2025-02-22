from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Unit
from app.schemas import UnitCreate, UnitResponse
from app.routers.auth import get_current_user, require_role

router = APIRouter()

# Create a Unit
@router.post("/units/create", response_model=UnitResponse)
async def create_unit(
    unit_data: UnitCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["Admin"]))
):
    new_unit = Unit(**unit_data.dict())
    db.add(new_unit)
    db.commit()
    db.refresh(new_unit)
    return new_unit


# Get All Units
@router.get("/units", response_model=List[UnitResponse])
async def get_units(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return db.query(Unit).all()


# Get Unit by ID
@router.get("/units/{unit_id}", response_model=UnitResponse)
async def get_unit(unit_id: int, db: Session = Depends(get_db)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit


# Update Unit
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


# Delete Unit
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


