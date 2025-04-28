# ICD Codes

**ICD Codes** is a Python-based project designed to periodically fetch and update information about **Billable** and **Non-Billable** ICD10 codes.  


## Installation
- git clone https://github.com/ivan-bohash/icd_codes.git
- cd icd_codes
- pip install -e.

## Running
To fetch data and update db use commands in terminal:
- rq worker low
- rqscheduler
- python manage.py

To search for specific code:
- run main.py 
- navigate to running server in your browser
