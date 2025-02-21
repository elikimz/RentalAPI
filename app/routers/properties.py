from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Property, User
from app.schemas import PropertyCreate, PropertyResponse
from app.routers.auth import get_current_user, require_role  # Import role protection

router = APIRouter()


# 🏠 Create Property (Only Landlords)
@router.post("/", response_model=PropertyResponse)
def create_property(
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Landlord,Admin"]))
):
    new_property = Property(
        name=property_data.name,
        location=property_data.location,
        landlord_id=current_user.id  # Assign to logged-in landlord
    )
    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    return new_property


# 📋 Get All Properties (Admins see all, Landlords see their own)
@router.get("/", response_model=List[PropertyResponse])
def get_properties(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "Admin":
        return db.query(Property).all()  # Admins get all properties
    return db.query(Property).filter(Property.landlord_id == current_user.id).all()  # Landlords get their own


# 🔍 Get Single Property (Only Admins or the Owner)
@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")

    if current_user.role != "Admin" and property.landlord_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this property")

    return property


# ✏️ Update Property (Only Landlords Who Own the Property)
@router.put("/{property_id}", response_model=PropertyResponse)
def update_property(
    property_id: int,
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Landlord"]))
):
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")

    if property.landlord_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this property")

    property.name = property_data.name or property.name
    property.location = property_data.location or property.location

    db.commit()
    db.refresh(property)
    return property


# ❌ Delete Property (Only Landlords Who Own the Property)
@router.delete("/{property_id}")
def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Landlord"]))
):
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")

    if property.landlord_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this property")

    db.delete(property)
    db.commit()
    return {"message": "Property deleted successfully"}
