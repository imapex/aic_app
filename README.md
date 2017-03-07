# Automated Infrastructure Configuration

The Automated Infrastructure Configuration (AIC) application is a microservce based application that leverages APIs, on platforms created by Cisco Systems, to automate common infrastructure configuration tasks.

### Table of Contents 

* [aic_app](#aic_app)
* [Installation](#installation)
  * [Environment](#environment)
  * [Downloading](#downloading)
  * [Install](#installing)
* [Usage](#usage)
  * [Rest APIs](#rest-apis)
  * [Workflows](#workflows)
  * [API Examples](#api-examples)
* [Development](#development)
* [License](#license)

#  aic_app 

This repository contains the main application logic used to implement AIC's northbound REST API, as well as the logic needed to execute the desired configuration workflow.

The northbound REST API can be used for the following tasks:
* Checking the status of the app.
* Displaying a list of registered workflows. (At present, the only workflow that is supported is called HBA Swap.)
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

If you have git installed, clone the repository:

    git clone https://github.com/imapex/aic_app

Option B:

The latest build of this project is also available as a Docker image from Docker Hub:

    docker pull /imapex/aic_app:latest

### Repository File Contents

| File Name | Description |
| --- | --- | 
| LICENSE | Describes the licenses the software is available under. |
| README.md | The repository readme file. (This file.) | 
| aic_api.py | Contains the majority of the Northbound API python code. | 
| app.py | Main application code. | 
| requirements.txt | Lists the required Python modules. | 
| tests.py | Contains the unit test python code. | 
| zone.py | Contains the majority of the HBA Swap workflow logic. |
| Dockerfile | Instructions for building a Docker image. |

## Install

This application can be installed locally on your server, or by using Docker (preferred).

In either case, the application requires certian enviormental variables be present:

* AIC_USER - Username on MDS Switch
* AIC_PASSWORD - Password on MDS Switch

### Docker Install 

This section is a work in progress...

The AIC application is pre-installed in the Docker image and will start when the aic_app container is started. 

Start the aic_app Docker container:

    docker run -p 127.0.0.1:5000:5000 -e AIC_USER=<your-username-here> -e AIC_PASSWORD=<your-password-here> imapex/aic_app

The -p flag in the "docker run" command expsoes the AIC REST API on port 5000 of the localhost.  The -e flag is used to set the enviormental variables.

### Local Install

If you haven't already cloned the repo, do so now:

    git clone https://github.com/imapex/aic_app

Create Virtual Environment and install dependencies:

    cd aic_app
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt

Set the required environment variables:

    export AIC_USER=<your-username-here>
    export AIC_PASSWORD=<your-password-here>

Start the application:

    python app.py

# Usage

The primary method of interacting with the application is via its REST API. The REST API binds to port 5000 of the local host when the application is started.

The URL path to the API is: 
    
    http://localhost:5000/aic/api/v1.0/

## REST APIs

| API | Description | Supported Methods |
| --- | --- | --- |
| http://localhost:5000/aic/api/v1.0/ | This is the root of the API. | GET
| http://localhost:5000/aic/api/v1.0/workflows | Displays a list of the registered workflows.| GET |
| http://localhost:5000/aic/api/v1.0/status | Displays the status of the API. | GET |
| http://localhost:5000/aic/api/v1.0/task | Task operations.| GET, POST |
| http://localhost:5000/aic/api/v1.0/task/x | ('x' is the task-id.) Displays the status of the task. | GET |

## Workflows

As of the v1.0 release, the only supported workflow is HBA Swap. 

| Name | Description |
| --- | --- | 
| HBA Swap | Changes the PWWN on a Cisco MDS Switch after an HBA failure. [Example below.](#example-hba-swap-task-submission) |

## API Examples

### Status Example

You can check the status of the application by accessing the 'status' API at this URL:

    http://localhost:5000/aic/api/v1.0/status

If the application is running, you will see the following output:

    {
    "Status": "Up"
    }

### Task Submission Example

Before submitting a new task you should gather the following information:

* IP Address of the device
* Device authentication credentials (As of the v1.0 release credentials are hard coded.)
* Name of the AIC workflow you plan to execute
* Any additional parameters needed by the AIC workflow 

#### Example HBA Swap Task Submission

This section will illustrate how to submit an HBA Swap task to the AIC app.

The "HBA Swap" workflow accepts five parameters via a JSON encoded payload:

| Parameter Name | Example | Description |
| --- | --- | --- |
| ip_address | 10.2.5.3 | IP address of the MDS Switch |
| selected-task | hba_swap | Name of the selected task |
| task_param1 | 11:11:11:11:11:11:11:11 | Current Physical World Wide Name |
| task_param2 | MDSDeviceAlias | Current Device Alias |
| task_param3 | 33:33:33:33:33:33:33:33 | New Physical World Wide Name |

All tasks are submitted via a POST method to this URL:

    http://localhost:5000/aic/api/v1.0/task

The POST message must contain the workflow parameters in a JSON encoded payload. An example POST method, using the 'curl' command is shown below: 

    curl -i -H "Content-Type: application/json" -X POST -d '{"ip_address":"127.0.0.1","selected-task":"hba_swap","task_param1":"11:11:11:11:11:11:11:11","task_param2":"OldDeviceAlias","task_param3":"33:33:33:33:33:33:33:33"}' http://localhost:5000/aic/api/v1.0/task

If the task completes successfully you will see output similar to the example shown below:

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

### Task Status Example

This section will illustrate how to check the status of a task that was previously submitted to the AIC app.

#### Listing All Tasks

You can view all of the previously submitted tasks by using the HTTP GET method to call the 'task' URL below:

    http://localhost:5000/aic/api/v1.0/task/

An example GET method, using the 'curl' command is shown below: 

    curl -i -H "Content-Type: application/json" -X GET http://127.0.0.1:5000/aic/api/v1.0/task

The output will be similar to the example below:

    {
      "task": [
        {
          "done": true, 
          "id": 1, 
          "ip_address": "172.22.163.35", 
          "selected-task": "hba_swap", 
          "task-parameter1": "11:11:11:11:11:11:11:11", 
          "task-parameter2": "OldDeviceAlias", 
          "task-parameter3": "33:33:33:33:33:33:33:33"
        }, 
        {
          "done": true, 
          "id": 2, 
          "ip_address": "172.22.163.36", 
          "selected-task": "hba_swap", 
          "task-parameter1": "11:11:11:11:11:11:11:11", 
          "task-parameter2": "OldDeviceAlias", 
          "task-parameter3": "33:33:33:33:33:33:33:33"
        }, 
        {
          "done": true, 
          "id": 3, 
          "ip_address": "172.22.163.37", 
          "selected-task": "hba_swap", 
          "task-parameter1": "11:11:11:11:11:11:11:11", 
          "task-parameter2": "OldDeviceAlias", 
          "task-parameter3": "33:33:33:33:33:33:33:33"
        }
      ]
    }

#### Viewing a Specific Task

As you can see in the output above, the AIC app assigns each task a unique task 'id'. We can use that id to check the status of an individual task, by appending the id to the end of the 'task' URL.

For example, if you'd like to view the status of the task with task id '2', append '2' to the end of the 'task' URL, as seen below, and call the URL with the HTTP GET method.

    http://localhost:5000/aic/api/v1.0/task/2

An example GET method, using the 'curl' command is shown below: 

    curl -i -H "Content-Type: application/json" -X GET http://127.0.0.1:5000/aic/api/v1.0/task/2

The output will be similar to the example below:

    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 265
    Server: Werkzeug/0.11.11 Python/2.7.12
    Date: Tue, 29 Nov 2016 21:36:32 GMT

    {
      "task": {
        "done": true, 
        "id": 2, 
        "ip_address": "172.22.163.36", 
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

This AIC app is licensed under the MIT License.