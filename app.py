# SSDT - Super Simple Detection Testing
# Dan Lussier - @dansec_ / the2dl

import time
import subprocess
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect
from supabase import create_client, Client
import platform
import threading

app = Flask(__name__)

# Supabase client initialization
url = "removed"
key = "removed"
supabase: Client = create_client(url, key)

def execute_command_with_timeout(command, timeout, unique_id, start_time, operating_system, on_timeout_callback):
    try:
        # Execute the command with a timeout
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, timeout=timeout)
        output_record = {
            "timestamp": start_time.isoformat(),
            "command": command,
            "output": result.stdout if result.stdout else result.stderr,
            "group_id": unique_id,
            "error": "",
            "operating_system": operating_system
        }
    except subprocess.CalledProcessError as e:
        output_record = {
            "timestamp": start_time.isoformat(),
            "command": command,
            "output": "",
            "group_id": unique_id,
            "error": str(e),
            "operating_system": operating_system
        }
    except subprocess.TimeoutExpired:
        output_record = {
            "timestamp": start_time.isoformat(),
            "command": command,
            "output": "failed",
            "group_id": unique_id,
            "error": "Command timed out after 30 seconds",
            "operating_system": operating_system
        }
    else:
        # If no exception was raised, insert the successful command output into Supabase
        supabase.table("command_outputs").insert(output_record).execute()
        return  # Early return to avoid executing the on_timeout_callback

    # Handle both CalledProcessError and TimeoutExpired by inserting the output record
    supabase.table("command_outputs").insert(output_record).execute()

def on_command_timeout(command, unique_id, start_time, operating_system):
    # This function will be called when the command exceeds its execution timeout
    output_record = {
        "timestamp": start_time.isoformat(),
        "command": command,
        "output": "failed",
        "group_id": unique_id,
        "error": "Command forcefully terminated after exceeding timeout",
        "operating_system": operating_system
    }
    # Insert the failure record into Supabase
    supabase.table("command_outputs").insert(output_record).execute()

def run_commands_and_store_in_supabase(commands, timeout):
    unique_id = str(uuid.uuid4())  # Generate a unique identifier for the group of commands
    operating_system = platform.system()  # Collect the OS name
    
    for command in commands:
        if command.strip():
            start_time = datetime.utcnow()
            # Adjust here to use the user-specified timeout
            thread = threading.Thread(target=execute_command_with_timeout, args=(command, timeout, unique_id, start_time, operating_system, lambda: on_command_timeout(command, unique_id, start_time, operating_system)))
            thread.start()
            # Adjust the join timeout to respect the user-defined timeout plus a buffer
            thread.join(timeout=timeout + 5)  # Use the user-specified timeout plus a buffer
            
            if thread.is_alive():
                # If the thread is still alive, it means the command exceeded the timeout
                # Explicitly call the timeout handler function to insert a failure record
                on_command_timeout(command, unique_id, start_time, operating_system)

            time.sleep(1)  # Throttle command execution

def get_latest_group_id():
    # Fetch all records with their timestamps
    result = supabase.table('command_outputs').select('group_id, timestamp').execute()

    if result.data:
        # Sort the records by timestamp in descending order to get the latest
        sorted_data = sorted(result.data, key=lambda x: x['timestamp'], reverse=True)
        # Return the group_id of the first record, which is the latest
        return sorted_data[0].get('group_id')
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        commands = request.form['commands'].splitlines()
        timeout = int(request.form.get('timeout', 30))  # Get the timeout from the form, default to 30 seconds
        run_commands_and_store_in_supabase(commands, timeout)  # Pass the timeout to your function
        return redirect('/')

    latest_group_id = get_latest_group_id()
    if latest_group_id:
        # Fetch command outputs from Supabase for the latest group
        data = supabase.table("command_outputs").select("*").eq('group_id', latest_group_id).execute().data
        table_data = [data]
    else:
        table_data = []

    return render_template('index.html', table_data=table_data)

@app.route('/delete_output', methods=['POST'])
def delete_output():
    group_id = request.args.get('group_id')  # Get the group_id from query parameters
    if group_id:
        # Delete entries from the command_outputs table with the matching group_id
        supabase.table("command_outputs").delete().eq('group_id', group_id).execute()
    return redirect('/')

@app.route('/history', methods=['GET'])
def history():
    # Retrieve all group_id values from the Supabase table
    result = supabase.table('command_outputs').select('group_id').execute()

    if result.data:
        # Extract the group_id values and use a set to ensure uniqueness
        historical_group_ids = list(set([row['group_id'] for row in result.data]))
    else:
        # If no data is found, return an empty list
        historical_group_ids = []

    # Render the history.html template, passing the unique group_ids
    return render_template('history.html', group_ids=historical_group_ids)

@app.route('/view_group/<group_id>')
def view_group(group_id):
    # Fetch command outputs with matching group_id from Supabase
    data = supabase.table("command_outputs").select("*").eq('group_id', group_id).execute().data

    if not data:
        # Handle the case where no data is found for the group_id
        return render_template('error.html', error_message="Group not found"), 404

    return render_template('view_group.html', group_data=data)

@app.route('/delete_group/<group_id>', methods=['POST'])
def delete_group(group_id):
    # Delete from Supabase
    supabase.table('command_outputs').delete().eq('group_id', group_id).execute() 
    return redirect('/history') 

@app.route('/workbench')
def workbench():
    stored_commands = supabase.table('stored_commands').select('*').execute().data
    return render_template('workbench.html', stored_commands=stored_commands)

@app.route('/add_command', methods=['POST']) 
def add_command():
    commands = request.form['commands']  # Get commands as a single string
    # Insert the command into the stored_commands table
    supabase.table('stored_commands').insert({"commands": commands, "created_at": datetime.utcnow().isoformat()}).execute()
    return redirect('/workbench') 

@app.route('/delete_command/<command_id>', methods=['POST']) 
def delete_command(command_id):
    supabase.table('stored_commands').delete().eq('id', command_id).execute()
    return redirect('/workbench')

if __name__ == '__main__':
    app.run(debug=True)