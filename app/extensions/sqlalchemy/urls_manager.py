import arrow


class UrlsManager:
    def __init__(self, session, urls_model, details_model, fetch_data):
        self.session = session
        self.urls_model = urls_model
        self.details_model = details_model
        self.fetch_data = fetch_data
        self.updated_at = arrow.utcnow()

    def add_icd(self):
        icd_code_list = {data.icd_code for data in self.session.query(self.urls_model.icd_code).all()}
        new_icd_codes = []

        for data in self.fetch_data:
            if data["icd_code"] not in icd_code_list:
                icd = self.urls_model(icd_code=data["icd_code"], url=data["url"])
                new_icd_codes.append(icd)

        if new_icd_codes:
            self.session.add_all(new_icd_codes)
            self.session.commit()
            print(f"Added {len(new_icd_codes)} urls")

    def update_icd(self):
        mapping = []
        db_data = {
            url.icd_code: url.id
            for url in self.session.query(self.urls_model).all()
        }

        for icd in self.fetch_data:
            url_id = db_data.get(icd["icd_code"])
            mapping.append({
                "id": url_id,
                "updated_at": self.updated_at
            })

        self.session.bulk_update_mappings(self.urls_model, mapping)
        self.session.commit()

        print(f"Updated {len(mapping)} items")

    def delete_icd(self):
        urls_to_delete = (self.session.query(self.urls_model).
                          filter(self.urls_model.updated_at != self.updated_at).all())

        if urls_to_delete:
            for url in urls_to_delete:
                self.session.delete(url)

            urls_id = [url.id for url in urls_to_delete]
            for url_id in urls_id:
                detail = self.session.query(self.details_model).filter(self.details_model.id == url_id).one_or_none()
                self.session.delete(detail)

            self.session.commit()
            print(f"Deleted {len(urls_to_delete)} items")

    def run(self):
        self.add_icd()
        self.update_icd()
        self.delete_icd()
