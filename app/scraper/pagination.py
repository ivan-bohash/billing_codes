import aiohttp
import asyncio
from lxml import html
from typing import Type

from app.db.init_db import SessionLocal
from app.config import settings
from app.services.icd_codes.pagination import PaginationService

from app.db.models.pagination import PaginationBaseModel, PaginationBillModel, PaginationNonBillModel


class PaginationParser:
    def __init__(
            self,
            base_url: str,
            pagination_model: Type[PaginationBaseModel]
    ) -> None:
        """
        :param base_url: base URL to parse pagination data from
        :param pagination_model: model to manage pagination data

        """

        self.headers: dict[str] = settings.headers
        self.base_url: str = base_url
        self.pagination_model: Type[PaginationBaseModel] = pagination_model

    async def extract_pagination_urls(self) -> list[str]:
        """
        Method to create list of URLs.

        Depends on number of last page of base url

        :return: List of pagination URLs
        :rtype: list[str]

        """

        attempt = 1
        max_attempt = 5

        async with aiohttp.ClientSession() as session:
            while attempt <= max_attempt:
                async with session.get(url=self.base_url, headers=self.headers) as response:
                    if response.status == 200:
                        response_html = await response.text()
                        tree = html.fromstring(response_html)

                        # get last index from URL
                        last_index: int = int(
                            tree.xpath('//ul[@class="pagination"]/li[@class="PagedList-skipToLast"]/a/@href')
                            [0].split('/')[-1]
                        )

                        # create list of URLs
                        urls: list[str] = [f"{self.base_url}{i}" for i in range(1, last_index + 1)]

                        return urls
                    else:
                        print(f"[{self.base_url.split('/')[-2]}] exception: sleep 30 sec")
                        attempt += 1
                        await asyncio.sleep(30)

            raise Exception("Max retries")

    async def manage_pagination(self) -> None:
        """
        Method to fetch and save URLs to database

        :return: None

        """

        with SessionLocal() as db:
            # fetch pagination URLs
            fetch_data: list[str] = await self.extract_pagination_urls()

            pagination_service = PaginationService(
                db=db,
                pagination_model=self.pagination_model,
                fetch_data=fetch_data
            )

            pagination_service.run()


class PaginationNonBillable(PaginationParser):
    """
    Parser for non-billable ICD

    """

    def __init__(self) -> None:
        super().__init__(
            base_url=settings.non_billable_url,
            pagination_model=PaginationNonBillModel
        )


class PaginationBillable(PaginationParser):
    """
    Parser for billable ICD

    """

    def __init__(self) -> None:
        super().__init__(
            base_url=settings.billable_url,
            pagination_model=PaginationBillModel
        )


def run_pagination_parser() -> None:
    """
    Run billable and non-billable parsers

    :return: None

    """

    non_billable_parser = PaginationNonBillable()
    billable_parser = PaginationBillable()

    async def run_pagination():
        await non_billable_parser.manage_pagination()
        await billable_parser.manage_pagination()

    asyncio.run(run_pagination())
