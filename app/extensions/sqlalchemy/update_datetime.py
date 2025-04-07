import arrow


def update_table_datetime(session, db_model):
    db_data = session.query(db_model).all()
    date = arrow.utcnow().datetime

    updated_data = [
        {
            "id": data.id,
            "created_at": date,
            "updated_at": date
        }
        for data in db_data
    ]

    session.bulk_update_mappings(db_model, updated_data)
    session.commit()
