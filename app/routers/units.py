

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Property, Unit, User, Lease
from app.schemas import UnitCreate, UnitResponse
from app.routers.auth import get_current_user

router = APIRouter()


# Create a Unit (Admin or Tenant)
@router.post("/", response_model=UnitResponse)
def create_unit(
    unit: UnitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "Admin":
        # Admin can create a unit for any of their properties
        property = db.query(Property).filter(Property.admin_id == current_user.id).first()
        if not property:
            raise HTTPException(status_code=404, detail="No property found for the admin")
    else:
        # Tenant can only create a unit in the property they are leasing
        lease = db.query(Lease).filter(Lease.tenant_id == current_user.id).first()
        if not lease:
            raise HTTPException(status_code=403, detail="Tenants can only create units in their leased property")
        property = lease.unit.property

    new_unit = Unit(
        name=unit.name,
        status=unit.status,
        property_id=property.id
    )

    db.add(new_unit)
    db.commit()
    db.refresh(new_unit)
    return new_unit


# Get All Units (Protected)
@router.get("/", response_model=List[UnitResponse])
async def get_units(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return db.query(Unit).all()


# Get Unit by ID (Protected)
@router.get("/{unit_id}", response_model=UnitResponse)
async def get_unit(unit_id: int, db: Session = Depends(get_db)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit


# Update Unit (Admin only)
@router.put("/{unit_id}", response_model=UnitResponse)
async def update_unit(
    unit_id: int,
    unit_data: UnitCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Only admins can update units")

    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    for key, value in unit_data.dict().items():
        setattr(unit, key, value)
    db.commit()
    db.refresh(unit)
    return unit


# Delete Unit (Admin only)
@router.delete("/{unit_id}")
async def delete_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Only admins can delete units")
    
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    db.delete(unit)
    db.commit()
    return {"message": "Unit deleted successfully"}


# Let me know if you want me to tweak anything! 🚀
