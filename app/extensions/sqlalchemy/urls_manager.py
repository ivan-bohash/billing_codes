import arrow


class UrlsManager:
    def __init__(self, session, pagination_model, urls_model, opposite_urls_model, details_model, fetch_method):
        self.session = session
        self.pagination_model = pagination_model
        self.urls_model = urls_model
        self.opposite_urls_model = opposite_urls_model
        self.details_model = details_model
        self.fetch_method = fetch_method
        self.updated_at = arrow.utcnow()

    async def update_urls(self):
        pagination_data = self.session.query(self.pagination_model).all()
        urls = [data.url for data in pagination_data]
        fetched_data = await self.fetch_method(urls=urls)

        def update():
            step = 10000
            updated_icd = 0

            db_data = {
                url.icd_code: url.id
                for url in self.session.query(self.urls_model).all()
            }

            for i in range(0, len(fetched_data), step):
                batch_fetched_data = fetched_data[i:i+step]
                mapping = []

                for icd in batch_fetched_data:
                    url_id = db_data.get(icd["icd_code"])

                    if url_id:
                        mapping.append({
                            "id": url_id,
                            "updated_at": self.updated_at
                        })

                if mapping:
                    self.session.bulk_update_mappings(self.urls_model, mapping)
                    updated_icd += len(mapping)

            self.session.commit()

            print(f"{self.urls_model.__name__}: {updated_icd} updated elements")

        def add_new():
            icd_code_list = {data.icd_code for data in self.session.query(self.urls_model.icd_code).all()}
            new_icd_codes = []

            for data in fetched_data:
                if data["icd_code"] not in icd_code_list:
                    icd = self.urls_model(icd_code=data["icd_code"], url=data["url"])
                    new_icd_codes.append(icd)

            if new_icd_codes:
                self.session.add_all(new_icd_codes)
                self.session.commit()
                print(f"{self.urls_model.__name__}: {len(new_icd_codes)} added elements")

        update()
        add_new()

    def delete_urls(self):
        urls_to_delete = (self.session.query(self.urls_model).
                          filter(self.urls_model.updated_at != self.updated_at).
                          filter(self.urls_model.icd_code.in_(self.session.query(self.opposite_urls_model.icd_code))
                                 )).all()

        if urls_to_delete:
            for url in urls_to_delete:
                self.session.delete(url)

            self.session.commit()

            urls_icd_code = [url.icd_code for url in urls_to_delete]
            for icd_code in urls_icd_code:
                detail = (self.session.query(self.details_model).
                          filter(self.details_model.icd_code == icd_code).
                          one_or_none())

                self.session.delete(detail)

            self.session.commit()

            print(f"{self.urls_model.__name__}, {self.details_model.__name__}: deleted {len(urls_to_delete)} elements")
