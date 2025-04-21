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
    """
    Class for parsing ICD URLs from paginated pages using UrlsManager

    """

    def __init__(self, pagination_model, urls_model, opposite_urls_model, details_model):
        """
        :param pagination_model: pagination model
        :param urls_model: current url model
        :param opposite_urls_model: url model for opposite category
        :param details_model: model for detailed information

        """

        self.headers = settings.headers
        self.pagination_model = pagination_model
        self.urls_model = urls_model
        self.opposite_urls_model = opposite_urls_model
        self.details_model = details_model

    async def get_icd_data(self, session, url):
        """
        Async method to fetch URLs from page

        :param session: current aiohttp.ClientSession
        :param url: URL to fetch data from

        :return: list of dictionaries with "icd_code" and full "url"
        :rtype: list[dict]

        """

        while True:
            async with session.get(url=url, headers=self.headers) as response:
                if response.status == 200:
                    base_urls = []
                    response_html = await response.text()
                    tree = html.fromstring(response_html)

                    # get icd href from page
                    icd_hrefs = tree.xpath(
                        '//ul[following-sibling::div[@class="ad-unit"]]//a[@class="identifier"]/@href'
                    )

                    for href in icd_hrefs:
                        base_urls.append({
                            "icd_code": href.split('/')[-1],
                            "url": f'https://www.icd10data.com{href}'
                        })

                    return base_urls

                else:
                    print(f"Error: icd({url.split('/')[-1]}). Sleep 30 sec")
                    await asyncio.sleep(30)

    async def manage_urls(self, task):
        """
        Async method to manage tasks using UrlsManager

        :param task: string describing task ("update" or "delete")
        :return: None

        """
        with SessionLocal() as db:
            icd_manager = UrlsManager(
                db=db,
                pagination_model=self.pagination_model,
                urls_model=self.urls_model,
                opposite_urls_model=self.opposite_urls_model,
                details_model=self.details_model,

                # method from BaseICD
                fetch_method=self.main
            )

            if task == "update":
                await icd_manager.update_urls()
            elif task == "delete":
                icd_manager.delete_urls()
            else:
                raise ValueError("Unknown task")


class UrlsNonBillable(UrlParser):
    """Parser for non-billable ICD"""

    def __init__(self):
        super().__init__(
            pagination_model=PaginationNonBillModel,
            urls_model=UrlsNonBillModel,
            opposite_urls_model=UrlsBillModel,
            details_model=DetailsNonBillModel
        )


class UrlsBillable(UrlParser):
    """Parser for billable ICD"""
    def __init__(self):
        super().__init__(
            pagination_model=PaginationBillModel,
            urls_model=UrlsBillModel,
            opposite_urls_model=UrlsNonBillModel,
            details_model=DetailsBillModel,
        )


def run_urls_parser(task):
    """
    Pass task and run billable and non-billable parsers

    :param task: Task to run ("update" to fetch and add new ICD, "delete" to remove outdated ICD)
    :return: None

    """

    non_billable_parser = UrlsNonBillable()
    billable_parser = UrlsBillable()

    async def run_parsers():
        await non_billable_parser.manage_urls(task)

        # extra sleep to avoid server blocking
        await asyncio.sleep(10)
        await billable_parser.manage_urls(task)

    asyncio.run(run_parsers())
