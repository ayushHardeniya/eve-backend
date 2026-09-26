from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class Login(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class CentreCreate(BaseModel):
    name: str
    location: str


class Centre(CentreCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TestCreate(BaseModel):
    name: str


class Test(TestCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CentreTestResponse(BaseModel):
    id: int
    name: str
    price: Decimal


class CentreTestCreate(BaseModel):
    test_id: int
    price: Decimal = Field(gt=0)


class BookingCreate(BaseModel):
    test_id: int
    centre_id: int
    appointment_at: datetime


class Booking(BaseModel):
    id: int
    user_id: int
    test_id: int
    centre_id: int
    appointment_at: datetime
    amount: Decimal
    status: str

    model_config = ConfigDict(from_attributes=True)


class PaymentCreate(BaseModel):
    booking_id: int


class Payment(BaseModel):
    id: int
    booking_id: int
    amount: Decimal
    status: str

    model_config = ConfigDict(from_attributes=True)


class Webhook(BaseModel):
    event_id: str
    booking_id: int
    status: str
