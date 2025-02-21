# import stripe
# from fastapi import APIRouter, HTTPException, Depends, Request
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.models import Payment, Lease, Tenant
# from app.schemas import PaymentCreate
# from app.routers.auth import get_current_user
# from app.config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET

# # Initialize Stripe with the secret key
# stripe.api_key = STRIPE_SECRET_KEY

# router = APIRouter()

# # 🏦 Create a Payment with Stripe Checkout
# @router.post("/pay")
# async def create_payment(
#     payment_data: PaymentCreate,
#     db: Session = Depends(get_db),
#     current_user: Tenant = Depends(get_current_user)
# ):
#     # Find the lease linked to the tenant (no need for lease_id in the request)
#     lease = db.query(Lease).filter(Lease.tenant_id == current_user.id).first()
#     print(lease)
#     if not lease:
#         raise HTTPException(status_code=404, detail="Lease not found for this tenant")

#     # Default the amount paid to the lease's rent amount if amount_paid is not specified
#     amount_due = lease.rent_amount  # Assuming rent_amount is part of the Lease model
#     amount_paid = payment_data.amount_paid if payment_data.amount_paid != 0 else amount_due

#     # Create Stripe Checkout Session
#     try:
#         checkout_session = stripe.checkout.Session.create(
#             payment_method_types=["card"],  # Specifies card payments
#             line_items=[
#                 {
#                     "price_data": {
#                         "currency": "usd",  # Ensure the currency is correctly set
#                         "product_data": {
#                             "name": f"Rent for lease {lease.id}",  # A descriptive name for the charge
#                         },
#                         "unit_amount": int(amount_paid * 100),  # Amount in cents
#                     },
#                     "quantity": 1,  # Quantity is always 1 for a single payment
#                 }
#             ],
#             mode="payment",  # Use "payment" mode for one-time payments
#             success_url="https://your-website.com/success?session_id={CHECKOUT_SESSION_ID}",  # Update with your success URL
#             cancel_url="https://your-website.com/cancel",  # Update with your cancel URL
#             metadata={"lease_id": lease.id},  # Pass lease info in metadata
#         )

#         # Create payment record in the database with the initial status as "pending"
#         payment = Payment(
#             tenant_id=current_user.id,
#             lease_id=lease.id,
#             amount_paid=amount_paid,
#             payment_status="pending",
#             stripe_payment_intent_id=checkout_session.id
#         )
#         db.add(payment)
#         db.commit()
#         db.refresh(payment)

#         return {"checkout_url": checkout_session.url, "payment_id": payment.id}

#     except stripe.error.StripeError as e:
#         raise HTTPException(status_code=400, detail=f"Stripe error: {e.user_message}")

# # 🧾 Webhook to Handle Stripe Events (Payment Confirmation)
# @router.post("/webhook")
# async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
#     payload = await request.body()
#     sig_header = request.headers.get('Stripe-Signature')
    
#     # Verify the webhook signature to ensure it came from Stripe
#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, STRIPE_WEBHOOK_SECRET
#         )
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail="Invalid payload")
#     except stripe.error.SignatureVerificationError as e:
#         raise HTTPException(status_code=400, detail="Invalid signature")

#     # Handle the event
#     if event['type'] == 'payment_intent.succeeded':
#         payment_intent = event['data']['object']  # Contains the payment intent data
#         payment_id = payment_intent['metadata']['lease_id']  # Use metadata to get the lease ID
#         payment = db.query(Payment).filter_by(stripe_payment_intent_id=payment_intent['id']).first()

#         if payment:
#             payment.payment_status = 'succeeded'
#             payment.stripe_payment_intent_id = payment_intent['id']
#             db.commit()
#         else:
#             raise HTTPException(status_code=404, detail="Payment not found")

#     elif event['type'] == 'payment_intent.failed':
#         payment_intent = event['data']['object']
#         payment = db.query(Payment).filter_by(stripe_payment_intent_id=payment_intent['id']).first()

#         if payment:
#             payment.payment_status = 'failed'
#             db.commit()
#         else:
#             raise HTTPException(status_code=404, detail="Payment not found")

#     # Return a 200 response to acknowledge receipt of the event
#     return {"status": "success"}


import stripe
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Payment, Lease, Tenant
from app.schemas import PaymentCreate
from app.routers.auth import get_current_user
from app.config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET

# Initialize Stripe with the secret key
stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter()

# 🏦 Create a Payment with Stripe Checkout
@router.post("/pay")
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Find the tenant linked to the current user
    tenant = db.query(Tenant).filter(Tenant.user_id == current_user.id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail=f"Tenant not found for user {current_user.id}")
    
    # Find the lease linked to the tenant
    lease = db.query(Lease).filter(Lease.tenant_id == tenant.id).first()
    if not lease:
        raise HTTPException(status_code=404, detail=f"Lease not found for tenant {tenant.id}")

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
            success_url="https://your-website.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://your-website.com/cancel",
            metadata={"lease_id": lease.id},
        )

        # Create payment record in the database with the initial status as "pending"
        payment = Payment(
            tenant_id=tenant.id,
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

# 🧾 Webhook to Handle Stripe Events (Payment Confirmation)
@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        lease_id = payment_intent['metadata']['lease_id']  # Use metadata to get the lease ID
        payment = db.query(Payment).filter_by(stripe_payment_intent_id=payment_intent['id']).first()

        if payment:
            payment.payment_status = 'succeeded'
            db.commit()
        else:
            raise HTTPException(status_code=404, detail="Payment not found")

    elif event['type'] == 'payment_intent.failed':
        payment_intent = event['data']['object']
        payment = db.query(Payment).filter_by(stripe_payment_intent_id=payment_intent['id']).first()

        if payment:
            payment.payment_status = 'failed'
            db.commit()
        else:
            raise HTTPException(status_code=404, detail="Payment not found")

    return {"status": "success"}
