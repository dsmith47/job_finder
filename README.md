# Job Crawl Script

A script for understanding job posting state/history

## Setup/Installation

1. Clone the Reposiory
```
git@github.com:dsmith47/job_finder.git
```

2. Install Dependencies
```
pip install -r REQUIREMENTS.txt
```

## Usage

### Executing Web Crawler

```
python3 main.py3
```

This will load jobs from all sites configured and output a file under
the name  `job-report_*` (where * is the date/time of script execution).
This file will be placed by default in the `output/` directory.

#### Advanced Execution Notes

By default the crawling script caches web pages for some of its queries.
The cache ensures partial success (in the case of slow networks), but 
can cannonize out-of date pages in the meantime. If you run the scrip
infrequently this can lead to outdated results. Manually clearing
files from the `.cache/` directory before executions prevents this.

### Further Processing Output

It may be necessary to process the job output further, which is why
this project features a secondary script to filter the job entries.
Execute the script by specifying a `TARGET_FILE`
