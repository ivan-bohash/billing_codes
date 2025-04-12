import arrow


class PaginationManager:
    def __init__(self, session, model, fetch_data):
        self.session = session
        self.model = model
        self.fetch_data = fetch_data
        self.updated_at = arrow.utcnow()

    def update_pagination(self):
        self.session.query(self.model).filter(self.model.url.in_(
            self.fetch_data)).update({self.model.updated_at: self.updated_at})

        self.session.commit()
        print("Pagination updated")

    def delete_pagination(self):
        data_to_delete = self.session.query(self.model).filter(
            self.model.updated_at != self.updated_at).all()

        if data_to_delete:
            for data in data_to_delete:
                self.session.delete(data)

        self.session.commit()

    def run(self):
        self.update_pagination()
        self.delete_pagination()
