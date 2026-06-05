from ..database.utils import fetch_query
from fastapi import APIRouter

taxi = APIRouter(prefix="/taxi", tags=["Taxi"])


@taxi.get("/all")
def get_all_taxis():
    return fetch_query("SELECT * FROM Taxi WHERE status = 'available'")
