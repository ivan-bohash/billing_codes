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
    def __init__(self, url_model, detail_model):
        self.headers = settings.headers
        self.url_model = url_model
        self.detail_model = detail_model

    async def get_details(self, session, url):
        async with session.get(url=url, headers=self.headers) as response:
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

    async def run_all(self, urls):
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_all(session, url) for url in urls]
            result = await asyncio.gather(*tasks)
            return list(itertools.chain(*result))

    async def main(self, urls, step=100):
        result = []

        for i in range(0, len(urls), step):
            details_step = list(urls[i:i + step])
            result_nested = await self.run_all(details_step)
            result.append(result_nested)

            if i + step < len(urls):
                print("Sleep...")
                await asyncio.sleep(30)

        return list(itertools.chain(*result))

    async def add_to_db(self):
        with SessionLocal() as db:
            data_list = db.query(self.url_model).all()
            urls = [item.url for item in data_list][:10]

            icd_data = await self.main(urls=urls)
            db_data = [
                self.detail_model(icd_code=data["icd_code"], detail=data["detail"])
                for data in icd_data
            ]

            db.add_all(db_data)
            db.commit()
            print(f"Added: {len(urls)} items")
            print("Done")


class DetailParserBill(DetailParser):
    def __init__(self):
        super().__init__(
            url_model=UrlBillModel,
            detail_model=DetailBillModel
        )


class DetailParserNonBill(DetailParser):
    def __init__(self):
        super().__init__(
            url_model=UrlNonBillModel,
            detail_model=DetailNonBillModel
        )


def run_detail_parser(parser_name):
    if parser_name == "billable":
        parser = DetailParserBill()
    elif parser_name == "non_billable":
        parser = DetailParserNonBill()
    else:
        raise ValueError("Unknown parser")

    asyncio.run(parser.add_to_db())
