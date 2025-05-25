from lxml import html
from typing import Type
from aiohttp import ClientSession

from app.config import settings
from app.scraper.base_icd import BaseICD
from app.db.init_db import SessionLocal
from app.services.icd_codes.urls import UrlsService
from app.services.icd_codes.data_parser import DataParser
from app.services.icd_codes.retry_decorator import retry

from app.db.models.pagination import PaginationBaseModel, PaginationBillModel, PaginationNonBillModel
from app.db.models.url import UrlsBaseModel, UrlsBillModel, UrlsNonBillModel
from app.db.models.history import HistoryBaseModel, HistoryBillModel, HistoryNonBillModel


class UrlParser(BaseICD):
    """
    Class for parsing ICD URLs from paginated pages using UrlsManager

    """

    def __init__(self, pagination_model, urls_model, opposite_urls_model, history_model) -> None:
        """
        :param pagination_model: pagination model
        :param urls_model: current url model
        :param opposite_urls_model: url model for opposite category
        :param history_model: model for history information

        """

        self.headers: dict[str] = settings.headers
        self.pagination_model: Type[PaginationBaseModel] = pagination_model
        self.urls_model: Type[UrlsBaseModel] = urls_model
        self.opposite_urls_model: Type[UrlsBaseModel] = opposite_urls_model
        self.history_model: Type[HistoryBaseModel] = history_model

    @retry(max_attempts=5, delay=30)
    async def get_icd_data(self, session: ClientSession, url: str) -> list[dict[str, str]]:
        """
        Async method to fetch URLs from page

        :param session: current aiohttp.ClientSession
        :param url: URL to fetch data from

        :return: list of dictionaries with "icd_codes" and full "url"
        :rtype: list[dict]

        """

        async with session.get(url=url, headers=self.headers) as response:
            if response.status == 200:
                result = []
                response_html = await response.text()
                tree = html.fromstring(response_html)

                # get icd href from page
                icd_hrefs = tree.xpath(
                    '//ul[following-sibling::div[@class="pagination-container"]]//a[@class="identifier"]/@href'
                )

                for href in icd_hrefs:
                    result.append({
                        "icd_code": href.split('/')[-1],
                        "url": f'https://www.icd10data.com{href}'
                    })

                return result
            else:
                raise Exception(f"[{url.split('/')[-1]}] exception")

    async def manage_data(self, action: str) -> None:
        """
        Async method to manage tasks using UrlsManager

        :param action: string describing action (task) ("update" or "delete")
        :return: None

        """

        with SessionLocal() as db:
            url_service = UrlsService(
                db=db,
                pagination_model=self.pagination_model,
                urls_model=self.urls_model,
                opposite_urls_model=self.opposite_urls_model,
                history_model=self.history_model,
                # method from BaseICD
                fetch_method=self.main
            )

            if action == "update":
                await url_service.update_urls()
            elif action == "delete":
                url_service.delete_urls()
            else:
                raise ValueError("Unknown task")


def run_data_parsers(action: str) -> None:
    """
    Pass task and run billable and non-billable parsers

    :param action: Task to run ("update" to fetch and add new ICD, "delete" to remove outdated ICD)
    :return: None

    """

    non_bill_parser = UrlParser(
        pagination_model=PaginationNonBillModel,
        urls_model=UrlsNonBillModel,
        opposite_urls_model=UrlsBillModel,
        history_model=HistoryNonBillModel
    )

    bill_parser = UrlParser(
        pagination_model=PaginationBillModel,
        urls_model=UrlsBillModel,
        opposite_urls_model=UrlsNonBillModel,
        history_model=HistoryBillModel
    )

    data_parser = DataParser(
        bill_parser=bill_parser,
        non_bill_parser=non_bill_parser,
        action=action
    )

    data_parser.run_data_parsers()
