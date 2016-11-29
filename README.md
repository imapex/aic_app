# Automated Infrastructure Configuration Framework v1.0

Any applicable badges (build/documentation/collaboration/licenses should go here

## Description

The Automated Infrastrucutre Configuration (AIC) Framework is a microservce based application that leverages APIs, on platformms created by Cisco Systems, to automate common infrastrucutre configuration tasks.

#  aic_app 

This repository contains the main application logic used to implement the northbound REST API, as well as the logic needed to execute the desired configuration workflow.

The northbound REST API can be used for the following tasks:
* Checking the status of the app.
* Displaying a list of registred workflows. (At present, the only workflow that is supported is called HBA Swap.)
* Submitting workflow tasks to the application.
* Viewing the status and parameters associated with completed workflow tasks.


# Installation

## Environment

Prerequisites

Software:
* Python 2.7+
* click 6.6
* Flask 0.11.1
* Flask-Testing 0.6.1
* itsdangerous 0.24
* Jinja2 2.8
* MarkupSafe 0.23
* requests 2.11.1
* Werkzeug 0.11.11

Hardware:
* Cisco MDS Switch

## Downloading

You can obtain a copy of the software from this repository as follows:

Option A:

If you have git installed, clone the repository

    git clone https://github.com/imapex/aic_app

Option B:

If you don't have git, [download a zip copy of the repository](https://github.com/imapex/aic_app/archive.zip) and extract.

Option C:

The latest build of this project is also available as a Docker image from Docker Hub

    docker pull username/aic_app:latest

## Installing

The AIC Framework is pre-installed in the Docker image and will start when the aic_app container is started.

If you've cloned the git repository, the application can be invoked by executing:

    python app.py

# Usage

The primary method of interacting with the application is via its REST API. The REST API binds to port 5000 of the local host when the application is started.

The URL path to the API is: 
    
    http://localhost:5000/aic/api/v1.0/

REST APIs:
* / - This is the root of the API. 
* /workflows - Displays a list of the registered workflows.
* /status - Displays the status of the API.
* /task - Task operations.
* /task/x - ('x' is the task-id.) Displays the status of the task.

## Workflow Task Example

Before submitting a workflow task it is usefull to have all of the information you might need, like:

* IP Address of the device
* Username and Password Credentials of the device
* Name of the AIC workflow you plane to execute
* Any additional parameters needed by the workflow 

### Example HBA Swap Workflow Task Submission

The "HBA Swap" workflow accepts five paramters via a JSON encoded payload:
* ip_address - IP address of the MDS Switch
* selected-task - 'hba_swap'
* task_param1 - This is the Current Physical World Wide Name
* task_param2 - This is the Current Device Alias
* task_param3 - This will be the new Physical World Wide Name

To submit a HBA Swap workflow via AIC's REST API, you will need to send an HTTP POST message to this URL:

    http://localhost:5000/aic/api/v1.0/task

The POST message must contain the workflow paramaters in a JSON encoded payload. An example POST method, using the 'curl' command is shown below: 

    curl -i -H "Content-Type: application/json" -X POST -d '{"ip_address":"x.x.x.x","selected-task":"hba_swap","task_param1":"11:11:11:11:11:11:11:11","task_param2":"OldDeviceAlias","task_param3":"33:33:33:33:33:33:33:33"}' http://localhost:5000/aic/api/v1.0/task

If the task completes scussesfully you should see output similar to the example below:

    HTTP/1.0 201 CREATED
    Content-Type: application/json
    Content-Length: 265
    Server: Werkzeug/0.11.11 Python/2.7.12
    Date: Tue, 29 Nov 2016 16:45:06 GMT

    {
    "task": {
        "done": true, 
        "id": 2, 
        "ip_address": "172.22.163.35", 
        "selected-task": "hba_swap", 
        "task-parameter1": "11:11:11:11:11:11:11:11", 
        "task-parameter2": "OldDeviceAlias", 
        "task-parameter3": "33:33:33:33:33:33:33:33"
        }
    }


# Development

Test coverage is poor right now.  Tests can be run by executing:
    
    python tests.py

# License

Include any applicable licenses here as well as LICENSE.TXT in the root of the repository

