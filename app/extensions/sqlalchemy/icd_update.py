import arrow


def icd_update(session, model, fetch_data):
    batch_size = 1000
    updated_at = arrow.utcnow()

    for i in range(0, len(fetch_data), batch_size):
        batch = fetch_data[i:i + batch_size]
        codes = [data["icd_code"] for data in batch]

        session.query(model).filter(model.icd_code.in_(codes)).update(
            {model.updated_at: updated_at},
            synchronize_session=False
        )

    session.commit()
