import arrow
from arrow import Arrow
from typing import Type, Callable

from sqlalchemy.orm import Session

from app.db.models.url import UrlsBaseModel
from app.db.models.history import HistoryBaseModel


class HistoryService:
    """
    Service responsible for updating existing records

    and creating new code history in the database

    """

    def __init__(
            self,
            db: Session,
            urls_model: Type[UrlsBaseModel],
            history_model: Type[HistoryBaseModel],
            fetch_method: Callable
    ):
        """
        :param db: current database session
        :param urls_model: model that stores ICD URLs
        :param history_model: model that stores ICD code history
        :param fetch_method: async method to fetch data

        """

        self.db: Session = db
        self.urls_model: Type[UrlsBaseModel] = urls_model
        self.history_model: Type[HistoryBaseModel] = history_model
        self.fetch_method: Callable = fetch_method
        self.updated_at: Arrow = arrow.utcnow()

    async def add_history(self) -> None:
        """
        Check url model for new records and add them to history model

        :return: None

        """

        # check for new icd code in urls model
        new_icd_codes = self.db.query(self.urls_model).filter(
            self.urls_model.created_at == self.urls_model.updated_at
        ).all()

        if new_icd_codes:
            urls = [icd.url for icd in new_icd_codes]

            # fetch new icd code history
            icd_history = await self.fetch_method(urls=urls)

            # create dict to have access to urls.id
            urls_id = {
                new_icd.icd_code: new_icd.id
                for new_icd in new_icd_codes
            }

            new_history = [
                self.history_model(
                    icd_code=icd["icd_code"],
                    history=icd["code_history"],
                    url_id=urls_id.get(icd["icd_code"])
                )
                for icd in icd_history
            ]

            self.db.add_all(new_history)
            self.db.commit()
            print(f"{self.history_model.__name__}: {len(new_history)} added records")

    def update_history(self) -> None:
        """
        Update field 'updated_at' for all records in history model

        :return: None

        """

        # list with updated fields
        data = [
            {"id": icd.id, "updated_at": self.updated_at}
            for icd in self.db.query(self.history_model).all()
        ]

        self.db.bulk_update_mappings(self.history_model, data)
        self.db.commit()
        print(f"{self.history_model.__name__}: {len(data)} updated records")

    async def run(self) -> None:
        """
        Run all methods

        :return: None

        """

        await self.add_history()
        self.update_history()


