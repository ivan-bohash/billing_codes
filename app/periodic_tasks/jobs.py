from app.scraper.pagination import run_pagination_parser
from app.scraper.urls import run_url_parser
from app.scraper.details import run_detail_parser

rq_jobs = [
    {
        "func": run_pagination_parser,
        "params": "billable"
    },
    {
        "func": run_pagination_parser,
        "params": "non_billable"
    },
]

scheduler_jobs = [
    # Urls
    {
        "func": run_url_parser,
        "cron_string": "* * * * *",
        "args": ["billable"],
    },
    {
        "func": run_url_parser,
        "cron_string": "* * * * *",
        "args": ["non_billable"],
    },

    # Details
    {
        "func": run_detail_parser,
        "cron_string": "* * * * *",
        "args": ["billable"]
    },
    {
        "func": run_detail_parser,
        "cron_string": "* * * * *",
        "args": ["non_billable"]
    }
]
