from fastapi.middleware.cors import CORSMiddleware
from middleware.config import settings

def add_cors(app):
    origins = settings.cors_origins

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # or ["*"] for all origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )