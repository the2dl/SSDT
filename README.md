# SSDT
 Stupid Simple Detection Testing

## Description
This tool is an extremely basic implementation of running commands on endpoints to help trigger your command line based detections and storing them in a database to see what was run and make sure it's not failing.

It also allows for historical views, and simple deletion capabilities to clear out your test queues.

## Installation
Signup for the free tier of Supabase at https://supabase.com/database

Create a new database, then setup a new table. The table is setup as below:

```
CREATE TABLE command_outputs (
  id BIGINT PRIMARY KEY,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  command TEXT,
  output TEXT,
  group_id TEXT,
  error TEXT,
  operating_system TEXT
);
```
From within the repo directory, run pip install -r requirements.txt.

### Adjust Supabase credentials in app.py

Lines 12 and 13
url = "SETYOURURL"
key = "SETYOURKEY"

## Start Flask
`flask run` from within the repository directory, connect to it on http://127.0.0.1:5000

## Run
Within the app, you can add a list of commands you want to run, one per new line, for example
```
nltest /dclist:
wmic os get version
whoami
```
## Screenshots
Landing Page
![Main](/screenshot/main.png?raw=true "Main")
Historical Page
![History](/screenshot/history.png?raw=true "History")