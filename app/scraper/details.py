import asyncio
from lxml import html
import re
from app.config import settings
from app.db.init_db import SessionLocal
from app.db.models.detail import DetailsBillModel, DetailsNonBillModel
from app.db.models.url import UrlsBillModel, UrlsNonBillModel
from app.extensions.sqlalchemy.details_manager import DetailsManager
from app.scraper.icd_mixin import ICDMixin


class DetailParser(ICDMixin):
    def __init__(self, urls_model, details_model):
        self.headers = settings.headers
        self.urls_model = urls_model
        self.details_model = details_model

    async def get_icd_data(self, session, url):
        async with session.get(url=url, headers=self.headers) as response:
            icd_details = []
            response_html = await response.text()
            tree = html.fromstring(response_html)

            icd_code = tree.xpath('//div[@class="headingContainer"]//span[@class="identifierDetail"]/text()')[0]
            description_data = tree.xpath('//ul/li[span[@class="identifier"]]/text()')
            description_detail = ' '.join(description_data)
            detail = re.sub(r'\s+', ' ', description_detail).strip()

            icd_details.append({"icd_code": icd_code, "detail": detail})

        return icd_details

    async def add_to_db(self):
        with SessionLocal() as session:
            details_manager = DetailsManager(
                session=session,
                urls_model=self.urls_model,
                details_model=self.details_model,
                fetch_method=self.main
            )

            await details_manager.run()


class DetailsBillable(DetailParser):
    def __init__(self):
        super().__init__(
            urls_model=UrlsBillModel,
            details_model=DetailsBillModel
        )


class DetailsNonBillable(DetailParser):
    def __init__(self):
        super().__init__(
            urls_model=UrlsNonBillModel,
            details_model=DetailsNonBillModel
        )


def run_details_parser(parser_name):
    if parser_name == "billable":
        parser = DetailsBillable()
    elif parser_name == "non_billable":
        parser = DetailsNonBillable()
    else:
        raise ValueError("Unknown parser")

    asyncio.run(parser.add_to_db())
