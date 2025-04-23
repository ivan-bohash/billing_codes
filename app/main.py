import uvicorn
from fastapi import FastAPI, Depends

from sqlalchemy.orm import Session
from app.db.init_db import engine, Base, get_db

from app.db.models.pagination import PaginationBillModel, PaginationNonBillModel
from app.db.models.url import UrlsBillModel, UrlsNonBillModel
from app.db.models.detail import DetailsBillModel, DetailsNonBillModel

app = FastAPI()
Base.metadata.create_all(bind=engine)


@app.get("/billable_pagination")
async def get_pagination(db: Session = Depends(get_db)):
    db_data = db.query(PaginationBillModel).all()
    return db_data


@app.get("/non_billable_pagination")
async def get_pagination(db: Session = Depends(get_db)):
    db_data = db.query(PaginationNonBillModel).all()
    return db_data


@app.get("/urls_billable")
async def get_urls(db: Session = Depends(get_db)):
    db_data = db.query(UrlsBillModel).all()
    return db_data


@app.get("/urls_non_billable")
async def get_urls(db: Session = Depends(get_db)):
    db_data = db.query(UrlsNonBillModel).all()
    return db_data


@app.get("/details_billable")
async def get_details(db: Session = Depends(get_db)):
    db_data = db.query(DetailsBillModel).all()
    return db_data


@app.get("/details_non_billable")
async def get_details(db: Session = Depends(get_db)):
    db_data = db.query(DetailsNonBillModel).all()
    return db_data


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
