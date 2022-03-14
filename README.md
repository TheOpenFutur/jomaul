# jomaul
A suite of open source tools that allow end-users to build system integrations and automations requiring little to no programming.

## How does it work?
At its core, jomaul is meant to run jobs on a set of predefined schedules. Each job defines its own schedule, using one of the tool's built in schedule types. 

### JobManager and Jobs
The JobManager class is responsible for reading through the schedule and trigger list and running the jobs when necessary. All Jobs are defined in the configured jobs directory and consist of only two functions. The first one is the __init__ function, which is responsible for defining the schedule. The second is the run function, which is responsible for running the actual payload of the job.

Refer to the sample Job below.
    
    from jomaul_core.Job import Job
    
    class PrintJob(Job):
        def __init__(self):
            super().__init__(
            config={
                    "schedule":{
                        "schedule_type":"interval",
                        "unit":"seconds",
                        "frequency":3
                        }
                    })

    def run(self, parent_job_result=None):
        print("This job ran.")
        return [True, "It ran."]

### Schedules
Currently, jomaul supports 3 different types of schedules; Interval, Dependent, and Triggered. Read below to get a better understanding of each specific schedule type. Each job's schedule data is saved to 
* Jobs ran on an interval schedule are ran after a preset amount of time, with the clock resetting after each time the job is ran.
* Dependent jobs are ran when their parent job's run results meet the specified criteria.
* Triggered jobs are ran whenever a predefined set of conditions are met, those condtions being defined using Trigger and TriggerSet objects.

### Triggers and TriggerSets
Triggers and TriggerSets are jomauls way of running a job if multiple conditions are met, as opposed to dependent jobs which rely on only one condition (the run results of the defined parent job). Each Trigger is meant to define a single condition and a TriggerSet is meant to group those Triggers using AND/OR operators.
