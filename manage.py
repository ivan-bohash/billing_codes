from app.run import RQWorker, PeriodicTask
from app.periodic_tasks.jobs import rq_jobs, scheduler_jobs


def run_rq():
    runner = RQWorker()

    for job in rq_jobs:
        runner.add_task(job=job)

    runner.run()


def run_scheduler():
    runner = PeriodicTask()

    for job in scheduler_jobs:
        runner.add_task(job)

    runner.run()


if __name__ == "__main__":
    run_rq()

