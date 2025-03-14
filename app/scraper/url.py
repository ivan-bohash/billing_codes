import asyncio
import aiohttp
from lxml import html
import itertools
from app.config import settings
from app.db.init_db import SessionLocal
from app.db.models.pagination import PaginationBillModel, PaginationNonBillModel
from app.db.models.url import UrlBillModel, UrlNonBillModel


class UrlParser:
    headers = settings.headers

    async def get_icd_urls(self, session, url):
        async with session.get(url=url, headers=self.headers) as response:
            print(response.status)
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
        print(base_urls)
        return base_urls

    async def get_all(self, session, url):
        return await self.get_icd_urls(session, url)

    async def run_all(self, urls):
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_all(session, url) for url in urls]
            gather_tasks = await asyncio.gather(*tasks)
            return list(itertools.chain(*gather_tasks))


async def main(urls, step=100):
    url_parser = UrlParser()
    result = []

    for i in range(0, len(urls), step):
        urls_step = urls[i:i + step]
        nested_result = await url_parser.run_all(urls_step)
        result.append(nested_result)

        if i + step < len(urls):
            print(i + step)
            print("Sleep...")
            await asyncio.sleep(30)

    return list(itertools.chain(*result))


def add_to_db(type):
    with SessionLocal() as db:
        if type == "billable":
            db_urls = db.query(PaginationBillModel).all()
        elif type == "non_billable":
            db_urls = db.query(PaginationNonBillModel).all()

        urls = [db_url.url for db_url in db_urls]
        icd_data = asyncio.run(main(urls))

        if type == "billable":
            db_data = [
                UrlBillModel(icd_code=data["icd_code"], url=data["url"])
                for data in icd_data
            ]
        elif type == "non_billable":
            db_data = [
                UrlNonBillModel(icd_code=data["icd_code"], url=data["url"])
                for data in icd_data
            ]

        db.add_all(db_data)
        db.commit()
        print(f"Added: {len(urls)} items")
        print("Done")


if __name__ == "__main__":
    add_to_db(type="non_billable")
