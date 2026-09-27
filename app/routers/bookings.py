from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Booking, CentreTest, User
from app.schemas import Booking as BookingSchema
from app.schemas import BookingCreate

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=BookingSchema)
def create_booking(
    data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    centre_test = db.scalar(
        select(CentreTest).where(
            CentreTest.centre_id == data.centre_id,
            CentreTest.test_id == data.test_id,
        )
    )

    if not centre_test:
        raise HTTPException(
            status_code=404,
            detail="Test is not available at this centre",
        )

    booking = Booking(
        user_id=current_user.id,
        test_id=data.test_id,
        centre_id=data.centre_id,
        appointment_at=data.appointment_at,
        amount=centre_test.price,
        status="PENDING",
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking


@router.get("/", response_model=list[BookingSchema])
def list_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.scalars(select(Booking).where(Booking.user_id == current_user.id)).all()


@router.get("/{booking_id}", response_model=BookingSchema)
def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = db.get(Booking, booking_id)

    if not booking or booking.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Booking not found")

    return booking


@router.patch("/{booking_id}/cancel", response_model=BookingSchema)
def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = db.get(Booking, booking_id)

    if not booking or booking.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status not in {"PENDING", "CONFIRMED"}:
        raise HTTPException(
            status_code=400,
            detail="Booking cannot be cancelled",
        )

    booking.status = "CANCELLED"
    db.commit()
    db.refresh(booking)

    return booking
