from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Unit, Property, User
from app.schemas import UnitCreate, UnitResponse
from app.routers.auth import get_current_user, require_role  # Role-based protection

router = APIRouter()


# 🏠 Create a Unit (Only Admins)
@router.post("/create", response_model=UnitResponse)
def create_unit(
    unit_data: UnitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    # Admin should provide a property_id, otherwise, assign the first property automatically
    if not unit_data.property_id:
        property = db.query(Property).first()  # Pick the first available property
        if not property:
            raise HTTPException(status_code=404, detail="No available property")
    else:
        property = db.query(Property).filter(Property.id == unit_data.property_id).first()

    # Create the unit with the correct property_id
    new_unit = Unit(
        name=unit_data.name,
        status=unit_data.status,
        property_id=property.id  # Automatically assign the correct property_id
    )
    db.add(new_unit)
    db.commit()
    db.refresh(new_unit)
    return new_unit


# 📋 Get All Units (Admins see all, Tenants see their own)
@router.get("/", response_model=List[UnitResponse])
def get_units(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "Admin":
        return db.query(Unit).all()
    return db.query(Unit).filter(Unit.property_id == current_user.id).all()  # For Tenant, filter based on property they are linked to


# 🔍 Get Single Unit (Only Admins or the Tenant)
@router.get("/{unit_id}", response_model=UnitResponse)
def get_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    if current_user.role == "Tenant" and unit.property_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this unit")
    return unit


# ✏️ Update Unit (Only Admins or the Tenant)
@router.put("/{unit_id}", response_model=UnitResponse)
def update_unit(
    unit_id: int,
    unit_data: UnitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    if current_user.role == "Tenant" and unit.property_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this unit")
    
    unit.name = unit_data.name or unit.name
    unit.status = unit_data.status or unit.status
    db.commit()
    db.refresh(unit)
    return unit


# ❌ Delete Unit (Only Admins)
@router.delete("/{unit_id}")
def delete_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    db.delete(unit)
    db.commit()
    return {"message": "Unit deleted successfully"}
