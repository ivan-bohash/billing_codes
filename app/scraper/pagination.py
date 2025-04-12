import requests
from lxml import html
from app.db.init_db import SessionLocal
from app.config import settings
from app.db.models.pagination import PaginationBillModel, PaginationNonBillModel
from app.extensions.sqlalchemy.pagination_manager import PaginationManager


class PaginationParser:
    def __init__(self, base_url, pagination_model):
        self.headers = settings.headers
        self.base_url = base_url
        self.pagination_model = pagination_model

    def extract_pagination_urls(self):
        response_html = requests.get(url=self.base_url, headers=self.headers).content
        tree = html.fromstring(response_html)
        last_index = int(
            tree.xpath('//ul[@class="pagination"]/li[@class="PagedList-skipToLast"]/a/@href')[0].split('/')[-1]) + 1

        urls = [f"{self.base_url}{i}" for i in range(1, last_index)]

        return urls

    def add_to_db(self):
        with SessionLocal() as session:
            urls = self.extract_pagination_urls()
            pagination_manager = PaginationManager(session=session, model=self.pagination_model, fetch_data=urls)
            pagination_manager.run()


class PaginationBillable(PaginationParser):
    def __init__(self):
        super().__init__(
            base_url=settings.billable_url,
            pagination_model=PaginationBillModel
        )


class PaginationNonBillable(PaginationParser):
    def __init__(self):
        super().__init__(
            base_url=settings.non_billable_url,
            pagination_model=PaginationNonBillModel
        )


def run_pagination_parser(parser_name):
    if parser_name == "billable":
        parser = PaginationBillable()
    elif parser_name == "non_billable":
        parser = PaginationNonBillable()
    else:
        raise ValueError("Unknown parser")

    parser.add_to_db()


