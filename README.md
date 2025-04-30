# ICD Codes

**ICD Codes** is a Python-based project designed to periodically fetch and update information about **Billable** and **Non-Billable** ICD10 codes.  


## Installation
- git clone https://github.com/ivan-bohash/icd_codes.git
- cd icd_codes
- pip install -e.

## Running
1) Open app/periodic_tasks/jobs.py and set time in cron_string.

2) To fetch data and update db use commands in terminal:
- rq worker low
- rqscheduler
- python manage.py

## Usage
- Run main.py 

Swagger API documentation: 
- http://127.0.0.1:8000/docs

Or enter icd code in the path:
- http://127.0.0.1:8000/icd-codes/{icd_code}

Use input to search for icd code:
- http://127.0.0.1:8000/icd-code

