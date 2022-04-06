# jomaul
An open source workflow automation API, built using Python and the Flask web framework.

## How does it work?
At its core, jomaul is meant to run jobs on a set of predefined schedules. Each job defines its own schedule, using one of the tool's built in schedule types. 

### JobHandler and Jobs
The JobManager class is responsible for receiving requests and running jobs with specified parameters and running the jobs when necessary. All Jobs are defined in the configured jobs directory and consist of only two functions. The first one is the __init__ function, which is responsible for defining the parameters that the job should use to run. The second is the run function, which is responsible for running the actual payload of the job.

Refer to the sample Job below.
    
    from jomaul.jomaul_core.Job import Job

    class PostTweet(Job):
        def __init__(self, job_config):
            super().__init__(config=job_config)

        def run(self, parameters={}):
            super().run(parameters = parameters)
            print(self.parameters['print_this'])
            return [True, None]


### Triggers, TriggerSets, TriggerHandler
Triggers and TriggerSets are jomauls way of running a job if a specified set of conditions are met. Each Trigger is meant to define a single condition and a TriggerSet is meant to group those Triggers using AND/OR operators. The TriggerHandler class is responsible for managing Triggers and TriggerSets, as well as communicating with JobHandler whenever a Job is triggered.
