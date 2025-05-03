from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.init_db import get_db
from app.db.schemas.schemas import IcdSchema

from app.db.models.url import UrlsBillModel, UrlsNonBillModel
from app.db.models.history import HistoryBillModel, HistoryNonBillModel

templates = Jinja2Templates(directory="templates")

# for Docker
# templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


@router.get('/')
async def index():
    return {"message": "ICD-10-CM Codes"}


@router.get('/icd-code', response_class=JSONResponse)
async def get_code(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/icd-codes/{icd_code}", response_model=IcdSchema)
async def get_code_json(icd_code: str, db: Session = Depends(get_db)):
    formatted_icd_code = icd_code.strip(' ').upper()

    data = [
        [UrlsBillModel, HistoryBillModel, "Billable/Specific ICD-10-CM Codes"],
        [UrlsNonBillModel, HistoryNonBillModel, "Non-Billable/Non-Specific ICD-10-CM Codes"],
    ]

    for url_model, history_model, rule in data:
        url_data = db.query(url_model).filter(url_model.icd_code == formatted_icd_code).one_or_none()

        if url_data:
            history = (db.query(history_model.code_history)
                       .filter(history_model.icd_code == formatted_icd_code)
                       .one_or_none())

            return IcdSchema(
                icd_code=url_data.icd_code,
                rule=rule,
                updated=url_data.updated_at.format(),
                url=url_data.url,
                code_history=history.code_history
            )

    raise HTTPException(status_code=404, detail="Invalid ICD-10-CM Code")
