from app.run import PeriodicTask
from app.periodic_tasks.jobs import scheduler_jobs


def run_scheduler():
    runner = PeriodicTask()

    # Add jobs from the list to the scheduler
    for job in scheduler_jobs:
        runner.add_task(job)

    runner.run()


if __name__ == "__main__":
    run_scheduler()

