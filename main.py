from src.configs.utilites import execute_sql_files
from src.configs.settings import settings 
import uvicorn
from app import app

def run_app():
    try:
        execute_sql_files()
    except Exception as e:
        exit(1)

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=settings.PORT or 8000,
        timeout_keep_alive=settings.SERVER_TIMEOUT,
        reload=False,
    )


if __name__ == "__main__":
    run_app()