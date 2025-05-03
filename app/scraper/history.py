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

    async def get_icd_data(self, session: ClientSession, url: str) -> list[dict[str, str]]:
        """
        Method to fetch code history from given URL

        :param session: current aiohttp.ClientSession
        :param url: url to fetch data from

        :return: list of dictionaries with "icd_codes" and "code_history"
        :rtype: list[dict]

        """
        while True:
            async with session.get(url=url, headers=self.headers) as response:
                if response.status == 200:
                    icd_history = []
                    response_html = await response.text()
                    tree = html.fromstring(response_html)

                    icd_code = url.split('/')[-1]

                    # code history
                    history = tree.xpath(
                        '//div[@class="body-content"]//span[text()="Code History"]/following::ul[1]//text()'
                    )
                    data = [item.strip() for item in history if item.strip()]

                    temp_str = ''

                    for i in range(0, len(data)):
                        if "effective" in data[i]:
                            temp_str += '{' + f"{data[i - 1]} {data[i]}{data[i + 1]}" + '}, '
                        elif "Revised code" in data[i]:
                            temp_str = temp_str.strip()[:-2] + '.' + f" {data[i+1]}; {data[i+2]}" + '}, '

                    code_history = temp_str.strip()[:-1]
                    icd_history.append({"icd_code": icd_code, "code_history": code_history})

                    return icd_history

                else:
                    print(f"[{url.split('/')[-1]}] exception. Sleep 30 seconds")
                    await asyncio.sleep(30)

    async def manage_history(self) -> None:
        """
        Async method to manage fetching data using HistoryManager

        """
        with SessionLocal() as db:
            history_service = HistoryService(
                db=db,
                urls_model=self.urls_model,
                history_model=self.history_model,
                fetch_method=self.main
            )

            await history_service.run()


class HistoryNonBillable(HistoryParser):
    """
    Parser for non-billable ICD

    """

    def __init__(self) -> None:
        super().__init__(
            urls_model=UrlsNonBillModel,
            history_model=HistoryNonBillModel
        )


class HistoryBillable(HistoryParser):
    """
    Parser for billable ICD

    """

    def __init__(self) -> None:
        super().__init__(
            urls_model=UrlsBillModel,
            history_model=HistoryBillModel
        )


def run_history_parser() -> None:
    """
    Method to run non-billable and billable parsers

    :return: None

    """

    non_billable_parser = HistoryNonBillable()
    billable_parser = HistoryBillable()

    async def run_parsers():
        await non_billable_parser.manage_history()
        await billable_parser.manage_history()

    asyncio.run(run_parsers())
