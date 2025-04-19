import asyncio
import itertools
from abc import ABCMeta, abstractmethod

import aiohttp


class BaseICD(metaclass=ABCMeta):
    @staticmethod
    async def exception_handler(e):
        print(f"Exception: {e}.\nSleep 2 min before next execution.")
        await asyncio.sleep(120)

    @abstractmethod
    async def get_icd_data(self, session, url):
        """

        :param session:
        :param url:
        :return:
        """

    async def get_all(self, session, url):
        return await self.get_icd_data(session=session, url=url)

    async def run_all(self, session, urls):
        tasks = [self.get_all(session, url) for url in urls]
        result = await asyncio.gather(*tasks)
        return list(itertools.chain(*result))

    async def main(self, urls, step=100):
        result = []
        start = 0

        async with aiohttp.ClientSession() as session:
            print(f"Sleep 30 sec after each request")
            while start < len(urls):
                try:
                    end = min(start + step, len(urls))
                    batch = urls[start:end]
                    nested_result = await self.run_all(session=session, urls=batch)
                    result.append(nested_result)
                    start += step
                    print(f"{min(start, len(urls))}/{len(urls)}")

                    if end != len(urls):
                        await asyncio.sleep(30)

                except Exception as e:
                    await self.exception_handler(e=e)

        return list(itertools.chain(*result))
