## Features
The project deploys a Web API served as a scheduler microservice for a manufacturing executive system.  Features of the system are:
- Utilise uWSGI and Nginx for hosting the API
- Documented by swagger module
- Utilise SQLite as the database engine to store and process data
- Data modelling with SQLAlchemy

## How To Run
- Install required modules in `requirements.txt` file
- run `server.py`
- Use content in `sample.json` file to test the API

## API: /schedule
![Alt text](https://github.com/stevietran/SchedulerWebAPI/blob/master/misc/ui.PNG)

Overview
- client sends an API request with all carton orders needed to be filled
- sever response with a sequence of carton order
- the scheduler can be:
(1) by order due-date: whatever order whose has ealier due date will be scheduled first  

When the API is calles:
- Write to 'order', 'carton' tables the request content of REST API
- Delete all old data
- Run `Scheduler`
- Prepare json output and return

## Scheduler
The project is only to showcase the framework, therefore a simple scheduler is implemented:
- Input: A list of cartons with items to be packed. The priority if for carton order with earlier due date
- There are two robots as machines. Assumption: Each robot requires 1 mins set up, 3 mins operation
- Output: job list with start time, set-up time, end time

## Deployment with `uWSGI` and `Nginx`
