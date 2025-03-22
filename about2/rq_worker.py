# run.py
# class RQWorker(RedisWorker):
#     def __init__(self):
#         super().__init__()
#         self.queue_names = list(settings.redis["queue_name"].keys())
#         self.queue = Queue("low", connection=self.connection)
#         self.worker = Worker(
#             queues=self.queue_names,
#             connection=self.connection,
#         )
#
#     def run(self):
#         for job in self.jobs:
#             self.queue.enqueue(job["func"], job["params"])
#
#         self.worker.work()

# manage.py
# def run_rq():
#     runner = RQWorker()
#
#     for job in rq_jobs:
#         runner.add_task(job=job)
#
#     runner.run()