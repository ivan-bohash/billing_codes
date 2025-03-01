import uvicorn
from fastapi import FastAPI
from app.db.init_db import engine, Base
from app.db.models.pagination import PaginationModel
from app.db.models.url import UrlModel
from app.db.models.detail import DetailModel


app = FastAPI()

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    uvicorn.run("run:app", reload=True)

