import stripe
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Payment, Lease, Tenant
from app.schemas import PaymentCreate
from app.routers.auth import get_current_user
from app.config import STRIPE_SECRET_KEY

# Initialize Stripe with the secret key
stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter()

# 🏦 Create a Payment with Stripe Checkout
@router.post("/pay")
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: Tenant = Depends(get_current_user)
):
    # Find the lease linked to the tenant (no need for lease_id in the request)
    lease = db.query(Lease).filter(Lease.tenant_id == current_user.id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found for this tenant")

    # Default the amount paid to the lease's rent amount if amount_paid is not specified
    amount_due = lease.rent_amount  # Assuming rent_amount is part of the Lease model
    amount_paid = payment_data.amount_paid if payment_data.amount_paid != 0 else amount_due

    # Create Stripe Checkout Session
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],  # Specifies card payments
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",  # Ensure the currency is correctly set
                        "product_data": {
                            "name": f"Rent for lease {lease.id}",  # A descriptive name for the charge
                        },
                        "unit_amount": int(amount_paid * 100),  # Amount in cents
                    },
                    "quantity": 1,  # Quantity is always 1 for a single payment
                }
            ],
            mode="payment",  # Use "payment" mode for one-time payments
            success_url="https://your-website.com/success?session_id={CHECKOUT_SESSION_ID}",  # Update with your success URL
            cancel_url="https://your-website.com/cancel",  # Update with your cancel URL
            metadata={"lease_id": lease.id},  # Pass lease info in metadata
        )

        # Create payment record in the database
        payment = Payment(
            tenant_id=current_user.id,
            lease_id=lease.id,
            amount_paid=amount_paid,
            payment_status="pending",
            stripe_payment_intent_id=checkout_session.id
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        return {"checkout_url": checkout_session.url, "payment_id": payment.id}

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {e.user_message}")
