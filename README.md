## Requirements
-- client sends an API request with all carton orders needed to be filled
-- sever response with a sequence of carton order
-- the scheduler can be:
(1) by order due-date: whatever order whose has ealier due date will be scheduled first  

## Algorithmn
- API: /schedule
-- Write to 'order', 'carton' and 'SKU' tables the request content of REST API
-- Delete all old data
-- Run Scheduler
-- Prepare json output and return

## Scheduler


## Deployment
### Set up remote development using SSH 

### 
uWSGI and Nginx

## TODO
### Version 0.1
- Remove hardcode input and output
- Create a schedule by carton order due date