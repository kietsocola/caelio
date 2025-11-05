"""
Script để chạy Caelio API - Combined Server
Chạy cả Personality API và Caelio Care API trên cùng 1 server
"""

import uvicorn
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import main APIs
from caelio_api import app as personality_app
from caelio_care.main import app as care_app

@asynccontextmanager
async def combined_lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Combined Caelio API Server...")
    print("📖 Personality API: http://localhost:8000/personality")  
    print("💚 Caelio Care API: http://localhost:8000/care")
    print("� Main Docs: http://localhost:8000/docs")
    print("🔧 Care Docs: http://localhost:8000/care/docs")
    print("⚡ Root API: http://localhost:8000")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Combined Caelio API Server")

# Create main combined app
main_app = FastAPI(
    title="Caelio Combined API",
    description="Combined Personality Assessment and Emotional Care System",
    version="2.0.0",
    lifespan=combined_lifespan
)

# CORS middleware for main app
main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@main_app.get("/")
async def root():
    """Root endpoint for combined API"""
    return {
        "message": "Caelio Combined API Server",
        "version": "2.0.0",
        "services": {
            "personality": {
                "description": "Personality assessment and book recommendations",
                "endpoint": "/personality",
                "docs": "/personality/docs"
            },
            "care": {
                "description": "Emotional assessment and white books system", 
                "endpoint": "/care",
                "docs": "/care/docs"
            }
        },
        "features": [
            "personality_assessment", 
            "book_recommendations", 
            "emotional_assessment", 
            "white_books", 
            "authentication"
        ]
    }

@main_app.get("/health")
async def health_check():
    """Combined health check"""
    return {
        "status": "healthy",
        "services": {
            "personality": "running",
            "care": "running"
        },
        "message": "All services are operational"
    }

# Mount sub-applications
main_app.mount("/personality", personality_app)
main_app.mount("/care", care_app)

if __name__ == "__main__":
    print("🌟 Starting Caelio Combined API Server...")
    print("=" * 60)
    print("📍 ENDPOINTS:")
    print("   🏠 Root: http://localhost:8000/")
    print("   🧠 Personality API: http://localhost:8000/personality/")
    print("   💚 Caelio Care API: http://localhost:8000/care/")
    print("=" * 60)
    print("📚 DOCUMENTATION:")
    print("   📖 Main Docs: http://localhost:8000/docs")
    print("   🧠 Personality Docs: http://localhost:8000/personality/docs") 
    print("   💚 Care Docs: http://localhost:8000/care/docs")
    print("=" * 60)
    
    uvicorn.run(
        "run_api:main_app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )