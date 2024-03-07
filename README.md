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

Supabase client initialization (these can be found in Project Settings > API). Verify permissions of your account you use, for simplicity since this is all local to your own instance, you can select the service_role secret, but you can also define proper roles if you'd like.

```
url = "removed"
key = "removed"
```

## Start Flask
`flask run` from within the repository directory, connect to it on http://127.0.0.1:5000

## Self contained executable

Sometimes you don't want to install Python on every endpoint, not a problem! Utilize pyinstaller to build a version for your underlying OS.

From within the flask app directory:

`pyinstaller.exe -w -F --add-data "templates;templates" --add-data "static;static" app.py`

The above when run on whatever operating system you're on will build an app binary (app/app.exe/etc) in the .\dist directory. Simply run this compiled payload and connect to it on http://127.0.0.1:5000.

## Run
Within the app, you can add a list of commands you want to run, one per new line, for example
```
nltest /dclist:
wmic os get version
whoami
```

## Ideas
I may create agent workers for this over time, it's a lot more work but something I may build out as it'd eliminate the need to deploy the webserver on each endpoint. Feel free to make a pull request!

## Screenshots
Landing Page
![Main](/screenshot/main.png?raw=true "Main")
Workbench
![Workbench](/screenshot/workbench.png?raw=true "Work Bench")
Historical Page
![History](/screenshot/historical_results.png?raw=true "History")
Historical Details
![Historical Details](/screenshot/view_historical.png?raw=true "Historical Details")