# tgaad-draftresults
Generates HTML files for draft results from auctions run through Two Guys and a Dream.

## Prerequisites

To run, you need:

 - Python 2.7
 - Python modules
   - MySQLdb
   - json
   - os
   - jinja2
   - boto3
 - AWS credentials in `~/.aws/credentials`
 - MySQL running on `localhost` with user `root` (no password), loaded with the Two Guys and a Dream schema and data

## To Run

    ./loadResults.py

## Output

The script generates the draft results and contracts data as json in the `data` directory.

It also creates HTML pages to render the results in the `html` directory.
