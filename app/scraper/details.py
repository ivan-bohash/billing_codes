import aiohttp
import asyncio
from lxml import html
from sqlalchemy import text
import itertools
import re
from app.config import settings
from app.db.init_db import get_db
from app.db.models.detail import DetailBillModel, DetailNonBillModel
from app.db.models.url import UrlBillModel, UrlNonBillModel


class DetailParser:
    def __init__(self, url_model, detail_model):
        self.headers = settings.headers
        self.url_model = url_model
        self.detail_model = detail_model

    @staticmethod
    async def exception_handler(e):
        print(f"Exception: {e}.\nSleep 2 min before next execution.")
        await asyncio.sleep(120)

    async def get_details(self, session, url):
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

    async def get_all(self, session, url):
        return await self.get_details(session=session, url=url)

    async def run_all(self, urls):
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_all(session, url) for url in urls]
            result = await asyncio.gather(*tasks)
            return list(itertools.chain(*result))

    async def main(self, urls, step=100):
        start = 0
        result = []

        while start < len(urls):
            try:
                end = min(start + step, len(urls))
                details_step_slice = list(urls[start:end])
                result_nested = await self.run_all(details_step_slice)
                result.append(result_nested)
                start += step

                print(f"Sleep 30 sec ({start}/{len(urls)})")
                await asyncio.sleep(30)
            except Exception as e:
                await self.exception_handler(e=e)

        return list(itertools.chain(*result))

    async def add_to_db(self, db=next(get_db()), step=1000):
        with db.connection() as conn:
            db_data = conn.execute(
                text(f"SELECT url FROM {self.url_model.__tablename__}")
            ).fetchall()
            urls = [url[0] for url in db_data]
            start = 0

            while start < len(urls):
                try:
                    end = min(start + step, len(urls))
                    urls_step_slice = urls[start:end]
                    icd_data = await self.main(urls=urls_step_slice)
                    db_data = [
                        self.detail_model(icd_code=data["icd_code"], detail=data["detail"])
                        for data in icd_data
                    ]
                    db.add_all(db_data)
                    db.commit()
                    start += step
                    print(f"Added {end}/{len(urls)} urls. Sleep 30 sec")
                    await asyncio.sleep(30)

                except Exception as e:
                    await self.exception_handler(e=e)


class DetailBillable(DetailParser):
    def __init__(self):
        super().__init__(
            url_model=UrlBillModel,
            detail_model=DetailBillModel
        )


class DetailNonBillable(DetailParser):
    def __init__(self):
        super().__init__(
            url_model=UrlNonBillModel,
            detail_model=DetailNonBillModel
        )


def run_detail_parser(parser_name):
    if parser_name == "billable":
        parser = DetailBillable()
    elif parser_name == "non_billable":
        parser = DetailNonBillable()
    else:
        raise ValueError("Unknown parser")

    asyncio.run(parser.add_to_db())

