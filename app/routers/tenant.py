from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Unit, User, Tenant, Property, Lease
from app.schemas import TenantCreate, TenantResponse, LeaseCreate, LeaseResponse
from app.routers.auth import get_current_user, require_role  # Automatically fetch current logged-in user

router = APIRouter()

# 🏠 Register Tenant (Automatically creating tenant from user)
@router.post("/register", response_model=TenantResponse)
def register_tenant(
    tenant_data: TenantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Automatically get the logged-in user
):
    # Check if the logged-in user is already a tenant
    existing_tenant = db.query(Tenant).filter(Tenant.user_id == current_user.id).first()
    if existing_tenant:
        raise HTTPException(status_code=400, detail="User is already a tenant")

    # Create new tenant and associate it with the logged-in user
    new_tenant = Tenant(
        user_id=current_user.id,  # Automatically associate with the logged-in user
        full_name=tenant_data.full_name,
        email=tenant_data.email,
        phone_number=tenant_data.phone_number
    )

    db.add(new_tenant)
    db.commit()
    db.refresh(new_tenant)
    
    return new_tenant


# 📋 Get All Tenants (Admins see all, Tenants see their own details)
@router.get("/", response_model=List[TenantResponse])
def get_tenants(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Tenant"]))  # Protect by role
):
    if current_user.role == "Admin":
        # Admin can view all tenants
        return db.query(Tenant).all()
    else:
        # Tenants can view only their own details
        tenant = db.query(Tenant).filter(Tenant.user_id == current_user.id).first()
        return [tenant] if tenant else []


# 🔍 Get Single Tenant (Only Admins or the Tenant themselves)
@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Tenant"]))  # Protect by role
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if current_user.role == "Tenant" and tenant.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view your own tenant")

    return tenant


# ✏️ Update Tenant Details (Admins and the tenant themselves)
@router.put("/{tenant_id}", response_model=TenantResponse)
def update_tenant(
    tenant_id: int,
    tenant_data: TenantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Tenant"]))  # Protect by role
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if current_user.role != "Admin" and tenant.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own tenant")
    
    tenant.full_name = tenant_data.full_name
    tenant.email = tenant_data.email
    tenant.phone_number = tenant_data.phone_number
    db.commit()
    db.refresh(tenant)
    return tenant


# ❌ Delete Tenant (Only Admins)
@router.delete("/{tenant_id}")
def delete_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))  # Only Admin can delete
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    db.delete(tenant)
    db.commit()
    return {"message": "Tenant deleted successfully"}


# # 📝 Create Lease (Link Tenant to Unit)
# @router.post("/leases", response_model=LeaseResponse)
# def create_lease(
#     lease_data: LeaseCreate,
#     db: Session = Depends(get_db)
# ):
#     tenant = db.query(Tenant).filter(Tenant.id == lease_data.tenant_id).first()
#     if not tenant:
#         raise HTTPException(status_code=404, detail="Tenant not found")

#     unit = db.query(Unit).filter(Unit.id == lease_data.unit_id).first()
#     if not unit:
#         raise HTTPException(status_code=404, detail="Unit not found")

#     # Create lease
#     new_lease = Lease(
#         tenant_id=tenant.id,
#         unit_id=unit.id,
#         start_date=lease_data.start_date,
#         end_date=lease_data.end_date
#     )
#     db.add(new_lease)
#     db.commit()
#     db.refresh(new_lease)
#     return new_lease
