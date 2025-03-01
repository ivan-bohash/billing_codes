import asyncio
import aiohttp
from lxml import html
import itertools
from app.config import settings
from app.db.init_db import SessionLocal
from app.db.models.pagination import PaginationModel
from app.db.models.url import UrlModel


class UrlParser:
    headers = settings.headers
    proxy = settings.proxy

    async def get_icd_urls(self, session, url):
        async with session.get(url=url, headers=self.headers, proxy=self.proxy) as r:
            base_urls = []
            response_html = await r.text()

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
            result = await asyncio.gather(*tasks)
            return result


async def main():
    # db = session_local()
    # db_urls = db.query(PaginationModel).all()
    # urls = [db_url.url for db_url in db_urls]
    urls = [
        "https://www.icd10data.com/ICD10CM/Codes/Rules/Billable_Specific_Codes/1",
        "https://www.icd10data.com/ICD10CM/Codes/Rules/Billable_Specific_Codes/2"
    ]
    url_parser = UrlParser()
    nested_result = await url_parser.run_all(urls)
    result = list(itertools.chain(*nested_result))

    return result


def add_to_db():
    with SessionLocal() as db:
        # Get pagination urls from db
        # db_urls = db.query(PaginationModel).all()
        # urls = [db_url.url for db_url in db_urls]

        icd_data = asyncio.run(main())
        db_data = [
            UrlModel(icd_code=data["icd_code"], url=data["url"])
            for data in icd_data
        ]
        db.add_all(db_data)
        db.commit()
        print("Done")


if __name__ == "__main__":
    add_to_db()
