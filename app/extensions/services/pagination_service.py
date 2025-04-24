import arrow
from arrow import Arrow
from typing import Type

from sqlalchemy.orm import Session

from app.db.models.pagination import PaginationBaseModel


class PaginationService:
    """
    Service responsible for creating, updating

    and deleting pagination records in the database

    """

    def __init__(
            self,
            db: Session,
            pagination_model: Type[PaginationBaseModel],
            fetch_data: list[str]
    ) -> None:
        """

        :param db: current database session
        :param pagination_model: model that stores pagination data
        :param fetch_data: list of urls to fetch data from

        """

        self.db: Session = db
        self.pagination_model: Type[PaginationBaseModel] = pagination_model
        self.fetch_data: list[str] = fetch_data
        self.updated_at: Arrow = arrow.utcnow()

    def add_pagination(self) -> None:
        """
        Add new URLs if not exists in database

        :return: None

        """

        new_pagination = []
        # set of all pagination URLs
        db_urls = {data[0] for data in self.db.query(self.pagination_model.url).all()}

        # create records if not exist in database
        for url in self.fetch_data:
            if url not in db_urls:
                new_url = self.pagination_model(url=url)
                new_pagination.append(new_url)

        if new_pagination:
            self.db.add_all(new_pagination)
            self.db.commit()
            print(f"{self.pagination_model.__name__}: {len(new_pagination)} added elements")

    def update_pagination(self) -> None:
        """
        Update field "updated_at" for URLs that in fetched data

        :return: None

        """

        self.db.query(self.pagination_model).filter(self.pagination_model.url.in_(
            self.fetch_data)).update({self.pagination_model.updated_at: self.updated_at})

        self.db.commit()
        print(f"{self.pagination_model.__name__}: updated")

    def delete_pagination(self) -> None:
        """
        Delete URLs that was not updated

        :return: None

        """

        data_to_delete = self.db.query(self.pagination_model).filter(
            self.pagination_model.updated_at != self.updated_at).all()

        if data_to_delete:
            for data in data_to_delete:
                self.db.delete(data)

        self.db.commit()

    def run(self) -> None:
        """
        Run all methods

        :return: None

        """

        self.add_pagination()
        self.update_pagination()
        self.delete_pagination()
