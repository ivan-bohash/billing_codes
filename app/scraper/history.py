import asyncio
from lxml import html
from typing import Type

from aiohttp import ClientSession

from app.config import settings
from app.db.init_db import SessionLocal
from app.scraper.base_icd import BaseICD
from app.services.icd_codes.history import HistoryService

from app.db.models.url import UrlsBaseModel, UrlsBillModel, UrlsNonBillModel
from app.db.models.history import HistoryBaseModel, HistoryBillModel, HistoryNonBillModel
from app.services.icd_codes.retry_decorator import retry


class HistoryParser(BaseICD):
    """
    Class for parsing ICD code history

    """

    def __init__(
            self,
            urls_model: Type[UrlsBaseModel],
            history_model: Type[HistoryBaseModel]
    ) -> None:
        """
        :param urls_model: url model that stores URLs to parse
        :param history_model: history model where parsed data are saved

        """

        self.headers: dict[str] = settings.headers
        self.urls_model: Type[UrlsBaseModel] = urls_model
        self.history_model: Type[HistoryBaseModel] = history_model

    @retry(max_attempts=5, delay=30)
    async def get_icd_data(self, session: ClientSession, url: str) -> list[dict[str, str]]:
        """
        Method to fetch code history from given URL

        :param session: current aiohttp.ClientSession
        :param url: url to fetch data from

        :return: list of dictionaries with "icd_codes" and "code_history"
        :rtype: list[dict]

        """

        async with session.get(url=url, headers=self.headers) as response:
            if response.status == 200:
                result = []
                history = []
                response_html = await response.text()
                tree = html.fromstring(response_html)

                icd_code = url.split('/')[-1]

                # code history
                code_history = tree.xpath(
                    '//div[@class="body-content"]//span[text()="Code History"]/following::ul[1]//text()'
                )
                data = [item.strip() for item in code_history if item.strip()]

                for i in range(0, len(data)):
                    if "effective" in data[i]:
                        year = data[i - 1]
                        effective_date = data[i].split()[1][:-1]
                        description = data[i + 1][2:]

                        result_dict = {
                            "year": year,
                            "effective_date": effective_date,
                            "description": description
                        }

                        history.append(result_dict)

                    # if revised - modify result_dict["description"]
                    elif "Revised code" in data[i]:
                        revised_code = data[i].split(': ')[1]
                        # split revised data
                        new_description = data[i + 1].split(': ')
                        old_description = data[i + 2].split(': ')

                        revised_data = {
                            new_description[0]: new_description[1],
                            old_description[0]: old_description[1]
                        }

                        # change description
                        result_dict["description"] = {
                            revised_code: revised_data
                        }

                result.append({"icd_code": icd_code, "history": history})

                return result
            else:
                raise Exception(f"[{url.split('/')[-1]}]")

    async def manage_data(self) -> None:
        """
        Async method to manage fetching data using HistoryManager

        """
        with SessionLocal() as db:
            history_service = HistoryService(
                db=db,
                urls_model=self.urls_model,
                history_model=self.history_model,
                # method from BaseICD
                fetch_method=self.main
            )

            await history_service.run()


def run_data_parsers() -> None:
    """
    Method to run non-billable and billable parsers

    :return: None

    """

    non_billable_parser = HistoryParser(
        urls_model=UrlsNonBillModel,
        history_model=HistoryNonBillModel
    )

    billable_parser = HistoryParser(
        urls_model=UrlsBillModel,
        history_model=HistoryBillModel
    )

    async def run_parsers():
        await non_billable_parser.manage_data()
        await billable_parser.manage_data()

    asyncio.run(run_parsers())
