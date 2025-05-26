# Development CORS configuration
from fastapi.middleware.cors import CORSMiddleware

def add_dev_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3001", 
            f"http://localhost:{FRONTEND_PORT}",
            "*"  # Allow all for development
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
