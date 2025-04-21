from redis import Redis
from app.config import settings


class RedisWorker:
    """
    Main Redis worker

    """

    def __init__(self):
        self.jobs = []
        self.connection = Redis(
            host=settings.redis["host"],
            port=settings.redis["port"],
            db=settings.redis["db"],
        )

    def add_task(self, job):
        self.jobs.append(job)

