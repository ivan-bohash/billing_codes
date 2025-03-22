import aiohttp
from aiohttp import BasicAuth
import asyncio
from lxml import html
from sqlalchemy import text
import itertools
import re
import math
from app.config import settings
from app.db.init_db import get_db
from app.db.models.detail import DetailBillModel, DetailNonBillModel
from app.db.models.url import UrlBillModel, UrlNonBillModel


class DetailParser:
    def __init__(self, url_model, detail_model):
        self.headers = settings.headers
        self.proxies = settings.proxies
        self.proxy_auth = BasicAuth(
            login=settings.proxy_auth["login"],
            password=settings.proxy_auth["password"]
        )
        self.url_model = url_model
        self.detail_model = detail_model

    async def get_details(self, session, url, proxy):
        async with session.get(
                url=url, headers=self.headers, proxy=proxy, proxy_auth=self.proxy_auth
        ) as response:
            if response.status != 200:
                print(f"Error {proxy}")
            icd_details = []
            data_text = await response.text()
            link_tree = html.fromstring(data_text)

            icd_code = link_tree.xpath('//div[@class="headingContainer"]//span[@class="identifierDetail"]/text()')[0]
            description_data = link_tree.xpath('//ul/li[span[@class="identifier"]]/text()')
            description_detail = ' '.join(description_data)
            detail = re.sub(r'\s+', ' ', description_detail).strip()

            icd_details.append({"icd_code": icd_code, "detail": detail})

        return icd_details

    async def get_all(self, session, url, proxy):
        return await self.get_details(session=session, url=url, proxy=proxy)

    async def run_all(self, urls, proxy):
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_all(session, url, proxy) for url in urls]
            result = await asyncio.gather(*tasks)
            return list(itertools.chain(*result))

    async def main(self, urls, proxy):
        result = []
        step = 20

        for i in range(0, len(urls), step):
            details_step = list(urls[i:i + step])
            result_nested = await self.run_all(details_step, proxy)
            result.append(result_nested)

            if i + step < len(urls):
                print(f"{i}/{len(urls)} {proxy} sleep 10 sec")
                await asyncio.sleep(10)

        return list(itertools.chain(*result))

    async def add_to_db(self, db=next(get_db())):
        with db.connection() as conn:
            # Get urls from db
            db_data = conn.execute(
                text(f"SELECT url FROM {self.url_model.__tablename__}")
            ).fetchall()
            urls_from_db = [url[0] for url in db_data]

            tasks = []
            for i, proxy in enumerate(self.proxies):
                urls_for_proxy = math.ceil(len(urls_from_db) / len(self.proxies))
                end_url = (i + 1) * urls_for_proxy
                start_url = end_url - urls_for_proxy
                urls = urls_from_db[start_url:end_url]
                print(f"Index: {i}, proxy: {proxy}, urls: {len(urls)}")

                task = asyncio.create_task(self.main(urls=urls, proxy=proxy))
                tasks.append(task)

            result = await asyncio.gather(*tasks)
            icd_data = list(itertools.chain(*result))

            db_data = [
                self.detail_model(icd_code=data["icd_code"], detail=data["detail"])
                for data in icd_data
            ]

            db.add_all(db_data)
            db.commit()
            print("Done")


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
#
#
# def run_detail_parser(parser_name):
#     if parser_name == "billable":
#         parser = DetailBillable()
#     elif parser_name == "non_billable":
#         parser = DetailNonBillable()
#     else:
#         raise ValueError("Unknown parser")
#     asyncio.run(parser.add_to_db())


if __name__ == "__main__":
    parser = DetailBillable()
    asyncio.run(parser.add_to_db())
