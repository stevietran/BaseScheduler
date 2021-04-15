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
- Prepare optimisation model
-- Variables: job list (i = 1,..,n), robot list (j = 1, 2)
-- Objective: minimise total time
-- constraints: each robot works on 1 job only

Assumption: Each robot requires 1 mins set up, 3 mins operation
Output: job list with start time, set-up time, end time

order with earlier due date first
## Deployment
### Set up remote development using SSH 

### 
uWSGI and Nginx

## TODO
### Version 0.1
- Fix output json to match with requirement's format
- Remove hardcode input and output
- Create a schedule by carton order due date