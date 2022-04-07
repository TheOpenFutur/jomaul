# Import utilities
import os
import json
from datetime import datetime

class TriggerSet:
    def __init__(self, config={}):
        errors = []
        if 'type' in config.keys():
            if isinstance(config['type'], str):
                if config['type'].lower() == "and" or config['type'].lower() == "or":
                    if 'trigger_list' in config.keys():
                        if isinstance(config['trigger_list'], list):
                            for trigger in config['trigger_list']:
                                if isinstance(trigger, dict):
                                    trigger = TriggerSet(config=trigger)
                                    if 'errors' in trigger.__dict__.keys():
                                        for error in trigger.errors:
                                            errors.append(error)
                                elif isinstance(trigger, str) == False:
                                    errors.append("All items within the trigger list must be of a dict/string type")
                        else:
                            errors.append("Trigger list must be a list object, the following type of object was supplied: {}".format(type(config['triggers'])))
                    else:
                        errors.append("'trigger_list' key missing from the trigger set definition")
                else:
                    errors.append("Invalid type supplied, must be AND/OR")
        else:
            errors.append("Type missing from trigger set, must be given a type of AND/OR")

        if len(errors) == 0:
            self.__type = config['type']
            self.__trigger_list  = config['trigger_list']
        else:
            self.errors = errors

    # Returns a list of the triggers within the TriggerSet
    def get_trigger_list(self):
        trigger_list = []
        for trigger in self.__trigger_list:
            if isinstance(trigger, TriggerSet):
                for trigger_set_trigger in trigger.get_trigger_list():
                    trigger_list.append(trigger_set_trigger)
            else:
                trigger_list.append(trigger)
        return trigger_list

    # Checks to see if a trigger name is found in the trigger list
    def contains_trigger(self, trigger_name):
        # Iterates through each trigger in the trigger list
        for trigger in self.__trigger_list:
            # Runs the contains_trigger function if trigger is a TriggerSet object
            if isinstance(trigger, dict):
                trigger = TriggerSet(config=trigger)
                # Returns True if it contains the specified trigger name
                if trigger.contains_trigger(trigger_name):
                    return True
            else:
                # Returns True if the specified trigger name is found
                if trigger == trigger_name:
                    return True
        # Returns False if the trigger is not found in the TriggerSet
        return False

    def evaluate(self, trigger_handler):
        # Only runs if the initializer ran without errors
        if 'errors' in self.__dict__.keys():
            return "Evaluation impossible, due to invalid trigger set definition"
        # Determines the trigger set type
        if self.__type.lower() == "and":
            # Iterates through each trigger and checks its state
            for trigger in self.__trigger_list:
                if isinstance(trigger, dict):
                    trigger = TriggerSet(config=trigger)
                    if trigger.evaluate(trigger_handler) == False:
                        return False
                else:
                    if trigger_handler.get_trigger_state(trigger) == False:
                        return False
            # Only returns True if all trigger states were positive
            return True
        else:
            # Iterates through each trigger and checks its state
            for trigger in self.__trigger_list:
                if isinstance(trigger, TriggerSet):
                    if trigger.evaluate(trigger_handler) == True:
                        return True
                else:
                    if trigger_handler.get_trigger_state(trigger) == True:
                        return True
            # Only returns False if all of the trigger states were negative
            return False

class TriggerHandler:
    def __init__(self, config={}):
        # Configure the trigger file path
        if 'trigger' in config.keys():
            self.__trigger_file = config['trigger']['trigger_file']
        else:
            self.__trigger_file = "data/trigger.json"
        # Create or load the trigger states
        if os.path.exists(self.__trigger_file):
            # Load data from trigger file
            with open(self.__trigger_file, 'r') as trigger_file:
                json_object = json.load(trigger_file)
                # Load trigger states
                self.__trigger_states = json_object['trigger_states']
                # Load trigger sets
                self.__trigger_sets = json_object['trigger_sets']
            # Build Trigger objects
            for trigger_name in self.__trigger_states.keys():
                self.__trigger_states[trigger_name]['trigger_object'] = Trigger(
                    name=self.__trigger_states[trigger_name]['name'],
                    state=self.__trigger_states[trigger_name]['state'],
                    config={
                        "reset_interval":self.__trigger_states[trigger_name]['reset_interval'],
                        "expiration":self.__trigger_states[trigger_name]['expiration']
                        }
                    )
            # Build TriggerSet objects
            for trigger_set_name in self.__trigger_sets.keys():
                self.__trigger_sets[trigger_set_name]['trigger_set_object'] = TriggerSet(
                    config = self.__trigger_sets[trigger_set_name]['config']
                )
        else:
            self.__trigger_states = {}
            self.__trigger_sets = {}

    # Saves the trigger states to a JSON formatted file
    def save_to_disk(self):
        with open(self.__trigger_file, 'w') as trigger_file:
            deserialized_triggers = {}
            for trigger_name in self.__triggers.keys():
                deserialized_triggers[trigger_name] = self.__triggers[trigger_name].serialize()
            json.dump(deserialized_triggers, trigger_file, indent=4)

    # Gets the current state of the specified trigger, assuming its False if the trigger is not found
    def get_trigger_state(self, trigger_name):
        if trigger_name in self.__trigger_states.keys():
            return self.__trigger_states[trigger_name]['trigger_object'].state()
        else:
            return False

    # Sets the state of the specified trigger, creating it if it does not exist
    def set(self, trigger_name, trigger_state, config={'reset_interval':None, 'type':'manual'}):
        if isinstance(trigger_state, bool) and isinstance(trigger_name, str):
            if trigger_name in self.__trigger_states.keys():
                if self.__trigger_states[trigger_name]['trigger_object'].get_reset_interval() != config['reset_interval']:
                    self.__trigger_states[trigger_name]['trigger_object'] = Trigger(trigger_name,trigger_state,config)
                else:
                    self.__trigger_states[trigger_name]['trigger_object'].set_state(trigger_state)
            else:
                self.__trigger_states[trigger_name]['trigger_object'] = Trigger(name=trigger_name,state=trigger_state,config=config)
            return True
        else:
            return "Invalid trigger object or trigger state."

    def set_trigger_states(self, trigger_states):
        # Created an empty list object for triggered jobs
        triggered_jobs = []
        # Iterate through each trigger name in the trigger_states object
        for trigger_name in trigger_states.keys():
            self.set(trigger_name, trigger_states[trigger_name])
            for trigger_set in self.__trigger_sets.keys():
                if self.__trigger_sets[trigger_set]['trigger_set_object'].contains_trigger(trigger_name) and self.__trigger_sets[trigger_set]['trigger_set_object'].evaluate(self):
                    for job_name in self.__trigger_sets[trigger_set]['mounted_jobs']:
                        if job_name not in triggered_jobs:
                            triggered_jobs.append(job_name)
        if len(triggered_jobs) != 0:
            return triggered_jobs
        else:
            return None

class Trigger:
    def __init__(self, name="TriggerObject", state=False, config={'reset_interval':None, 'type':'manual'}, expiration=None):
        self.__name = name
        self.__config = config
        self.__expiration = expiration
        if expiration != None:
            self.__state = state
        else:
            self.set_state(state=state)

    def name(self):
        return self.__name

    def state(self):
        # Reset trigger if it's expired
        if self.__expiration != None:
            if datetime.now() >= expiration and self.__state == True:
                self.__state = False
                self.__expiration = None
        # Return tirgger state
        return self.__state

    def get_reset_interval(self):
        return self.__config['reset_interval']

    def get_type(self):
        return self.__config['type']

    def expiration(self):
        return self.__expiration

    def set_state(self, state=True):
        if isinstance(state, bool):
            # Checks reset_interval if trigger state is being set to True
            if state == True:
                # If reset interval is configured, set expiration date
                if self.__config['reset_interval'] != None:
                    self.__expiration = datetime.now() + self.__config['reset_interval']
            # Set state to True
            self.__state = state
            return [True, self.__state]
        else:
            return [False, "Invalid state supplied."]

    def serialize(self):
        return {
            "name":self.__name,
            "state":self.__state,
            "config":{
                "reset_interval":str(self.__config['reset_interval']),
                "type":self.__config['type']
            },
            "expiration":str(self.__expiration)
        }
