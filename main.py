from fastapi import FastAPI
from typing import Optional
from api.routes import auth, users, garmin
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# origins = ['http://localhost:8000', 'http://localhost', 'http://localhost:3000',
#            'http://127.0.0.1:8000', 'http://127.0.0.1:3000']

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(garmin.router, prefix="/garmin")
# app.include_router(accounts.router, prefix="/accounts")