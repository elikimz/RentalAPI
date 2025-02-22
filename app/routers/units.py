from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Unit, Property, User
from app.schemas import UnitCreate, UnitResponse
from app.routers.auth import get_current_user, require_role  # Role-based protection

router = APIRouter()





