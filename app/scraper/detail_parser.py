import aiohttp
import asyncio
from lxml import html
import itertools
import re
from app.config import settings
from app.db.init_db import SessionLocal
from app.db.models.detail import DetailModel
from app.db.models.url import UrlModel


class DetailParser:
    headers = settings.headers
    proxy = settings.proxy

    async def get_detail(self, session, url):
        async with session.get(url=url, headers=self.headers, proxy=self.proxy) as r:
            icd_details = []
            # print("status: ", r.status)
            # print("url: ", url)
            data_text = await r.text()
            link_tree = html.fromstring(data_text)

            icd_code = link_tree.xpath('//div[@class="headingContainer"]//span[@class="identifierDetail"]/text()')[0]
            description_data = link_tree.xpath('//ul/li[span[@class="identifier"]]/text()')
            description_detail = ' '.join(description_data)
            detail = re.sub(r'\s+', ' ', description_detail).strip()

            icd_details.append({"icd_code": icd_code, "detail": detail})

        return icd_details

    async def get_all(self, session, url):
        return await self.get_detail(session, url)

    async def run_all(self, urls):
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_all(session, url) for url in urls]
            result = await asyncio.gather(*tasks)
            return result


async def main(urls):
    detail_parser = DetailParser()
    result_nested = await detail_parser.run_all(urls)
    result = list(itertools.chain(*result_nested))

    return result


def add_to_db():
    # urls = [
    #     "https://www.icd10data.com/ICD10CM/Codes/A00-B99/A00-A09/A00-/A00.0",
    #     "https://www.icd10data.com/ICD10CM/Codes/A00-B99/A00-A09/A00-/A00.1"
    # ]

    with SessionLocal() as db:
        # Get icd urls from db
        data_list = db.query(UrlModel).all()
        urls = [item.url for item in data_list]

        icd_data = asyncio.run(main(urls=urls))
        db_data = [
            DetailModel(icd_code=data["icd_code"], detail=data["detail"])
            for data in icd_data
        ]
        db.add_all(db_data)
        db.commit()
        print("Done")


if __name__ == "__main__":
    add_to_db()
