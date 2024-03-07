# SSDT

Stupid Simple Detection Testing - For when you just need to quickly validate some rules.

## Description
This tool is an extremely basic implementation of running commands on endpoints to help trigger your command line based detections and storing them in a database to see what was run and make sure it's not failing.

It also allows for historical views, and simple deletion capabilities to clear out your test queues.

This tool is operating system agnostic. As long as you have python installed it will run. You could also pre-compile it as a binary per OS and run it without installing python with pyinstaller.

## Installation
Signup for the free tier of Supabase at https://supabase.com/database

Create a new database, then setup some new tables. The first table is for command_outputs:

```
CREATE TABLE command_outputs (
  id BIGINT PRIMARY KEY,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  command TEXT,
  output TEXT,
  group_id TEXT,
  error TEXT,
  operating_system TEXT,
  hostname TEXT
);
```

The second table is for stored_commands for the workbench:

``` 
CREATE TABLE stored_commands (
  id BIGINT PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  commands TEXT,
  description TEXT
);
```

From within the repo directory, run `pip install -r requirements.txt`.

### Adjust Supabase credentials in app.py

### Supabase client initialization
```
url = "removed"
key = "removed"
```

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
Historical Details
![Historical Details](/screenshot/historical_land.png?raw=true "Historical Details")