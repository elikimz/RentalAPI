from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Lease, Tenant, Unit, User
from app.schemas import LeaseCreate, LeaseResponse
from app.routers.auth import get_current_user, require_role

router = APIRouter()

# 🏠 Create a Lease (Only Admins can create leases)
@router.post("/leases", response_model=LeaseResponse)
def create_lease(
    lease_data: LeaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find tenant (implicitly associated with the logged-in user)
    tenant = db.query(Tenant).filter(Tenant.user_id == current_user.id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Automatically assign the first available unit to the lease
    unit = db.query(Unit).first()
    if not unit:
        raise HTTPException(status_code=404, detail="No available unit")

    # Create the lease
    new_lease = Lease(
        tenant_id=tenant.id,
        unit_id=unit.id,
        start_date=lease_data.start_date,
        end_date=lease_data.end_date,
        rent_amount=lease_data.rent_amount,
        deposit_amount=lease_data.deposit_amount
    )

    db.add(new_lease)
    db.commit()
    db.refresh(new_lease)
    return new_lease


# 📋 Get All Leases (Admins see all, Tenants see their own)
@router.get("/leases", response_model=List[LeaseResponse])
def get_leases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "Admin":
        return db.query(Lease).all()
    tenant = db.query(Tenant).filter(Tenant.user_id == current_user.id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return db.query(Lease).filter(Lease.tenant_id == tenant.id).all()


# 🔍 Get Single Lease (Only Admins or the Tenant)
@router.get("/leases/{lease_id}", response_model=LeaseResponse)
def get_lease(
    lease_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lease = db.query(Lease).filter(Lease.id == lease_id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    if current_user.role == "Tenant" and lease.tenant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this lease")
    return lease


# ✏️ Update Lease (Only Admins or the Tenant)
@router.put("/leases/{lease_id}", response_model=LeaseResponse)
def update_lease(
    lease_id: int,
    lease_data: LeaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lease = db.query(Lease).filter(Lease.id == lease_id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    
    # Only Admins or the Tenant who owns the lease can update it
    if current_user.role == "Tenant" and lease.tenant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this lease")
    
    # Update lease details
    lease.start_date = lease_data.start_date or lease.start_date
    lease.end_date = lease_data.end_date or lease.end_date
    lease.rent_amount = lease_data.rent_amount or lease.rent_amount
    lease.deposit_amount = lease_data.deposit_amount or lease.deposit_amount

    db.commit()
    db.refresh(lease)
    return lease


# ❌ Delete Lease (Only Admins)
@router.delete("/leases/{lease_id}")
def delete_lease(
    lease_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lease = db.query(Lease).filter(Lease.id == lease_id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")

    # Only Admin can delete leases
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this lease")
    
    db.delete(lease)
    db.commit()
    return {"message": "Lease deleted successfully"}
