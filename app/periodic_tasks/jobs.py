from app.scraper.pagination import run_pagination_parser
from app.scraper.urls import run_urls_parser
from app.scraper.details import run_details_parser

cron_string = "* * * * *"

scheduler_jobs = [
    # Billable data
    {
       "func": run_pagination_parser,
       "cron_string": cron_string,
       "args": ["billable"],
       "depends_on": None,
    },
    {
        "func": run_urls_parser,
        "cron_string": cron_string,
        "args": ["billable"],
        "depends_on": "run_pagination_parser_billable",
    },
    {
        "func": run_details_parser,
        "cron_string": cron_string,
        "args": ["billable"],
        "depends_on": "run_urls_parser_billable",
    },
    # Non-billable data
    {
        "func": run_pagination_parser,
        "cron_string": cron_string,
        "args": ["non_billable"],
        "depends_on": "run_details_parser_billable",
    },
    {
        "func": run_urls_parser,
        "cron_string": cron_string,
        "args": ["non_billable"],
        "depends_on": "run_pagination_parser_non_billable",
    },
    {
        "func": run_details_parser,
        "cron_string": cron_string,
        "args": ["non_billable"],
        "depends_on": "run_urls_parser_non_billable",
    },
]
