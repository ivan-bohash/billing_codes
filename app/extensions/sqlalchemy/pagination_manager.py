import arrow


class PaginationManager:
    def __init__(self, session, pagination_model, fetch_data):
        self.session = session
        self.pagination_model = pagination_model
        self.fetch_data = fetch_data
        self.updated_at = arrow.utcnow()

    def add_pagination(self):
        new_pagination = []
        db_urls = {data[0] for data in self.session.query(self.pagination_model.url).all()}

        for url in self.fetch_data:
            if url not in db_urls:
                new_url = self.pagination_model(url=url)
                new_pagination.append(new_url)

        if new_pagination:
            self.session.add_all(new_pagination)
            self.session.commit()
            print(f"{self.pagination_model.__name__}: {len(new_pagination)} added elements")

    def update_pagination(self):
        self.session.query(self.pagination_model).filter(self.pagination_model.url.in_(
            self.fetch_data)).update({self.pagination_model.updated_at: self.updated_at})

        self.session.commit()
        print(f"{self.pagination_model.__name__}: updated")

    def delete_pagination(self):
        data_to_delete = self.session.query(self.pagination_model).filter(
            self.pagination_model.updated_at != self.updated_at).all()

        if data_to_delete:
            for data in data_to_delete:
                self.session.delete(data)

        self.session.commit()

    def run(self):
        self.add_pagination()
        self.update_pagination()
        self.delete_pagination()
