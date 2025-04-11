import arrow


class ICDManager:
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
            print(new_icd_codes)
            self.session.add_all(new_icd_codes)
            print("Added")
            self.session.commit()
        else:
            return None

    def update_icd(self):
        batch_size = 1000

        try:
            for i in range(0, len(self.fetch_data), batch_size):
                batch = self.fetch_data[i:i + batch_size]
                codes = [data["icd_code"] for data in batch]

                self.session.query(self.urls_model).filter(self.urls_model.icd_code.in_(codes)).update(
                    {self.urls_model.updated_at: self.updated_at},
                    synchronize_session=False
                )
            print("Updated")
            self.session.commit()

        except Exception as e:
            print(e)

    def delete_icd(self):
        removed_icd = self.session.query(self.urls_model).filter(self.urls_model.updated_at != self.updated_at).all()

        if removed_icd:
            # delete from urls table
            for icd in removed_icd:
                self.session.delete(icd)

            # delete form details table
            removed_icd_codes = [icd.icd_code for icd in removed_icd]
            icd_to_delete = self.session.query(self.details_model).filter(self.details_model.icd_code.in_(
                removed_icd_codes)).all()

            for icd in icd_to_delete:
                self.session.delete(icd)

            self.session.commit()
            print("Deleted")
        else:
            return None

    def run(self):
        self.update_icd()
        self.add_icd()
        self.delete_icd()

