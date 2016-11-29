# Automated Infrastructure Configuration Framework v1.0

Any applicable badges (build/documentation/collaboration/licenses should go here

## Description

The Automated Infrastrucutre Configuration (AIC) Framework is a microservce based application that leverages APIs, on platformms created by Cisco Systems, to automate common infrastrucutre configuration tasks.

#  aic_app 

This repository contains the main application logic used to implement the northbound REST API, as well as the logic needed to execute the desired configuration workflow.

The northbound REST API is used to submit configuration tasks to the application.

At present, the only configuration task that can be submitted is called HBA Swap.

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
* /plugins - Displays a list of the registered plug-ins.
* /status - Displays the status of the API.
* /task - Task operations.
* /task/<integer> - Displays the status of the task.

# Development

Test coverage is poor right now.  Tests can be run by executing:
    
    python tests.py

# License

Include any applicable licenses here as well as LICENSE.TXT in the root of the repository

