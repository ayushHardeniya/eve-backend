from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")


class DiagnosticCentre(Base):
    __tablename__ = "diagnostic_centres"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)

    tests: Mapped[list["CentreTest"]] = relationship(
        back_populates="centre",
        cascade="all, delete-orphan",
    )
    bookings: Mapped[list["Booking"]] = relationship(back_populates="centre")


class DiagnosticTest(Base):
    __tablename__ = "diagnostic_tests"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    centres: Mapped[list["CentreTest"]] = relationship(
        back_populates="test",
        cascade="all, delete-orphan",
    )
    bookings: Mapped[list["Booking"]] = relationship(back_populates="test")


class CentreTest(Base):
    __tablename__ = "centre_tests"

    centre_id: Mapped[int] = mapped_column(
        ForeignKey("diagnostic_centres.id"),
        primary_key=True,
    )
    test_id: Mapped[int] = mapped_column(
        ForeignKey("diagnostic_tests.id"),
        primary_key=True,
    )
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    centre: Mapped["DiagnosticCentre"] = relationship(back_populates="tests")
    test: Mapped["DiagnosticTest"] = relationship(back_populates="centres")


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    test_id: Mapped[int] = mapped_column(
        ForeignKey("diagnostic_tests.id"),
        nullable=False,
    )
    centre_id: Mapped[int] = mapped_column(
        ForeignKey("diagnostic_centres.id"),
        nullable=False,
    )
    appointment_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")

    user: Mapped["User"] = relationship(back_populates="bookings")
    test: Mapped["DiagnosticTest"] = relationship(back_populates="bookings")
    centre: Mapped["DiagnosticCentre"] = relationship(back_populates="bookings")
    payment: Mapped["Payment | None"] = relationship(
        back_populates="booking",
        uselist=False,
    )


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id"),
        unique=True,
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    booking: Mapped["Booking"] = relationship(back_populates="payment")


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
