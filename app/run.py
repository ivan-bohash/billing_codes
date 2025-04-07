from rq import Queue, Worker
from rq_scheduler import Scheduler
from app.config import settings
from app.extensions.rq_ext.redis_worker import RedisWorker


class PeriodicTask(RedisWorker):
    def __init__(self):
        super().__init__()

        self.queue = Queue("low", connection=self.connection)
        self.queue_name = settings.redis["queue_name"]["low"]
        self.scheduler = Scheduler(
            queue=self.queue,
            connection=self.connection
        )

    def run(self):
        jod_ids = {}

        for job in self.jobs:
            job_name = f"{job['func'].__name__}_{job['args'][0]}"
            depends_on = jod_ids.get(job["depends_on"]) if job["depends_on"] else None

            scheduled_job = self.scheduler.cron(
                cron_string=job["cron_string"],
                func=job["func"],
                args=job["args"],
                depends_on=depends_on,
                queue_name=self.queue_name,
                timeout=50000
            )

            jod_ids[job_name] = scheduled_job.id

