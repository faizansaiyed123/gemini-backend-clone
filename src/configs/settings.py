
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from os.path import join, dirname, abspath
import os
# Load the .env file
env_file = join(dirname(abspath(__file__)), "..", ".env")  
if not os.getenv("RENDER"):  
    load_dotenv(env_file, override=True)  
class Settings(BaseSettings):
    """
    Use this class for adding constants from .env file
    """
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    GMAIL_USERNAME: str
    GMAIL_PASSWORD: str
    PORT: int = 8000  
    SERVER_TIMEOUT: int = 60  
    UPSTASH_REDIS_REST_TOKEN: str
    UPSTASH_REDIS_REST_URL: str
    OPENAI_API_KEY:str
    DATABASE_URL: str
    STRIPE_SECRET_KEY:str
    FRONTEND_URL: str = "https://example.com"
    STRIPE_PRICE_ID:str
    STRIPE_WEBHOOK_SECRET:str



    class Config:
        env_file = env_file 
        extra = "allow"

settings = Settings()

