import asyncio
from lxml import html
from app.config import settings
from app.db.init_db import SessionLocal
from app.db.models.pagination import PaginationBillModel, PaginationNonBillModel
from app.db.models.url import UrlsBillModel, UrlsNonBillModel
from app.db.models.detail import DetailsBillModel, DetailsNonBillModel
from app.extensions.sqlalchemy.urls_manager import UrlsManager
from app.scraper.base_icd import BaseICD


class UrlParser(BaseICD):
    def __init__(self, pagination_model, urls_model, opposite_urls_model, details_model):
        self.headers = settings.headers
        self.pagination_model = pagination_model
        self.urls_model = urls_model
        self.opposite_urls_model = opposite_urls_model
        self.details_model = details_model

    async def get_icd_data(self, session, url):
        async with session.get(url=url, headers=self.headers) as response:
            base_urls = []

            response_html = await response.text()
            tree = html.fromstring(response_html)

            icd_hrefs = tree.xpath(
                '//ul[following-sibling::div[@class="ad-unit"]]//a[@class="identifier"]/@href'
            )

            for href in icd_hrefs:
                base_urls.append({
                    "icd_code": href.split('/')[-1],
                    "url": f'https://www.icd10data.com{href}'
                })

        return base_urls

    async def manage_urls(self, task):
        with SessionLocal() as session:
            icd_manager = UrlsManager(
                session=session,
                pagination_model=self.pagination_model,
                urls_model=self.urls_model,
                opposite_urls_model=self.opposite_urls_model,
                details_model=self.details_model,
                fetch_method=self.main
            )

            if task == "update_urls":
                await icd_manager.update_urls()
            elif task == "delete_urls":
                icd_manager.delete_urls()
            else:
                raise ValueError("Unknown task")


class UrlsNonBillable(UrlParser):
    def __init__(self):
        super().__init__(
            pagination_model=PaginationNonBillModel,
            urls_model=UrlsNonBillModel,
            opposite_urls_model=UrlsBillModel,
            details_model=DetailsNonBillModel
        )


class UrlsBillable(UrlParser):
    def __init__(self):
        super().__init__(
            pagination_model=PaginationBillModel,
            urls_model=UrlsBillModel,
            opposite_urls_model=UrlsNonBillModel,
            details_model=DetailsBillModel,
        )


def run_urls_parser(task):
    non_billable_parser = UrlsNonBillable()
    billable_parser = UrlsBillable()

    async def run_parsers():
        await non_billable_parser.manage_urls(task)
        await billable_parser.manage_urls(task)

    asyncio.run(run_parsers())




