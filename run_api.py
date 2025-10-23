"""
Script để chạy Caelio API
"""

import uvicorn
from caelio_api import app

if __name__ == "__main__":
    print("🚀 Starting Caelio Personality API...")
    print("📖 Docs: http://localhost:8000/docs")
    print("🔧 ReDoc: http://localhost:8000/redoc") 
    print("⚡ API: http://localhost:8000")
    
    uvicorn.run(
        "caelio_api:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,  # Auto reload khi code thay đổi
        log_level="info"
    )