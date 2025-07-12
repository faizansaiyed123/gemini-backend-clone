import os
import threading
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from src.routers.auth import router as auth_router
from src.configs.utilites import execute_sql_files
from src.routers.user import router as user_router
from src.routers.chatroom import router as chatroom_router
from src.routers.message import router as message_router
from src.routers.subscription import router as subscription_router

# ✅ Import your worker loop function
from src.services.worker import worker_loop

def configure_routes(app: FastAPI) -> None:
    """
    Register all routers on the application instance.
    """
    app.include_router(auth_router, prefix="/auth", tags=["Auth"])
    app.include_router(user_router, prefix="/user", tags=["User"])
    app.include_router(chatroom_router, prefix="/ChatRoom", tags=["ChatRoom"])
    app.include_router(message_router, prefix="/message", tags=["Message"])
    app.include_router(subscription_router , prefix="/subscribe", tags=["Subscription"])

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    configure_routes(app)

    return app

# Run database setup
execute_sql_files()

# Create app instance
app = create_app()

# tart the background worker in a thread when app starts
@app.on_event("startup")
async def startup_event():
    def start_worker():
        thread = threading.Thread(target=worker_loop, daemon=True)
        thread.start()

    start_worker()
