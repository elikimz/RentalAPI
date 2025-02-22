# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import List

# from app.database import get_db
# from app.models import Property, User
# from app.schemas import PropertyCreate, PropertyResponse
# from app.routers.auth import get_current_user, require_role  # Import role protection

# router = APIRouter()

# # 🏠 Create Property (Admins only)
# @router.post("/", response_model=PropertyResponse)
# def create_property(
#     property_data: PropertyCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(require_role(["Admin"]))  # Only Admin can create properties
# ):
#     new_property = Property(
#         name=property_data.name,
#         location=property_data.location,
#         admin_id=current_user.id  # Automatically assign the logged-in user (admin) as the property owner
#     )
    
#     db.add(new_property)
#     db.commit()
#     db.refresh(new_property)
#     return new_property


# # 📋 Get All Properties (Admins see all, Tenants see their own rented properties)
# @router.get("/", response_model=List[PropertyResponse])
# def get_properties(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)  # Ensure user is authenticated
# ):
#     if current_user.role == "Admin":
#         return db.query(Property).all()  # Admins get all properties
    
#     # For Tenants, fetch only properties they are renting (assuming there is a relationship)
#     return db.query(Property).join(User).filter(User.id == current_user.id).all()  # Assuming a tenant-property relationship


# # 🔍 Get Single Property (Admins or Tenants who are renting the property)
# @router.get("/{property_id}", response_model=PropertyResponse)
# def get_property(
#     property_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)  # Ensure user is authenticated
# ):
#     property = db.query(Property).filter(Property.id == property_id).first()
#     if not property:
#         raise HTTPException(status_code=404, detail="Property not found")

#     # Admins can view any property, tenants can only view properties they are renting
#     if current_user.role == "Admin" or current_user.id == property.admin_id:
#         return property  # Admins and landlords can view

#     # If the user is a tenant, check if they are renting the property
#     if current_user.role == "Tenant" and current_user.id == property.admin_id:
#         return property  # Tenants can view only their rented property
#     else:
#         raise HTTPException(status_code=403, detail="Not authorized to view this property")


# # ✏️ Update Property (Admins only)
# @router.put("/{property_id}", response_model=PropertyResponse)
# def update_property(
#     property_id: int,
#     property_data: PropertyCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(require_role(["Admin"]))  # Only Admin can update properties
# ):
#     property = db.query(Property).filter(Property.id == property_id).first()
#     if not property:
#         raise HTTPException(status_code=404, detail="Property not found")

#     # Admins can update any property
#     if current_user.role == "Admin":
#         property.name = property_data.name or property.name
#         property.location = property_data.location or property.location

#         db.commit()
#         db.refresh(property)
#         return property
#     else:
#         raise HTTPException(status_code=403, detail="Not authorized to update this property")


# # ❌ Delete Property (Admins only)
# @router.delete("/{property_id}")
# def delete_property(
#     property_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(require_role(["Admin"]))  # Only Admin can delete properties
# ):
#     property = db.query(Property).filter(Property.id == property_id).first()
#     if not property:
#         raise HTTPException(status_code=404, detail="Property not found")

#     # Admins can delete any property
#     if current_user.role == "Admin":
#         db.delete(property)
#         db.commit()
#         return {"message": "Property deleted successfully"}
#     else:
#         raise HTTPException(status_code=403, detail="Not authorized to delete this property")



from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Property, User
from app.schemas import PropertyCreate, PropertyResponse
from app.routers.auth import get_current_user, require_role

router = APIRouter()

# 🏠 Create Property (Admins only)
@router.post("/", response_model=PropertyResponse)
def create_property(
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    new_property = Property(
        name=property_data.name,
        location=property_data.location,
        description=property_data.description or "",  # Handle null descriptions
        admin_id=current_user.id
    )
    
    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    return new_property


# 📋 Get All Properties
@router.get("/", response_model=List[PropertyResponse])
def get_properties(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    properties = db.query(Property).all()
    
    for prop in properties:
        prop.description = prop.description or ""
    
    return properties


# 🔍 Get Single Property
@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")

    if current_user.role == "Admin" or current_user.id == property.admin_id:
        property.description = property.description or ""
        return property

    if current_user.role == "Tenant" and current_user.id == property.admin_id:
        property.description = property.description or ""
        return property
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view this property")


# ✏️ Update Property
@router.put("/{property_id}", response_model=PropertyResponse)
def update_property(
    property_id: int,
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")

    if current_user.role == "Admin":
        property.name = property_data.name or property.name
        property.location = property_data.location or property.location
        property.description = property_data.description or property.description or ""

        db.commit()
        db.refresh(property)
        return property
    else:
        raise HTTPException(status_code=403, detail="Not authorized to update this property")


# ❌ Delete Property
@router.delete("/{property_id}")
def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")

    if current_user.role == "Admin":
        db.delete(property)
        db.commit()
        return {"message": "Property deleted successfully"}
    else:
        raise HTTPException(status_code=403, detail="Not authorized to delete this property")
