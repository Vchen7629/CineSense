from fastapi.middleware.cors import CORSMiddleware

def add_cors(app):
    origins = [
        "http://localhost:3000",  # React dev server
        "http://localhost:8000",  # optional if needed
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # or ["*"] for all origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )