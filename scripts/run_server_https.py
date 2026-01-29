#!/usr/bin/env python
"""
Development server with self-signed SSL certificate.
Use this for local HTTPS testing only.
"""
import sys
from pathlib import Path
import ssl

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn
from app.core.config import get_settings

if __name__ == "__main__":
    settings = get_settings()

    # SSL certificate paths (will be created if they don't exist)
    cert_file = Path(__file__).parent.parent / "certs" / "cert.pem"
    key_file = Path(__file__).parent.parent / "certs" / "key.pem"

    # Create certs directory if it doesn't exist
    cert_file.parent.mkdir(exist_ok=True)

    # Generate self-signed certificate if not exists
    if not cert_file.exists() or not key_file.exists():
        print("🔐 Generating self-signed SSL certificate...")
        import subprocess

        subprocess.run(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:4096",
                "-keyout",
                str(key_file),
                "-out",
                str(cert_file),
                "-days",
                "365",
                "-nodes",
                "-subj",
                "/CN=localhost",
            ]
        )
        print("✅ Certificate generated!")

    print(
        f"""
    ╔════════════════════════════════════════╗
    ║  Semantic Search SaaS - HTTPS Server   ║
    ╚════════════════════════════════════════╝
    
    📌 API Title: {settings.API_TITLE}
    📌 Version: {settings.API_VERSION}
    📌 Server: https://{settings.HOST}:{settings.PORT}
    📌 Debug: {settings.DEBUG}
    
    ⚠️  WARNING: Using self-signed certificate
    ⚠️  Only for development/testing!
    
    🚀 Starting HTTPS server...
    📖 Docs: https://localhost:{settings.PORT}/api/docs
    
    💡 Ignore browser SSL warnings (self-signed cert)
    """
    )

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
        ssl_certfile=str(cert_file),
        ssl_keyfile=str(key_file),
    )
