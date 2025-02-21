from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User
from app.schemas import UserResponse, UserUpdate
from app.routers.auth import get_current_user, require_role

router = APIRouter()

# 🛡️ Get All Users (Only Admins)
@router.get("/", response_model=List[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin"))  # ✅ Only Admins
):
    return db.query(User).all()

# 🔍 Get Single User by ID (Admin or the user themselves)
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.role != "Admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return user

# ✏️ Update User (Admin or the user themselves)
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.role != "Admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if current_user.role != "Admin" and user_data.role:
        raise HTTPException(status_code=403, detail="You cannot change your own role")
    
    if current_user.role != "Admin" and user_data.is_active is not None:
        raise HTTPException(status_code=403, detail="You cannot deactivate yourself")

    user.full_name = user_data.full_name or user.full_name
    if current_user.role == "Admin":
        user.role = user_data.role or user.role
        user.is_active = user_data.is_active if user_data.is_active is not None else user.is_active

    db.commit()
    db.refresh(user)
    return user

# ❌ Delete User (Only Admins)
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin"))  # ✅ Only Admins
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id == user_id:
        raise HTTPException(status_code=403, detail="You cannot delete yourself!")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
