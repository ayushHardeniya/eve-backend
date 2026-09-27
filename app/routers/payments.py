from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Booking, Payment, User, WebhookEvent
from app.schemas import Payment as PaymentSchema
from app.schemas import PaymentCreate, Webhook

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=PaymentSchema)
def create_payment(
    data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = db.get(Booking, data.booking_id)

    if not booking or booking.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail="Booking is not pending",
        )

    if data.status not in {"SUCCESS", "FAILED"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment status",
        )

    existing = db.scalar(select(Payment).where(Payment.booking_id == booking.id))
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Payment already exists",
        )

    payment = Payment(
        booking_id=booking.id,
        amount=booking.amount,
        status=data.status,
    )

    booking.status = "CONFIRMED" if data.status == "SUCCESS" else "FAILED"

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


@router.post("/webhook/")
def payment_webhook(
    data: Webhook,
    db: Session = Depends(get_db),
):
    existing_event = db.scalar(
        select(WebhookEvent).where(WebhookEvent.event_id == data.event_id)
    )

    if existing_event:
        return {"message": "Event already processed"}

    booking = db.get(Booking, data.booking_id)

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if data.status not in {"SUCCESS", "FAILED"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment status",
        )

    payment = db.scalar(select(Payment).where(Payment.booking_id == booking.id))

    if payment:
        payment.status = data.status
    else:
        payment = Payment(
            booking_id=booking.id,
            amount=booking.amount,
            status=data.status,
        )
        db.add(payment)

    booking.status = "CONFIRMED" if data.status == "SUCCESS" else "FAILED"

    event = WebhookEvent(event_id=data.event_id)
    db.add(event)
    db.commit()

    return {"message": "Webhook processed"}
