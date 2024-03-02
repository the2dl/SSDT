import time
import json
import subprocess
import os
import platform
import uuid  # Added for generating unique identifiers
from datetime import datetime
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename 

app = Flask(__name__)

output_file_path = r"/Users/dan/detection_testing/out.json"

def run_commands_from_commands_list(commands):
    output_data = []
    unique_id = str(uuid.uuid4())  # Generate a unique identifier for the group of commands

    for command in commands:
        if command.strip():
            try:
                start_time = datetime.utcnow()
                result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

                output_record = {
                    "timestamp": start_time.isoformat(),
                    "command": command,
                    "output": result.stdout if result.stdout else result.stderr,
                    "group_id": unique_id  # Associate the unique identifier with the command
                }
                output_data.append(output_record)

            except subprocess.CalledProcessError as e:
                output_record = {
                    "timestamp": datetime.now().isoformat(),
                    "command": command,
                    "error": str(e),
                    "group_id": unique_id  # Associate the unique identifier with the command
                }
                output_data.append(output_record)

            time.sleep(1)

    # Append new commands to the existing file instead of overwriting
    try:
        with open(output_file_path, "r") as output_file:
            existing_data = json.load(output_file)
            existing_data.extend(output_data)
    except FileNotFoundError:
        existing_data = output_data

    with open(output_file_path, "w") as output_file:
        json.dump(existing_data, output_file, indent=2)

@app.route('/', methods=['GET', 'POST'])
def index():
    operating_system = platform.system()  # Get OS info

    if request.method == 'POST':
        commands = request.form['commands'].splitlines()
        with open('inputs.txt', 'w') as f:
            f.writelines(command + '\n' for command in commands)
        run_commands_from_commands_list(commands)
        return redirect('/')  

    # Read output from file and group by 'group_id'
    try:
        with open(output_file_path, 'r') as f:
            output_data = json.load(f) 

            grouped_data = {}
            for record in output_data:
                group_id = record.get('group_id')
                if group_id in grouped_data:
                    grouped_data[group_id].append(record)
                else:
                    grouped_data[group_id] = [record]

            # Convert grouped_data to a list of lists for easier template rendering
            # You'll need to adjust the template to handle this structure
            table_data = [[record for record in records] for group_id, records in grouped_data.items()]

            return render_template('index.html', table_data=table_data, operating_system=operating_system)
    except FileNotFoundError:
        return render_template('index.html', operating_system=operating_system) # Still display the OS

@app.route('/delete_output', methods=['POST'])
def delete_output():
    try:
        os.remove(output_file_path)
    except FileNotFoundError:
        pass  # Ignore if the file doesn't exist
    return redirect('/') 

if __name__ == '__main__':
    app.run(debug=True) 
