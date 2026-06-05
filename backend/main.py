from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers.admin import admin
from .routers.auth import auth
from .routers.booking import booking
from .routers.taxi import taxi

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/frontend", StaticFiles(directory=str(frontend_dir)), name="frontend")

app.include_router(auth)
app.include_router(booking)
app.include_router(taxi)
app.include_router(admin)


@app.get("/")
def root():
    return {"message": "Server running!"}
