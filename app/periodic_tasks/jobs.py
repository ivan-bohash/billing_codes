from app.scraper.pagination import run_pagination_parser
from app.scraper.urls import run_url_parser
from app.scraper.details import run_detail_parser

scheduler_jobs = [
    # Billable data
    # {
    #    "func": run_pagination_parser,
    #    "cron_string": "50 16 * * *",
    #    "args": ["billable"],
    #    "depends_on": None,
    # },
    # {
    #     "func": run_url_parser,
    #     "cron_string": "50 16 * * *",
    #     "args": ["billable"],
    #     "depends_on": "run_pagination_parser_billable",
    # },
    # {
    #     "func": run_detail_parser,
    #     "cron_string": "50 16 * * *",
    #     "args": ["billable"],
    #     "depends_on": "run_url_parser_billable",
    # },
    # Non-billable data
    {
        "func": run_pagination_parser,
        "cron_string": "59 16 * * *",
        "args": ["non_billable"],
        "depends_on": None,
    },
    {
        "func": run_url_parser,
        "cron_string": "59 16 * * *",
        "args": ["non_billable"],
        "depends_on": "run_pagination_parser_non_billable",
    },
    {
        "func": run_detail_parser,
        "cron_string": "59 16 * * *",
        "args": ["non_billable"],
        "depends_on": "run_url_parser_non_billable",
    }
]
