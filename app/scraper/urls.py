from sqlalchemy import text
import asyncio
import aiohttp
from lxml import html
import itertools
from app.config import settings
from app.db.init_db import get_db
from app.db.models.pagination import PaginationBillModel, PaginationNonBillModel
from app.db.models.url import UrlBillModel, UrlNonBillModel


class UrlParser:
    def __init__(self, pagination_model, url_model):
        self.headers = settings.headers
        self.pagination_model = pagination_model
        self.url_model = url_model

    async def get_icd_urls(self, session, url):
        async with session.get(url=url, headers=self.headers) as response:
            base_urls = []
            response_html = await response.text()
            tree = html.fromstring(response_html)
            icd_hrefs = tree.xpath(
                '//ul[following-sibling::div[@class="proper-ad-unit"]]//a[@class="identifier"]/@href'
            )

            for href in icd_hrefs:
                base_urls.append({
                    "icd_code": href.split('/')[-1],
                    "url": f'https://www.icd10data.com{href}'
                })
        return base_urls

    async def get_all(self, session, url):
        return await self.get_icd_urls(session, url)

    async def run_all(self, urls):
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_all(session, url) for url in urls]
            gather_tasks = await asyncio.gather(*tasks)
            return list(itertools.chain(*gather_tasks))

    async def main(self, urls, step=100):
        result = []

        for i in range(0, len(urls), step):
            urls_step = urls[i:i + step]
            nested_result = await self.run_all(urls_step)
            result.append(nested_result)

            if i + step < len(urls):
                print(i + step)
                print("Sleep...")
                await asyncio.sleep(30)

        return list(itertools.chain(*result))

    async def add_to_db(self, db=next(get_db())):
        with db.connection() as conn:
            db_data = conn.execute(text(
                f"SELECT url FROM {self.pagination_model.__tablename__}"
            )).fetchall()
            urls = [url[0] for url in db_data]
            print(f"Hello form URLS: len {len(urls)}")

            # icd_data = await self.main(urls=urls)
            #
            # db_data = [
            #     self.url_model(icd_code=data["icd_code"], url=data["url"])
            #     for data in icd_data
            # ]
            #
            # db.add_all(db_data)
            # db.commit()
            # print(f"Added: {len(urls)} items")
            # print("Done")


class UrlBillable(UrlParser):
    def __init__(self):
        super().__init__(
            pagination_model=PaginationBillModel,
            url_model=UrlBillModel
        )


class UrlNonBillable(UrlParser):
    def __init__(self):
        super().__init__(
            pagination_model=PaginationNonBillModel,
            url_model=UrlNonBillModel
        )


def run_url_parser(parser_name):
    if parser_name == "billable":
        parser = UrlBillable()
    elif parser_name == "non_billable":
        parser = UrlNonBillable()
    else:
        raise ValueError("Unknown parser")

    asyncio.run(parser.add_to_db())


