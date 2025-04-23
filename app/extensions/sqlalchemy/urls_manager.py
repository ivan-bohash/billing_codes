import arrow
from arrow import Arrow
from typing import Type, Callable

from sqlalchemy.orm import Session

from app.db.models.pagination import PaginationBaseModel
from app.db.models.url import UrlsBaseModel
from app.db.models.detail import DetailsBaseModel


class UrlsManager:
    """
    Manager responsible for updating, creating records

    and deleting urls with associated details in the database

    """

    def __init__(
            self,
            db: Session,
            pagination_model: Type[PaginationBaseModel],
            urls_model: Type[UrlsBaseModel],
            opposite_urls_model: Type[UrlsBaseModel],
            details_model: Type[DetailsBaseModel],
            fetch_method: Callable
    ) -> None:

        """
        :param db: current database session
        :param pagination_model: model that stores pagination links
        :param urls_model: model that stores urls and icd_code
        :param opposite_urls_model: opposite model to check records
        :param details_model: model that stores ICD detailed information
        :param fetch_method: async method to fetch data

        """

        self.db: Session = db
        self.pagination_model: Type[PaginationBaseModel] = pagination_model
        self.urls_model: Type[UrlsBaseModel] = urls_model
        self.opposite_urls_model: Type[UrlsBaseModel] = opposite_urls_model
        self.details_model: Type[DetailsBaseModel] = details_model
        self.fetch_method: Callable = fetch_method
        self.updated_at: Arrow = arrow.utcnow()

    async def update_urls(self) -> None:
        """
        Fetches URLs data, update or add new records

        :return: None

        """

        # get all pagination URLs from database
        urls = [icd.url for icd in self.db.query(self.pagination_model.url).all()]

        # fetch URLs data
        fetched_data = await self.fetch_method(urls=urls)

        def update() -> None:
            """
            Update field "updated_at" for records that exist in database

            :return: None

            """

            # create dict from urls model data
            db_urls = {
                url.icd_code: url.id
                for url in self.db.query(self.urls_model).all()
            }

            if db_urls:
                # update only existing in database records
                data = [
                    {"id": db_urls.get(icd["icd_code"]), "updated_at": self.updated_at}
                    for icd in fetched_data
                ]

                self.db.bulk_update_mappings(self.urls_model, data)
                self.db.commit()

                print(f"{self.urls_model.__name__}: {len(data)} updated elements")

        def add_new() -> None:
            """
            Add new records if they don't exist to the database

            :return: None

            """

            # get all icd codes from urls model
            db_icd_codes = {data.icd_code for data in self.db.query(self.urls_model.icd_code).all()}
            new_icd_codes = []

            for data in fetched_data:
                # add only if icd doesn't exist in database
                if data["icd_code"] not in db_icd_codes:
                    icd = self.urls_model(icd_code=data["icd_code"], url=data["url"])
                    new_icd_codes.append(icd)

            if new_icd_codes:
                self.db.add_all(new_icd_codes)
                self.db.commit()
                print(f"{self.urls_model.__name__}: {len(new_icd_codes)} added elements")

        update()
        add_new()

    def delete_urls(self) -> None:
        """
        Delete outdated ICD from database and remove ICD from details model

        :return: None

        """

        # check outdated ICD exists in the opposite model
        urls_to_delete = (self.db.query(self.urls_model).
                          filter(self.urls_model.updated_at != self.updated_at).
                          filter(self.urls_model.icd_code.in_(self.db.query(self.opposite_urls_model.icd_code))
                                 )).all()

        if urls_to_delete:
            for url in urls_to_delete:
                self.db.delete(url)

            # delete ICD from details model
            urls_icd_code = [url.icd_code for url in urls_to_delete]

            for icd_code in urls_icd_code:
                detail = (self.db.query(self.details_model).
                          filter(self.details_model.icd_code == icd_code).
                          one_or_none())

                self.db.delete(detail)

            self.db.commit()

            print(f"{self.urls_model.__name__}, {self.details_model.__name__}: deleted {len(urls_to_delete)} elements")
