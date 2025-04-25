import arrow
from arrow import Arrow
from typing import Type, Callable

from sqlalchemy.orm import Session

from app.db.models.url import UrlsBaseModel
from app.db.models.detail import DetailsBaseModel


class DetailsService:
    """
    Service responsible for updating existing records

    and creating new details in the database

    """

    def __init__(
            self,
            db: Session,
            urls_model: Type[UrlsBaseModel],
            details_model: Type[DetailsBaseModel],
            fetch_method: Callable
    ):
        """
        :param db: current database session
        :param urls_model: model that stores ICD URLs
        :param details_model: model that stores  ICD detailed information
        :param fetch_method: async method to fetch data

        """

        self.db: Session = db
        self.urls_model: Type[UrlsBaseModel] = urls_model
        self.details_model: Type[DetailsBaseModel] = details_model
        self.fetch_method: Callable = fetch_method
        self.updated_at: Arrow = arrow.utcnow()

    async def add_details(self) -> None:
        """
        Check url model for new records and add them to details model

        :return: None

        """

        # check for new icd code in urls model
        new_icd_codes = self.db.query(self.urls_model).filter(
            self.urls_model.created_at == self.urls_model.updated_at
        ).all()

        if new_icd_codes:
            urls = [icd.url for icd in new_icd_codes]

            # fetch new icd details
            icd_details = await self.fetch_method(urls=urls)

            new_details = [
                self.details_model(icd_code=icd["icd_codes"], detail=icd["detail"])
                for icd in icd_details
            ]

            self.db.add_all(new_details)
            self.db.commit()
            print(f"{self.details_model.__name__}: {len(new_details)} added details")

    def update_details(self) -> None:
        """
        Update field 'updated_at' for all records in details model

        :return: None

        """

        # list with updated fields
        data = [
            {"id": detail.id, "updated_at": self.updated_at}
            for detail in self.db.query(self.details_model).all()
        ]

        self.db.bulk_update_mappings(self.details_model, data)
        self.db.commit()
        print(f"{self.details_model.__name__}: {len(data)} updated details")

    async def run(self) -> None:
        """
        Run all methods

        :return: None


        """
        await self.add_details()
        self.update_details()


