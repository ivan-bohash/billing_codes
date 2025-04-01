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
        return await self.get_icd_urls(session=session, url=url)

    async def run_all(self, urls):
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_all(session, url) for url in urls]
            result = await asyncio.gather(*tasks)
            return list(itertools.chain(*result))

    async def main(self, urls, step=100):
        result = []

        for i in range(0, len(urls), step):
            urls_step = urls[i:i + step]
            nested_result = await self.run_all(urls_step)
            result.append(nested_result)

            if i + step < len(urls):
                print(f"{i + step}/{len(urls)}")
                print(f"Sleep 30 sec")
                await asyncio.sleep(30)

        return list(itertools.chain(*result))

    async def add_to_db(self, db=next(get_db())):
        with db.connection() as conn:
            db_data = conn.execute(text(
                f"SELECT url FROM {self.pagination_model.__tablename__}"
            )).fetchall()
            urls = [url[0] for url in db_data][:10]
            icd_data = await self.main(urls=urls)

            db_data = [
                self.url_model(icd_code=data["icd_code"], url=data["url"])
                for data in icd_data
            ]

            db.add_all(db_data)
            db.commit()
            print(f"Done. Added: {len(urls)} items.")

            # Check data difference between db and fetched data
            # db data set
            db_urls = conn.execute(text(
                f"SELECT url FROM {UrlBillModel.__tablename__}"
            )).fetchall()
            db_urls_set = {db_url[0] for db_url in db_urls[:15]}
            # fetched data set
            fetch_urls_set = {data["url"] for data in icd_data[:10]}

            print(f"Difference: {db_urls_set.symmetric_difference(fetch_urls_set)}")

            # for db_url in db_urls:
            #     if db_url[0] in icd_urls:
            #         print(f"Url {db_url} exists")
            # else:
            #     print(f"Not {db_url} exists")

            # url_exists = db.query(exists().where(self.url_model.url == data["url"])).scalar()
            # if url_exists:
            #     print("Exists")
            # else:
            #     print(f"Url: {data} does not exist")


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

#
# def check_exists():
#     url_to_check = "https://www.icd10data.com/ICD10CM/Codes/A00-B99/A50-A64/A52-/A52.10"
#     with SessionLocal() as session:
#         url_exists = session.query(exists().where(UrlBillModel.url == url_to_check)).scalar()
#
#     if url_exists:
#         print('User exists!')
#         print(url_exists)
#     else:
#         print('User does not exist.')

#
# if __name__ == "__main__":
#     parser = UrlBillable()
#     asyncio.run(parser.add_to_db())
