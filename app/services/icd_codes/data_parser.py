import asyncio


class DataParser:
    """
    Class responsible for async run of billable and non-billable parsers

    """

    def __init__(self, non_bill_parser, bill_parser, action=None):
        self.non_bill_parser = non_bill_parser
        self.bill_parser = bill_parser
        self.action = action

    def run_data_parsers(self) -> None:
        async def run_parsers():
            if self.action:
                await self.non_bill_parser.manage_data(self.action)
                await self.bill_parser.manage_data(self.action)
            else:
                await self.non_bill_parser.manage_data()
                await self.bill_parser.manage_data()

        asyncio.run(run_parsers())
