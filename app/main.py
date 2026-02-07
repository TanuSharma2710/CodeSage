from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from db.database import engine, Base
from models.user import User
from models.debug_session import DebugSession, ErrorTracking  # Import debug models

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Add missing columns if they don't exist (migration for existing databases)
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR"))
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE"))
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
        conn.commit()
except Exception as e:
    print(f"Migration note: {e}")

# Import router after DB setup
from app.api.v1.router import router as api_router

app = FastAPI(
    title="CodeSage API",
    description="AI-Assisted Debugger and Learning Platform",
    version="1.0.0"
)

# Configure CORS - allow all origins during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Welcome to CodeSage API", "docs": "/docs"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
