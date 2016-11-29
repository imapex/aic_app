from flask import Flask
from flask import jsonify
from flask import make_response
from flask import abort
from flask import request
import uuid
import sys
import requests
import json
import zone_bonnett

app = Flask(__name__)

# The dictionary below, named "api_methods", lists the various URL paths that are
# available in the Flask API.

api_methods = {
    '/' : 'Your current location.',
    '/status'  : 'Displays the status of the API.',
    '/workflows' : 'Displays a list of the registered workflows.',
    '/task' : 'Task operations. '
}

# The dictionrary below, named "registred_workflow", is used to list
# all of the available workflows within the AIC Framework. 
# Future devlopers should consider developing a framework for registering 
# additional workflow.
# 
# The "hba_swap" workflow is used to execute an HBA Swap on a Cisco MDS Switch.
# The "nxapi" workflow is used primalry to test the NX-API.
# In the intial release of the AIC Framework, only the "hba_swap" workflow will be used.

registered_workflows = {
    'hba_swap' : 'HBA Swap is used to run the HBA Swap Workflow',
    'nxapi'   : 'Shim for NX-API tetsing.'
}

# The dictionary below, named "credentials", could be used for storing the device 
# credentials the application will need to access the MDS and other network devices.
# As of 11-17-16, the credentials below aren't used by Dan's "zone.py" code.

credentials = [
    {
        'ip_address': '123.34.34.12', 
        'usename': 'mike',
        'password': 'blah'
    }
]

# The array below, named "tasks", is used to store information related to the tasks
# that have been submitted to the API.
#
# The array is initilized below with no data.  The array will contain dictonaries,
# each of which will contain keys named: "id", "ip_address", "selected_task",  
# and "done". The dictonaires may also include other keys named:
# "task-parameter1", "task-parameter2", and "task-parameter3". These addiotnal keys
# are used to store data associated with the selected plugin.

tasks = [
]

app_status = 'Up'

# The fucntion below is used to route the submitted task to the correct plugin.
# The function accepts three paramters: 
# "ip_address", which is required. 
# "plugin", which is optional. Defaults to None.
# "*other_params", also optional. Used to pass additional values to the selected plugin. 
#
# For now, the code includes DEBUG output that is written to stdout. 

def call_selected_plugin(ip_address, plugin=None, *other_params):
    sys.stdout.write('DEBUG: call_selected_plugin(): Begin function execution.\n')
    if plugin is None:
        sys.stdout.write('DEBUG: call_selected_plugin(): No plugin selected.\n')
    else:
        if plugin == 'hba_swap':
            sys.stdout.write('DEBUG: call_selected_plugin(): Calling hba_swap().\n')
            hba_swap(ip_address, other_params[0], other_params[1], other_params[2])
        else:
            sys.stdout.write('DEBUG: call_selected_plugin(): Calling call_nxaip().\n')
            call_nxapi(ip_address, payload)
    return 

# The function below named "hba_swap" is used to invoke thet HBA SWAP workflow. 
# It calls the configure_zone() function from the zone.py file. The hba_swap() fucntion
# passes the "ipaddress", "OldPwnn", "OldDevAlias", and "NewPwwn" paramters to configure_zone().
#
# This function includes DEBUG output that is written to stdout.

def hba_swap(ipaddress, OldPwwn, OldDevAlias, NewPwwn):
    sys.stdout.write('DEBUG: hba_swap(): Executing "hba_swap" plugin.\n')
    sys.stdout.write('DEBUG: hba_swap(): IP address is: '+ipaddress+'\n')
    sys.stdout.write('DEBUG: hba_swap(): OldPwwn is: '+OldPwwn+'\n')
    sys.stdout.write('DEBUG: hba_swap(): OldDevAlias is: '+OldDevAlias+'\n')
    sys.stdout.write('DEBUG: hba_swap(): NewPwwn is: '+NewPwwn+'\n')
    sys.stdout.write('DEBUG: hba_swap(): Calling zone.configure_zone().\n')
    zone_bonnett.configure_zone(ipaddress, OldPwwn, OldDevAlias, NewPwwn)
    return

# The function below, named "call_nxapi", is used to access the NX-API. 
# This function will likley refactored to call Dan's code in 
# the "zone.py" file.
#
# This function includes DEBUG output that is written to stdout.
# 
# For now, the MDS credeintals are defined in the variables: "switchuser" & 
# "switchpassword".
#
# The "url" variable is used to build the base NX-API URL.
# This function returns the JSON response recived from the NX-API.

def call_nxapi(ip_address, payload):
    sys.stdout.write('DEBUG: call_nxapi: Executing "nxapi" plugin\n')

    switchuser='danwms'
    switchpassword='AICteam'

    url = 'http://'+ip_address+':8080/ins'
    headers = {'content-Type': 'application/json'}

    sys.stdout.write('DEBUG: call_nxapi(): Making NX-API Call:'+url+'\n')
    response = requests.post(url,data=json.dumps(payload), headers=headers,auth=(switchuser,switchpassword)).json()
    sys.stdout.write('DEBUG: call_nxapi(): NX-API response: '+json.dumps(response, indent=4, sort_keys=True)+'.\n')
    return response

# The functions below that start with "@app.route" are part of the Flask 
# REST API Framework.
#
# The '/' function is the root of the overall API. When called it returns
# the string shown below.

@app.route('/')
def get_http_root():
    return 'Automated Infrastrucutre Configuration Framework v1.0'

# The function below is the root of the AIC v1.0 API. When called via a GET method,
# it returns a JSON payload of the "api_methods" dictionary variable.

@app.route('/aic/api/v1.0/', methods=['GET'])
def get_api_root():
    return jsonify(api_methods)

# The function below is used to check the status of AIC v1.0 API. When called via a 
# GET method, it returns a JSON payload that contains the "app_status" variable.

@app.route('/aic/api/v1.0/status', methods=['GET'])
def get_api_status():
    return jsonify(Status=app_status)

# The function below is used to list the workflows avialble in the AIC v1.0 API. 
# When called via a GET method, it returns a JSON payload that contains 
# the "registered_workflows" dictionary variable.

@app.route('/aic/api/v1.0/workflows', methods=['GET'])
def get_api_plugins_list():
    return jsonify(registered_workflows)

# The function below is used to list the tasks submitted to the AIC v1.0 API. 
# When called via a GET method, it returns a JSON payload that contains 
# the "tasks" array variable.

@app.route('/aic/api/v1.0/task', methods=['GET'])
def get_api_tasks():
    return jsonify({'task': tasks})

# The function below is used to submit a task to the AIC v1.0 API. 
# The function expects a JSON payload that contains, at a minum, the "ip_address"
# parameter. Optional parameters include "selected-task", "task-param1",
# "task-param2", and "task-param3".
# The fucntion is invoked via the POST method. 

@app.route('/aic/api/v1.0/task', methods=['POST'])
def create_task():
    # Ensure, at a minimum, the "ip_address" parameter is included in the JSON
    # payload. If not, abort the transcation and return an HTTP 400 error message.
    if not request.json or not 'ip_address' in request.json:
        abort(400)
    # The "if" code below is used to assign a value to the "task_id" variable.
    if tasks:
        # If tasks exist in the "task" array, incremnet the highest id by one 
        # and assign the new value to "task_id" variable.
        task_id = tasks[-1]['id'] + 1
    else:
        # If tasks do not exist in the "tasks" array, assign the integer of 1 to the
        # "task_id" variable.
        task_id = 1
    # Define the "task" dictionary.
    if not request.json.get('selected-task'):
        task = {
        'id': task_id,
        'ip_address': request.json['ip_address'],
        'done': True
        }
    else:
        task = {
        'id': task_id,
        'ip_address': request.json['ip_address'],
        'selected-task': request.json.get('selected-task'),
        # I was thinking that having a catch-all parameter for generic json payloads may
        # be usefull.  This idea hasn't been implemented yet.
        # 'generic_json_payload': request.json.get('generic_json_payload'),
        'task-parameter1': request.json.get('task_param1'),
        'task-parameter2': request.json.get('task_param2'),
        'task-parameter3': request.json.get('task_param3'),
        'done': False
        }
    # Append the new "task" dictionary to the "tasks" array.
    tasks.append(task)
    # Write DEBUG output to stdout.
    sys.stdout.write('DEBUG: create_task(): Added task id: '+str(task_id)+' to tasks array.\n')
    # The "if" conditional below checks for the prescence of the 'selected-task' paramter.
    # If it doesn't exist the Debug ouput will print as much.
    # If it does exist the "else" conditional will print the value of the selected task.
    if not request.json.get('selected-task'):
        sys.stdout.write('DEBUG: create_task(): No plugin was requested. \n')
    else:
        sys.stdout.write('DEBUG: create_task(): Requested plugin is: '+task['selected-task']+' \n')
    sys.stdout.write('DEBUG: create_task(): Host IP Address is: '+task['ip_address']+' \n')
    # The "if" conditional below checks for the prescence of the 'task-parameters'.
    # If they do exist the the code will print the values of the paramaters.
    # If they doesn't exist the "else" conditional will print as much.
    if request.json.get('plugin_param1') or request.json.get('plugin_param2') or request.json.get('plugin_param3'):
        sys.stdout.write('DEBUG: create_task(): Plugin parameter 1 is: '+task['task-parameter1']+' \n')
        sys.stdout.write('DEBUG: create_task(): Plugin parameter 2 is: '+task['task-parameter2']+' \n')
        sys.stdout.write('DEBUG: create_task(): Plugin parameter 3 is: '+task['task-parameter3']+' \n')
    else:
        sys.stdout.write('DEBUG: create_task(): No optional Plugin parameters submitted. \n')
    sys.stdout.write('DEBUG: create_task(): Passing IP address, plugin name, and plugin paramters (if they exist) to call_selected_plugin().\n')
    # Invoke the "call_selected_plugin()" function and pass the 
    # appropriate mandatory and, if needed, the optional parameters to the function.
    if not request.json.get('selected-task'):
        call_selected_plugin(task['ip_address'])
    else:
        call_selected_plugin(task['ip_address'], task['selected-task'], task['task-parameter1'], task['task-parameter2'], task['task-parameter3'])
    # Set the "done" parameter in the "task" dictionary to True.
    task['done'] = True
    # Currently, the function only return a 201 (Created, HTTP Response).
    # This shoud be addressed in teh future.
    # Return a JSON representation of the "task" dictionary. This will include an 
    # HTTP response of 201. 
    return jsonify({'task': task}), 201

# The function below is used to view the status of particular task submited to the AIC
# v1.0 API. 
# The fucntion is invoked via the GET method.

@app.route('/aic/api/v1.0/task/<int:task_id>', methods=['GET'])
def get_task(task_id):
    # Walk the "tasks" array to find the dictionary where "task_id" (which is provided
    # in the URL) is equal to the "id" stored in the dictionary.
    task = [task for task in tasks if task['id'] == task_id]
    # If we can't find a match, retun an HTTP 404 Error.
    if len(task) == 0:
        abort(404)
    # When a match is found, retun a JSON representation of the found "task".
    return jsonify({'task': task[0]})

@app.route('/aic/api/v1.0/plugins/nx-api', methods=['POST'])
def post_api_plugins_nxapi():
    return jsonify()

# The functions below that start with "@app.errorhandler" are part of the Flask API
# and are used to simplify error handling.
#
# The fucntions return a JSON payload with the HTTP Error code defined in the fucntion call. 

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

# The code below is only used when aic_app.py is called via the python executbale.

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

