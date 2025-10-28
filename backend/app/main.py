from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import meetings, search 
from app.db import database, models

# For production, use Alembic migrations
# models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="AI Meeting Intelligence Platform",
    description="Process meeting recordings to generate summaries and insights.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    meetings.router,
    prefix="/api/v1/meetings",
    tags=["Meetings"]
)

app.include_router(
    search.router,
    prefix="/api/v1/search",
    tags=["Search"]
)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the AI Meeting Intelligence Platform API"}