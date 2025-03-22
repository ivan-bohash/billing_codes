from app.run import CronJobScheduler
from app.periodic_tasks.jobs import scheduler_jobs


def run_scheduler():
    runner = CronJobScheduler()

    for job in scheduler_jobs:
        runner.add_task(job)

    runner.run()


if __name__ == "__main__":
    run_scheduler()
