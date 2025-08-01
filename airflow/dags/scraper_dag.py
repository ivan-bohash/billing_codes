git from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def pagination_callable():
    from app.scraper.pagination import run_data_parsers
    run_data_parsers()


def urls_callable(action):
    from app.scraper.urls import run_data_parsers
    run_data_parsers(action)


def history_callable():
    from app.scraper.history import run_data_parsers
    run_data_parsers()


default_args = {
        "owner": "airflow",
        "retries": 0,
}

with DAG(
    default_args=default_args,
    dag_id="scraper_dag_v1",
    description="Dag to scrape ICD-10-CM data and update records in the database",
    start_date=datetime(2025, 5, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["scraper"]
) as dag:

    task_run_pagination = PythonOperator(
        task_id="pagination_task",
        python_callable=pagination_callable,
    )

    task_run_urls_update = PythonOperator(
        task_id="urls_update_task",
        python_callable=urls_callable,
        # op_args=["update"],
        op_kwargs={"action": "update"},
    )

    task_run_urls_delete = PythonOperator(
        task_id="urls_delete_task",
        python_callable=urls_callable,
        # op_args=["delete"],
        op_kwargs={"action": "delete"},
    )

    task_run_history = PythonOperator(
        task_id="history_task",
        python_callable=history_callable,
    )

    task_run_pagination >> task_run_urls_update >> [task_run_urls_delete, task_run_history]

