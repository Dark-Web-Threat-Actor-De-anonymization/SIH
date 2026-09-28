from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import (
    APP_NAME,
    APP_VERSION,
)

from app.routes import (
    actors,
    blockchain,
    handles,
    intelligence,
    posts,
    profile,
    search,
)


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Evidence-driven DarkForums behavioral "
        "persona analysis API."
    ),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTES
# ============================================================

app.include_router(search.router)
app.include_router(profile.router)
app.include_router(actors.router)
app.include_router(handles.router)
app.include_router(posts.router)
app.include_router(intelligence.router)
app.include_router(blockchain.router)


# ============================================================
# HEALTH
# ============================================================

@app.get("/")
def home():

    return {
        "message": "DarkTrace Intelligence API Running",
        "version": APP_VERSION,
    }


@app.get("/health")
def health():

    return {
        "status": "ok",
        "database": "PostgreSQL"
    }