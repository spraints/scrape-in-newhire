# In-Newhire.com Employee Scraper

This script scrapes employee data from in-newhire.com, including both new hires and terminations.

Cursor wrote this whole thing. It hasn't updated this README, but the content here is pretty close.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the script:
```bash
python scrape_employees.py
```

## Output

The script will:
1. Scrape the website for employee data
2. Save the data to a CSV file with a timestamp (e.g., `employees_20240321_143022.csv`)
3. Display a summary of the scraped data

## Data Format

The CSV file will contain the following columns:
- name: Employee name
- status: Employment status (new hire/termination)
- date: Date of the status change

## Note

The script includes error handling and will:
- Print any errors encountered during scraping
- Continue processing even if some entries fail to parse
- Save all successfully scraped data 
