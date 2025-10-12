from __future__ import annotations
import os
import uvicorn

from src.settings import settings
from src.database import database_service


def main():
    if not database_service.check_database_exists():
        print("Database not initialized. Please run the schema.sql file.")
        print("psql -U postgres -d yourdb -f src/database/schema.sql")
        exit(1)
    
    # Start server
    port = int(os.getenv("PORT", "8000"))
    print(f"🚀 Starting server on http://127.0.0.1:{port}")
    
    uvicorn.run(
        "src.api.api:app",
        host="127.0.0.1",
        port=port,
        reload=settings.app_debug
    )

if __name__ == "__main__":
    main()

