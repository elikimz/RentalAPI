
import stripe
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Payment, Lease, Tenant, User
from app.schemas import PaymentCreate, PaymentUpdate, PaymentResponse
from app.routers.auth import get_current_user
from app.config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
from typing import List, Optional

# Initialize Stripe
stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter()

# 🏦 Create a Payment with Stripe Checkout
@router.post("/pay", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tenant = db.query(Tenant).filter(Tenant.user_id == current_user.id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found for the logged-in user.")
    
    lease = db.query(Lease).filter(Lease.tenant_id == tenant.id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found for the tenant.")

    amount_paid = payment_data.amount_paid or lease.rent_amount

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": f"Rent for lease {lease.id}"},
                        "unit_amount": int(amount_paid * 100),
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="https://rental-eta-lake.vercel.app/success?session_id={CHECKOUT_SESSION_ID}",
            # success_url="https://rental-eta-lake.vercel.app/success",
            cancel_url="https://rental-eta-lake.vercel.app/cancel",
            metadata={"lease_id": lease.id, "tenant_id": tenant.id},
        )

        payment = Payment(
            tenant_id=tenant.id,
            lease_id=lease.id,
            amount_paid=float(amount_paid),
            payment_status="pending",
            stripe_payment_intent_id=checkout_session.id
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        return PaymentResponse(
            checkout_url=checkout_session.url,
            payment_id=str(payment.id),
            amount_paid=payment.amount_paid,
            payment_status=payment.payment_status
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {e.user_message}")


# 🧾 Webhook to Handle Stripe Payment Confirmation
@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook event")

    session = event['data']['object']
    payment = db.query(Payment).filter_by(stripe_payment_intent_id=session['id']).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if event['type'] == 'checkout.session.completed':
        payment.payment_status = 'succeeded'
    elif event['type'] == 'payment_intent.payment_failed':
        payment.payment_status = 'failed'
    
    db.commit()
    return {"status": "success"}


# 💜 Get All Payments (Admin Only)
@router.get("/", response_model=List[PaymentResponse])
async def get_all_payments(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if current_user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    payments = db.query(Payment).all()
    
    payment_responses = []
    for payment in payments:
        payment_responses.append(
            PaymentResponse(
                payment_id=str(payment.id),
                amount_paid=float(payment.amount_paid),
                payment_status=payment.payment_status,
                checkout_url=f"https://checkout.stripe.com/pay/{payment.stripe_payment_intent_id}" if payment.stripe_payment_intent_id else ""
            )
        )
    return payment_responses


@router.get("/payments/verify")
async def verify_payment(session_id: str, db: Session = Depends(get_db)):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        payment = db.query(Payment).filter_by(stripe_payment_intent_id=session_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        return {"status": session.payment_status}
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {e.user_message}")


# 💜 Get Payment by ID (Admin & Tenant)
@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if current_user.role.lower() != "admin" and payment.tenant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return PaymentResponse(
        payment_id=str(payment.id),
        amount_paid=float(payment.amount_paid),
        payment_status=payment.payment_status,
        checkout_url=f"https://checkout.stripe.com/pay/{payment.stripe_payment_intent_id}" if payment.stripe_payment_intent_id else ""
    )


# 🔄 Update Payment (Admin Only)
@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: int, 
    updated_payment: PaymentUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if current_user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment.amount_paid = updated_payment.amount_paid or payment.amount_paid
    payment.payment_status = updated_payment.payment_status or payment.payment_status
    
    db.commit()
    db.refresh(payment)
    return PaymentResponse(
        payment_id=str(payment.id),
        amount_paid=float(payment.amount_paid),
        payment_status=payment.payment_status,
        checkout_url=f"https://checkout.stripe.com/pay/{payment.stripe_payment_intent_id}" if payment.stripe_payment_intent_id else ""
    )


# ❌ Delete Payment (Admin Only)
@router.delete("/{payment_id}")
async def delete_payment(
    payment_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if current_user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    db.delete(payment)
    db.commit()
    return {"detail": "Payment deleted successfully"}
