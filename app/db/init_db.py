from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

db_path = "postgresql+psycopg2://admin:admin@localhost:5432/icd_codes"
engine = create_engine(db_path)

# SQLite
# db_path = "sqlite:////home/ivan/Projects/icd_codes/data/icd_codes.db"
# engine = create_engine(
#     db_path,
#     connect_args={"check_same_thread": False},
# )

# Docker
# db_path = "sqlite:////app/data/icd_codes.db"

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
