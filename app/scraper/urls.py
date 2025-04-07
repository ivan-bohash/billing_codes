import asyncio
import aiohttp
from lxml import html
import itertools
from app.config import settings
from app.db.init_db import SessionLocal
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
                '//ul[following-sibling::div[@class="ad-unit"]]//a[@class="identifier"]/@href'
            )

            for href in icd_hrefs:
                base_urls.append({
                    "icd_code": href.split('/')[-1],
                    "url": f'https://www.icd10data.com{href}'
                })

        return base_urls

    async def get_all(self, session, url):
        return await self.get_icd_urls(session=session, url=url)

    async def run_all(self, urls):
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_all(session, url) for url in urls]
            result = await asyncio.gather(*tasks)
            return list(itertools.chain(*result))

    async def main(self, urls, step=100):
        result = []
        start = 0

        while start < len(urls):
            try:
                end = min(start + step, len(urls))
                urls_step_slice = urls[start:end]
                nested_result = await self.run_all(urls_step_slice)
                result.append(nested_result)
                start += step
                print(f"{min(start, len(urls))}/{len(urls)}")

                if end != len(urls):
                    print(f"Sleep 30 sec")
                    await asyncio.sleep(30)

            except Exception as e:
                print(f"Exception: {e}.\nSleep 2 min before next execution.")
                await asyncio.sleep(120)

        return list(itertools.chain(*result))

    async def add_to_db(self):
        with SessionLocal() as session:
            db_data = session.query(self.pagination_model).all()
            urls = [data.url for data in db_data]
            icd_data = await self.main(urls=urls)
            db_data = [
                self.url_model(icd_code=data["icd_code"], url=data["url"])
                for data in icd_data
            ]
            session.add_all(db_data)
            session.commit()
            print(f"Done. Added: {len(urls)} items.")


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


