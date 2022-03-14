# Import system utilities
import os
import json
from datetime import datetime, timedelta
import importlib.util
#Import jomaul modules
from jomaul.Trigger import TriggerSet

class Schedule:
    # Default initializer
    def __init__(self, config={}):
        # Configure the schedule file path
        if 'schedule_file' in config.keys():
            self.__schedule_file = config['schedule_file']
        else:
            self.__schedule_file = "schedule.json"
        # Create or load the schedule
        if os.path.exists(self.__schedule_file):
            with open(self.__schedule_file, 'r') as schedule_file:
                self.__schedule = json.load(schedule_file)
        else:
            self.__schedule = {}

    # Updates each individual job schedule in self.__schedule
    def update_schedule(self, jobs):
        def update_job_status(self, job):
            # Calculates job status for jobs scheduled on an interval
            def interval_schedule(self, job):
                # If the job has not been ran, return a pending status
                if job['run_data']['last_run'] == None:
                    return "pending"
                # Compare the delta between now and when the job was last run to the scheduled interval
                schedule_delta = eval("timedelta({} = {})".format(job['schedule']['unit'], job['schedule']['frequency']))
                actual_delta = datetime.now() - datetime.fromisoformat(job['run_data']['last_run'])
                # If it is past the scheduled time, return a pending status
                if actual_delta >= schedule_delta:
                    return "pending"
                # If it is still not time to run this job, return a scheduled status
                else:
                    return "waiting"

            # Calculates job status for jobs dependent on the result of another job
            def dependent_schedule(self, job):
                return "waiting"

            # Calculates job status for jobs dependent on the result of another job
            def triggered_schedule(self, job):
                return "waiting"

            # Define a list of valid schedule types
            schedule_types = ["interval", "dependent", "triggered"]
            # If the schedule type is valid, run the appropriate schedule function
            if job['schedule']['schedule_type'] in schedule_types:
                return eval("{}_schedule(self, job)".format(job['schedule']['schedule_type']))
            # Return false if an unknown schedule type is supplied
            else:
                return False

        for job_name in jobs.keys():
            job_schedule = jobs[job_name].get_schedule()
            # Adds job schedule if the Job object is new
            if job_name not in self.__schedule.keys():
                self.__schedule[job_name] = {"schedule":job_schedule,"run_data":{"status":"pending","last_run":None,"last_run_result":None}}
            # Updates the job schedule, if necessary
            elif self.__schedule[job_name] != job_schedule:
                self.__schedule[job_name]['schedule'] = job_schedule
            # Updates job status
            self.__schedule[job_name]['run_data']['status'] = update_job_status(self, self.__schedule[job_name])

    # Saves the schedule to a JSON formatted file
    def save_to_disk(self):
        with open(self.__schedule_file, 'w') as schedule_file:
            json.dump(self.__schedule, schedule_file, indent=4)

    # Returns the current schedule, will update it first if update is set to True and the jobs object is not empty
    def get_schedule(self, update_jobs={}):
        if update_jobs != {}:
            self.update_schedule(jobs)
        return self.__schedule

    # Returns the run data of the specified job
    def get_run_data(self, job_name):
        if job_name in self.__schedule.keys():
            return self.__schedule[job_name]["run_data"]
        else:
            return {"status":"pending", "last_run":None, "last_run_result":None}

    #Updates the run data of the specified job
    def set_run_data(self, job_name, run_data):
        if job_name in self.__schedule.keys():
            self.__schedule[job_name]["run_data"] = run_data
            return True
        else:
            return False

    # Returns a dictionary of jobs dependent on the specified job
    def get_dependent_jobs(self, job_name):
        dependent_jobs = {}
        for job in self.__schedule.keys():
            if self.__schedule[job]['schedule']['schedule_type'] == "dependent":
                if self.__schedule[job]['schedule']['parent_job'] == job_name:
                    dependent_jobs[job] = self.__schedule[job]['schedule']
        return dependent_jobs

    # Returns a list of jobs associated with the specified trigger
    def get_triggered_jobs(self, trigger_name):
        triggered_jobs = []
        for job in self.__schedule.keys():
            if self.__schedule[job]['schedule']['schedule_type'] == "triggered":
                trigger_set = TriggerSet(config = self.__schedule[job]['schedule']['config'])
                if trigger_set.contains_trigger(trigger_name):
                    triggered_jobs.append([job, trigger_set])
        return triggered_jobs
