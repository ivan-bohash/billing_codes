import arrow


class DetailsManager:
    def __init__(self, session, urls_model, details_model, fetch_method):
        self.session = session
        self.urls_model = urls_model
        self.details_model = details_model
        self.fetch_method = fetch_method
        self.updated_at = arrow.utcnow()

    async def add_details(self):
        db_data = self.session.query(self.urls_model).filter(
            self.urls_model.created_at == self.urls_model.updated_at
        ).all()

        if db_data:
            urls = [data.url for data in db_data]
            icd_data = await self.fetch_method(urls=urls)

            db_data = [
                self.details_model(icd_code=data["icd_code"], detail=data["detail"])
                for data in icd_data
            ]
            self.session.add_all(db_data)
            self.session.commit()
            print(f"Added {len(db_data)} details")

    def update_details(self):
        data = [
            {"id": detail.id, "updated_at": self.updated_at}
            for detail in self.session.query(self.details_model).all()
        ]

        self.session.bulk_update_mappings(self.details_model, data)
        self.session.commit()
        print(f"Updated {len(data)} details")

    async def run(self):
        await self.add_details()
        self.update_details()
