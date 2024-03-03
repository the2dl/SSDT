import time
import subprocess
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect
from supabase import create_client, Client
import platform

app = Flask(__name__)

# Supabase client initialization
url = "SETYOURURL"
key = "SETYOURKEY"
supabase: Client = create_client(url, key)

def run_commands_and_store_in_supabase(commands):
    unique_id = str(uuid.uuid4())  # Generate a unique identifier for the group of commands
    operating_system = platform.system() # Collect the OS name
    
    for command in commands:
        if command.strip():
            start_time = datetime.utcnow()
            try:
                result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
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
            # Insert command output into Supabase
            supabase.table("command_outputs").insert(output_record).execute()

            time.sleep(1)

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
        run_commands_and_store_in_supabase(commands)
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

if __name__ == '__main__':
    app.run(debug=True)