from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


db_path = "sqlite:////home/ivan/Projects/icd_codes/data/icd_codes.db"

# for Docker
# db_path = "sqlite:////app/data/icd_codes.db"

engine = create_engine(
    db_path
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
