from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql://gemini_sp7e_user:vMIEXSVAfR7TXXjhQlBc5q31jdYGexYm@dpg-d1p28cs9c44c7385ctmg-a/gemini_sp7e"


engine = create_engine(DATABASE_URL, pool_pre_ping=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

