from fastapi import FastAPI
from contextlib import asynccontextmanager
from brain.core.db import init_db
from brain.api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the database
    init_db()
    yield
    # Shutdown: Clean up if needed
    pass

app = FastAPI(
    title="AI Context Operating System (The Brain)",
    description="The persistent intelligence layer that manages AI context, code structures, episodic, semantic, decision, and failure memories.",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(router)
