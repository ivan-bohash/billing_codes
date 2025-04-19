from app.scraper.pagination import run_pagination_parser
from app.scraper.urls import run_urls_parser
from app.scraper.details import run_details_parser

cron_string = "* * * * *"

scheduler_jobs = [
    # pagination
    {
       "func": run_pagination_parser,
       "cron_string": cron_string,
       "args": None,
       "depends_on": None,
    },
    # urls
    {
        "func": run_urls_parser,
        "cron_string": cron_string,
        "args": ["update_urls"],
        "depends_on": "run_pagination_parser",
    },
    {
        "func": run_urls_parser,
        "cron_string": cron_string,
        "args": ["delete_urls"],
        "depends_on": "run_urls_parser_update_urls",
    },
    # details
    {
        "func": run_details_parser,
        "cron_string": cron_string,
        "args": None,
        "depends_on": "run_urls_parser_delete_urls",
    },

]




