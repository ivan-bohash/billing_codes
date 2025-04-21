import requests
from lxml import html
from app.db.init_db import SessionLocal
from app.config import settings
from app.db.models.pagination import PaginationBillModel, PaginationNonBillModel
from app.extensions.sqlalchemy.pagination_manager import PaginationManager


class PaginationParser:
    def __init__(self, base_url, pagination_model):
        """
        :param base_url: base URL to parse pagination data from
        :param pagination_model: model to manage pagination data

        """

        self.headers = settings.headers
        self.base_url = base_url
        self.pagination_model = pagination_model

    def extract_pagination_urls(self):
        """
        :return: List of pagination URLs
        :rtype: list[str]

        """

        response_html = requests.get(url=self.base_url, headers=self.headers).content
        tree = html.fromstring(response_html)

        # get last index from URL
        last_index = int(
            tree.xpath('//ul[@class="pagination"]/li[@class="PagedList-skipToLast"]/a/@href')[0].split('/')[-1]) + 1

        # create list of URLs
        urls = [f"{self.base_url}{i}" for i in range(1, last_index)]

        return urls

    def manage_pagination(self):
        """
        :return: None

        """
        with SessionLocal() as db:
            # fetch pagination URLs
            urls = self.extract_pagination_urls()

            pagination_manager = PaginationManager(
                db=db,
                pagination_model=self.pagination_model,

                # pass pagination URLs to pagination manager
                fetch_data=urls
            )

            pagination_manager.run()


class PaginationNonBillable(PaginationParser):
    """
    Parser for non-billable ICD
    """
    def __init__(self):
        super().__init__(
            base_url=settings.non_billable_url,
            pagination_model=PaginationNonBillModel
        )


class PaginationBillable(PaginationParser):
    """
    Parser for billable ICD
    """
    def __init__(self):
        super().__init__(
            base_url=settings.billable_url,
            pagination_model=PaginationBillModel
        )


def run_pagination_parser():
    """
    Run billable and non-billable parsers

    :return: None

    """

    non_billable_parser = PaginationNonBillable()
    billable_parser = PaginationBillable()

    non_billable_parser.manage_pagination()
    billable_parser.manage_pagination()


