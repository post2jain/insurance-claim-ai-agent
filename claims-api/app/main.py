from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import claims, suggestions
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Insurance Claims Processing API",
    description="API for processing insurance claims with AI-powered suggestions",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(claims.router, prefix="/api", tags=["claims"])
app.include_router(suggestions.router, prefix="/api", tags=["suggestions"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Insurance Claims Processing API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    } 