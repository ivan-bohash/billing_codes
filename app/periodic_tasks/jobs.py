from app.scraper.pagination import run_pagination_parser
from app.scraper.urls import run_url_parser
from app.scraper.details import run_detail_parser


scheduler_jobs = [
    # Pagination
    {
        "func": run_pagination_parser,
        "cron_string": "32 * * * *",
        "args": ["billable"],
        "depends_on": None,
    },
    {
        "func": run_pagination_parser,
        "cron_string": "32 * * * *",
        "args": ["non_billable"],
        "depends_on": None,
    },

    # Urls
    {
        "func": run_url_parser,
        "cron_string": "33 * * * *",
        "args": ["billable"],
        "depends_on": "run_pagination_parser_billable",
    },
    {
        "func": run_url_parser,
        "cron_string": "33 * * * *",
        "args": ["non_billable"],
        "depends_on": "run_pagination_parser_non_billable",
    },

    # Details
    {
        "func": run_detail_parser,
        "cron_string": "32 * * * *",
        "args": ["billable"],
        "depends_on": "run_url_parser_billable",
    },
    {
        "func": run_detail_parser,
        "cron_string": "32 * * * *",
        "args": ["non_billable"],
        "depends_on": "run_url_parser_non_billable",
    }
]
