import asyncio
from lxml import html
import re

from app.config import settings
from app.db.init_db import SessionLocal
from app.scraper.base_icd import BaseICD

from app.db.models.detail import DetailsBillModel, DetailsNonBillModel
from app.db.models.url import UrlsBillModel, UrlsNonBillModel
from app.extensions.sqlalchemy.details_manager import DetailsManager


class DetailParser(BaseICD):
    """
    Class for parsing ICD detailed information using DetailsManager

    """

    def __init__(self, urls_model, details_model):
        """
        :param urls_model: url model that stores URLs to parse
        :param details_model: details model where parsed data are saved

        """

        self.headers = settings.headers
        self.urls_model = urls_model
        self.details_model = details_model

    async def get_icd_data(self, session, url):
        """
        Async method to fetch detailed ICD information from given URL

        :param session: current aiohttp.ClientSession
        :param url: url to fetch data from

        :return: list of dictionaries with "icd_code" and "detail" with detailed information
        :rtype: list[dict]

        """

        async with session.get(url=url, headers=self.headers) as response:

            icd_details = []
            response_html = await response.text()
            tree = html.fromstring(response_html)

            # fetch icd code
            icd_code = tree.xpath('//div[@class="headingContainer"]//span[@class="identifierDetail"]/text()')[0]

            # fetch icd details
            description_data = tree.xpath('//ul/li[span[@class="identifier"]]/text()')

            # reformat details text
            description_detail = ' '.join(description_data)
            detail = re.sub(r'\s+', ' ', description_detail).strip()

            icd_details.append({"icd_code": icd_code, "detail": detail})

        return icd_details

    async def manage_details(self):
        """
        Async method to manage fetching using DetailsManager

        """
        with SessionLocal() as db:
            details_manager = DetailsManager(
                db=db,
                urls_model=self.urls_model,
                details_model=self.details_model,
                fetch_method=self.main
            )

            await details_manager.run()


class DetailsNonBillable(DetailParser):
    """
    Parser for non-billable ICD

    """

    def __init__(self):
        super().__init__(
            urls_model=UrlsNonBillModel,
            details_model=DetailsNonBillModel
        )


class DetailsBillable(DetailParser):
    """
    Parser for billable ICD

    """
    def __init__(self):
        super().__init__(
            urls_model=UrlsBillModel,
            details_model=DetailsBillModel
        )


def run_details_parser():
    """
    Method to run non-billable and billable parsers

    """

    non_billable_parser = DetailsNonBillable()
    billable_parser = DetailsBillable()

    async def run_parsers():
        await non_billable_parser.manage_details()
        await billable_parser.manage_details()

    asyncio.run(run_parsers())


