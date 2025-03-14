import aiohttp
import asyncio
from lxml import html
import itertools
import re
from app.config import settings
from app.db.init_db import SessionLocal
from app.db.models.detail import DetailBillModel, DetailNonBillModel
from app.db.models.url import UrlBillModel, UrlNonBillModel


class DetailParser:
    headers = settings.headers

    async def get_details(self, session, url):
        async with session.get(url=url, headers=self.headers) as response:

            if response.status != 200:
                print("url: ", url)
                return []
            icd_details = []
            data_text = await response.text()
            link_tree = html.fromstring(data_text)

            icd_code = link_tree.xpath('//div[@class="headingContainer"]//span[@class="identifierDetail"]/text()')[0]
            description_data = link_tree.xpath('//ul/li[span[@class="identifier"]]/text()')
            description_detail = ' '.join(description_data)
            detail = re.sub(r'\s+', ' ', description_detail).strip()

            icd_details.append({"icd_code": icd_code, "detail": detail})

        return icd_details

    async def get_all(self, session, url):
        return await self.get_details(session, url)

    # async def run_all(self, urls, concurrency=20):
        # connector = aiohttp.TCPConnector(limit=concurrency, limit_per_host=10)
        # async with aiohttp.ClientSession(connector=connector) as session:
    async def run_all(self, urls):
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_all(session, url) for url in urls]
            result = await asyncio.gather(*tasks)
            return list(itertools.chain(*result))


async def main(urls, step=100):
    detail_parser = DetailParser()
    result = []

    for i in range(0, len(urls), step):
        details_step = list(urls[i:i + step])
        result_nested = await detail_parser.run_all(details_step)
        result.append(result_nested)

        if i + step < len(urls):
            print("Sleep...")
            await asyncio.sleep(30)

    return list(itertools.chain(*result))


def add_to_db(type):
    with SessionLocal() as db:
        if type == "billable":
            data_list = db.query(UrlBillModel).all()
        elif type == "non_billable":
            data_list = db.query(UrlNonBillModel).all()
        urls = [item.url for item in data_list]

        icd_data = asyncio.run(main(urls=urls))

        if type == "billable":
            db_data = [
                DetailBillModel(icd_code=data["icd_code"], detail=data["detail"])
                for data in icd_data
            ]
        elif type == "non_billable":
            db_data = [
                DetailNonBillModel(icd_code=data["icd_code"], detail=data["detail"])
                for data in icd_data
            ]

        db.add_all(db_data)
        db.commit()
        print(f"Added: {len(urls)} items")
        print("Done")


if __name__ == "__main__":
    add_to_db(type="billable")
