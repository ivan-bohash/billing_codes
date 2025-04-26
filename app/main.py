import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.init_db import engine, Base, get_db
from app.db.schemas.schemas import IcdSchema

from app.db.models.pagination import PaginationBillModel, PaginationNonBillModel
from app.db.models.url import UrlsBillModel, UrlsNonBillModel
from app.db.models.detail import DetailsBillModel, DetailsNonBillModel

app = FastAPI()
Base.metadata.create_all(bind=engine)


@app.get("/{icd_code}", response_model=IcdSchema)
async def get_code(icd_code: str, db: Session = Depends(get_db)):
    formatted_icd_code = icd_code.strip(' ').upper()

    data = [
        [UrlsBillModel, DetailsBillModel, "Billable/Specific ICD-10-CM Codes"],
        [UrlsNonBillModel, DetailsNonBillModel, "Non-Billable/Non-Specific ICD-10-CM Codes"],
    ]

    for url_model, details_model, rule in data:
        url_data = db.query(url_model).filter(url_model.icd_code == formatted_icd_code).one_or_none()

        if url_data:
            details = db.query(details_model.detail).filter(details_model.icd_code == formatted_icd_code).one_or_none()

            return IcdSchema(
                icd_code=url_data.icd_code,
                rule=rule,
                updated=url_data.updated_at.format(),
                url=url_data.url,
                details=details.detail
            )

    raise HTTPException(status_code=404, detail="Invalid ICD-10-CM Code")


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
