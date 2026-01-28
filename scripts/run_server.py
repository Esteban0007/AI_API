#!/usr/bin/env python
"""
Development server startup script.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn
from app.core.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    print(f"""
    ╔════════════════════════════════════════╗
    ║  Semantic Search SaaS - FastAPI Server ║
    ╚════════════════════════════════════════╝
    
    📌 API Title: {settings.API_TITLE}
    📌 Version: {settings.API_VERSION}
    📌 Server: {settings.HOST}:{settings.PORT}
    📌 Debug: {settings.DEBUG}
    
    🚀 Starting server...
    📖 Docs: http://localhost:{settings.PORT}/api/docs
    """)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
