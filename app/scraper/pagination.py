import requests
from lxml import html
from app.db.init_db import SessionLocal
from app.config import settings
from app.db.models.pagination import PaginationBillModel, PaginationNonBillModel


def extract_pagination_urls(type):
    if type == "billable":
        base_url = "https://www.icd10data.com/ICD10CM/Codes/Rules/Billable_Specific_Codes/"
    elif type == "non_billable":
        base_url = "https://www.icd10data.com/ICD10CM/Codes/Rules/Non_Billable_Specific_Codes/"

    headers = settings.headers
    # proxies = {"http": "72.10.160.171:1959"}

    response_html = requests.get(url=base_url, headers=headers).content
    tree = html.fromstring(response_html)

    last_index = int(
        tree.xpath('//ul[@class="pagination"]/li[@class="PagedList-skipToLast"]/a/@href')[0].split('/')[-1]) + 1

    urls = [f"{base_url}{i}" for i in range(1, last_index)]

    return urls


def add_to_db(type):
    with SessionLocal() as db:
        urls = extract_pagination_urls(type)
        if type == "billable":
            db_data = [PaginationBillModel(url=url) for url in urls]
        elif type == "non_billable":
            db_data = [PaginationNonBillModel(url=url) for url in urls]
        db.add_all(db_data)
        db.commit()
        print(f"Done {len(db_data)}")


if __name__ == "__main__":
    add_to_db(type="non_billable")

