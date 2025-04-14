import asyncio
from lxml import html
from app.config import settings
from app.db.init_db import SessionLocal
from app.db.models.pagination import PaginationBillModel, PaginationNonBillModel
from app.db.models.url import UrlsBillModel, UrlsNonBillModel
from app.db.models.detail import DetailsBillModel, DetailsNonBillModel
from app.extensions.sqlalchemy.urls_manager import UrlsManager
from app.scraper.icd_mixin import ICDMixin


class UrlParser(ICDMixin):
    def __init__(self, pagination_model, urls_model, details_model):
        self.headers = settings.headers
        self.pagination_model = pagination_model
        self.urls_model = urls_model
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

    async def add_to_db(self):
        with SessionLocal() as session:
            pagination_data = session.query(self.pagination_model).all()
            urls = [data.url for data in pagination_data]
            icd_data = await self.main(urls=urls)

            icd_manager = UrlsManager(
                session=session,
                urls_model=self.urls_model,
                details_model=self.details_model,
                fetch_data=icd_data
            )
            icd_manager.run()


class UrlsBillable(UrlParser):
    def __init__(self):
        super().__init__(
            pagination_model=PaginationBillModel,
            urls_model=UrlsBillModel,
            details_model=DetailsBillModel,
        )


class UrlsNonBillable(UrlParser):
    def __init__(self):
        super().__init__(
            pagination_model=PaginationNonBillModel,
            urls_model=UrlsNonBillModel,
            details_model=DetailsNonBillModel
        )


def run_urls_parser(parser_name):
    if parser_name == "billable":
        parser = UrlsBillable()
    elif parser_name == "non_billable":
        parser = UrlsNonBillable()
    else:
        raise ValueError("Unknown parser")

    asyncio.run(parser.add_to_db())
