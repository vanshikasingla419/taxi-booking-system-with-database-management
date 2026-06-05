import os
from datetime import datetime

import jwt
from ..database.utils import execute_query, fetch_query
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

booking = APIRouter(prefix="/booking", tags=["Booking"])

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"


class BookingRequest(BaseModel):
    taxi_id: int
    source: str
    destination: str
    distance_km: float


class UpdateBookingRequest(BaseModel):
    taxi_id: int
    source: str
    destination: str
    distance_km: float
    payment_status: str


class FareRequest(BaseModel):
    distance_km: float


def get_user_id_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def calculate_fare(distance_km: float):
    return round(distance_km * 12.0, 2)


@booking.post("/create")
def create_booking(req: BookingRequest, token: str = Header(...)):
    customer_id = get_user_id_from_token(token)
    fare = calculate_fare(req.distance_km)

    # 1. Create booking
    execute_query(
        """
        INSERT INTO Booking (customer_id, taxi_id, source, destination, date, fare, payment_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            customer_id,
            req.taxi_id,
            req.source,
            req.destination,
            datetime.now(),
            fare,
            "pending",
        ),
    )

    # 2. Set taxi unavailable
    execute_query(
        "UPDATE Taxi SET status = 'unavailable' WHERE taxi_id = %s", (req.taxi_id,)
    )

    # 3. Fetch driver info
    driver = fetch_query(
        "SELECT name, phone FROM Driver WHERE taxi_id = %s", (req.taxi_id,)
    )

    driver_info = driver[0] if driver else {"name": "N/A", "phone": "N/A"}

    return {
        "message": "Booking created",
        "fare": fare,
        "driver_name": driver_info["name"],
        "driver_phone": driver_info["phone"],
    }


@booking.get("/{booking_id}")
def get_booking(booking_id: int, token: str = Header(...)):
    customer_id = get_user_id_from_token(token)

    rows = fetch_query(
        """
        SELECT * FROM Booking
        WHERE booking_id = %s AND customer_id = %s
        """,
        (booking_id, customer_id),
    )

    if not rows:
        raise HTTPException(status_code=404, detail="Booking not found")

    return rows[0]


@booking.get("/user/me")
def get_user_bookings(token: str = Header(...)):
    customer_id = get_user_id_from_token(token)

    return fetch_query(
        "SELECT * FROM Booking WHERE customer_id = %s ORDER BY date DESC",
        (customer_id,),
    )


@booking.put("/{booking_id}")
def update_booking(
    booking_id: int, req: UpdateBookingRequest, token: str = Header(...)
):
    customer_id = get_user_id_from_token(token)
    fare = calculate_fare(req.distance_km)

    execute_query(
        """
        UPDATE Booking
        SET taxi_id=%s, source=%s, destination=%s,
            date=%s, fare=%s, payment_status=%s
        WHERE booking_id=%s AND customer_id=%s
        """,
        (
            req.taxi_id,
            req.source,
            req.destination,
            datetime.now(),
            fare,
            req.payment_status,
            booking_id,
            customer_id,
        ),
    )

    return {"message": "Booking updated", "fare": fare}


@booking.delete("/{booking_id}")
def cancel_booking(booking_id: int, token: str = Header(...)):
    customer_id = get_user_id_from_token(token)

    execute_query(
        "DELETE FROM Booking WHERE booking_id=%s AND customer_id=%s",
        (booking_id, customer_id),
    )

    return {"message": "Booking cancelled"}


@booking.post("/calculate-fare")
def calc_fare(req: FareRequest):
    return {"fare": calculate_fare(req.distance_km)}


class DriverUpdateRequest(BaseModel):
    driver_name: str
    booking_id: int
    payment_status: str


@booking.post("/driver/update")
def driver_update(req: DriverUpdateRequest):
    rows = fetch_query(
        "SELECT taxi_id FROM Booking WHERE booking_id = %s", (req.booking_id,)
    )

    if not rows:
        raise HTTPException(status_code=404, detail="Booking not found")

    taxi_id = rows[0]["taxi_id"]

    execute_query(
        "UPDATE Booking SET payment_status = %s WHERE booking_id = %s",
        (req.payment_status, req.booking_id),
    )

    execute_query("UPDATE Taxi SET status = 'available' WHERE taxi_id = %s", (taxi_id,))

    return {
        "message": "Booking updated successfully",
        "taxi_id": taxi_id,
        "new_status": req.payment_status,
    }
