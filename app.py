import os
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from logging.config import dictConfig
from src.routers.auth import router as auth_router
from src.configs.utilites import execute_sql_files
from src.routers.user import router as user_router
from src.routers.chatroom import router as chatroom_router
from src.routers.message import router as message_router
from src.routers.subscription import router as subscription_router

def configure_routes(app: FastAPI) -> None:
    """
    Register all routers on the application instance.
    """

    app.include_router(auth_router, prefix="/auth", tags=["Auth"])
    app.include_router(user_router, prefix="/user", tags=["User"])
    app.include_router(chatroom_router, prefix="/user", tags=["ChatRoom"])
    app.include_router(message_router, prefix="/user", tags=["Message"])
    app.include_router(subscription_router , prefix="/subscribe", tags=["Subscription"])



def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI()

    

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://103.204.189.95:5000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


 
    configure_routes(app)

    return app
execute_sql_files() 


app = create_app()
