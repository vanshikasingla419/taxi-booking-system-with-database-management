import os
from datetime import datetime, timedelta

import jwt
from ..database.utils import execute_query, fetch_query
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

admin = APIRouter(prefix="/admin", tags=["Admin"])

ADMIN_NAME = os.environ.get("ADMIN_NAME")
ADMIN_PASS = os.environ.get("ADMIN_PASS")

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"


def create_admin_token():
    payload = {
        "sub": "ADMIN",
        "role": "admin",
        "exp": datetime.utcnow() + timedelta(hours=6),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_admin(token: str = Header(...)):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not admin token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ---------------- LOGIN ----------------


class AdminLogin(BaseModel):
    username: str
    password: str


@admin.post("/login")
def admin_login(req: AdminLogin):
    if req.username != ADMIN_NAME or req.password != ADMIN_PASS:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    token = create_admin_token()
    return {"admin_token": token}


# ---------------- VERIFY TOKEN ----------------


@admin.get("/verify")
def verify_admin_token(token: str = Header(...)):
    verify_admin(token)  # reuse function
    return {"valid": True}


# ---------------- TAXI CRUD ----------------


class TaxiModel(BaseModel):
    model: str
    capacity: int
    status: str = "available"


@admin.post("/taxi/add")
def add_taxi(data: TaxiModel, token: str = Header(...)):
    verify_admin(token)

    execute_query(
        "INSERT INTO Taxi(model, capacity, status) VALUES (%s, %s, %s)",
        (data.model, data.capacity, data.status),
    )
    return {"message": "Taxi added successfully"}


class TaxiUpdate(BaseModel):
    model: str
    capacity: int
    status: str


@admin.put("/taxi/update/{taxi_id}")
def update_taxi(taxi_id: int, data: TaxiUpdate, token: str = Header(...)):
    verify_admin(token)

    execute_query(
        """
        UPDATE Taxi
        SET model=%s, capacity=%s, status=%s
        WHERE taxi_id=%s
        """,
        (data.model, data.capacity, data.status, taxi_id),
    )
    return {"message": "Taxi updated"}


@admin.delete("/taxi/delete/{taxi_id}")
def delete_taxi(taxi_id: int, token: str = Header(...)):
    verify_admin(token)

    execute_query("DELETE FROM Taxi WHERE taxi_id=%s", (taxi_id,))
    return {"message": "Taxi deleted"}


# ---------------- DRIVER CRUD ----------------


class DriverModel(BaseModel):
    name: str
    phone: str
    taxi_id: int


@admin.post("/driver/add")
def add_driver(data: DriverModel, token: str = Header(...)):
    verify_admin(token)

    execute_query(
        "INSERT INTO Driver(name, phone, taxi_id) VALUES (%s, %s, %s)",
        (data.name, data.phone, data.taxi_id),
    )
    return {"message": "Driver added successfully"}


class DriverUpdate(BaseModel):
    name: str
    phone: str
    taxi_id: int


@admin.put("/driver/update/{driver_id}")
def update_driver(driver_id: int, data: DriverUpdate, token: str = Header(...)):
    verify_admin(token)

    execute_query(
        """
        UPDATE Driver
        SET name=%s, phone=%s, taxi_id=%s
        WHERE driver_id=%s
        """,
        (data.name, data.phone, data.taxi_id, driver_id),
    )
    return {"message": "Driver updated"}


@admin.delete("/driver/delete/{driver_id}")
def delete_driver(driver_id: int, token: str = Header(...)):
    verify_admin(token)

    execute_query("DELETE FROM Driver WHERE driver_id=%s", (driver_id,))
    return {"message": "Driver deleted"}


@admin.get("/taxi/all")
def get_all_taxis():
    return fetch_query("SELECT * FROM Taxi")


@admin.get("/driver/all")
def get_all_drivers():
    return fetch_query("""
        SELECT d.driver_id, d.name, d.phone, d.taxi_id, t.model AS taxi_model
        FROM Driver d
        LEFT JOIN Taxi t ON d.taxi_id = t.taxi_id
    """)


@admin.get("/bookings/completed")
def get_completed_bookings(token: str = Header(...)):
    verify_admin(token)

    return fetch_query("""
        SELECT
            b.booking_id,
            b.source,
            b.destination,
            b.date,
            b.fare,
            b.payment_status,

            c.customer_id,
            c.name AS customer_name,
            c.phone AS customer_phone,
            c.email AS customer_email,

            d.driver_id,
            d.name AS driver_name,
            d.phone AS driver_phone,

            t.model AS taxi_model,
            t.capacity AS taxi_capacity

        FROM Booking b
        JOIN Customer c ON b.customer_id = c.customer_id
        JOIN Driver d ON b.taxi_id = d.taxi_id
        JOIN Taxi t ON b.taxi_id = t.taxi_id
        WHERE b.payment_status IN ('paid', 'completed')
        ORDER BY b.date DESC;
    """)


@admin.get("/bookings/pending")
def get_pending_bookings(token: str = Header(...)):
    verify_admin(token)

    return fetch_query("""
        SELECT
            b.booking_id,
            b.source,
            b.destination,
            b.date,
            b.fare,
            b.payment_status,

            c.customer_id,
            c.name AS customer_name,
            c.phone AS customer_phone,
            c.email AS customer_email,

            d.driver_id,
            d.name AS driver_name,
            d.phone AS driver_phone,

            t.model AS taxi_model,
            t.capacity AS taxi_capacity

        FROM Booking b
        JOIN Customer c ON b.customer_id = c.customer_id
        JOIN Driver d ON b.taxi_id = d.taxi_id
        JOIN Taxi t ON b.taxi_id = t.taxi_id
        WHERE b.payment_status = 'pending'
        ORDER BY b.date DESC;
    """)
