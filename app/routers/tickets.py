from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import SupportTicket, User
from app.schemas import TicketCreate, TicketResponse
from app.routers.auth import get_current_user, require_role

router = APIRouter()

# 🌼 Create Ticket (Anyone logged in can create)
@router.post("/", response_model=TicketResponse)
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_ticket = SupportTicket(
        subject=ticket_data.subject,
        description=ticket_data.description,
        status="Open",
        tenant_id=current_user.id
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket


# 🗋 Get All Tickets (Admin)
@router.get("/", response_model=List[TicketResponse])
def get_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    tickets = db.query(SupportTicket).all()
    return tickets


# 🔍 Get Tenant's Tickets
@router.get("/my-tickets", response_model=List[TicketResponse])
def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Tenant"]))
):
    tickets = db.query(SupportTicket).filter(SupportTicket.tenant_id == current_user.id).all()
    return tickets


# ✏️ Update Ticket Status (Admin)
@router.put("/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.status = status
    db.commit()
    db.refresh(ticket)
    return {"message": "Ticket status updated", "ticket": ticket}


# ❌ Delete Ticket (Admin)
@router.delete("/{ticket_id}")
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    db.delete(ticket)
    db.commit()
    return {"message": "Ticket deleted successfully"}


# Let me know if anything needs tweaking! 🚀
