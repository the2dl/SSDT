import time
import subprocess
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect
from supabase import create_client, Client
import platform

app = Flask(__name__)

# Supabase client initialization
url = "redacted"
key = "redacted"
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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        commands = request.form['commands'].splitlines()
        run_commands_and_store_in_supabase(commands)
        return redirect('/')  

    # Fetch command outputs from Supabase and group by 'group_id'
    data = supabase.table("command_outputs").select("*").execute().data
    grouped_data = {}
    for record in data:
        group_id = record.get('group_id')
        if group_id in grouped_data:
            grouped_data[group_id].append(record)
        else:
            grouped_data[group_id] = [record]

    table_data = [[record for record in records] for _, records in grouped_data.items()]

    return render_template('index.html', table_data=table_data)

@app.route('/delete_output', methods=['POST'])
def delete_output():
    group_id = request.args.get('group_id')  # Get the group_id from query parameters
    if group_id:
        # Delete entries from the command_outputs table with the matching group_id
        supabase.table("command_outputs").delete().eq('group_id', group_id).execute()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)