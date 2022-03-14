# Import utilities
import os
import json
import datetime

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
        if 'trigger_file' in config.keys():
            self.__trigger_file = config['trigger_file']
        else:
            self.__trigger_file = "trigger.json"
        # Create or load the trigger states
        if os.path.exists(self.__trigger_file):
            with open(self.__trigger_file, 'r') as trigger_file:
                self.__triggers = json.load(trigger_file)
                for trigger_name in self.__triggers.keys():
                    self.__triggers[trigger_name] = Trigger(
                        name=self.__triggers[trigger_name]['name'],
                        state=self.__triggers[trigger_name]['state'],
                        reset_interval=self.__triggers[trigger_name]['reset_interval'],
                        expiration=self.__triggers[trigger_name]['expiration']
                        )
        else:
            self.__triggers = {}

    # Saves the trigger states to a JSON formatted file
    def save_to_disk(self):
        with open(self.__trigger_file, 'w') as trigger_file:
            deserialized_triggers = {}
            for trigger_name in self.__triggers.keys():
                deserialized_triggers[trigger_name] = self.__triggers[trigger_name].serialize()
            json.dump(deserialized_triggers, trigger_file, indent=4)

    # Gets the current state of the specified trigger, assuming its False if the trigger is not found
    def get_trigger_state(self, trigger_name):
        if trigger_name in self.__triggers.keys():
            return self.__triggers[trigger_name].state()
        else:
            return False

    # Sets the state of the specified trigger, creating it if it does not exist
    def set(self, trigger_name, trigger_state, reset_interval=None):
        if isinstance(trigger_state, bool) and isinstance(trigger_name, str):
            if trigger_name in self.__triggers.keys():
                if self.__triggers[trigger_name].get_reset_interval() != reset_interval:
                    self.__triggers[trigger_name] = Trigger(trigger_name,trigger_state,reset_interval)
                else:
                    self.__triggers[trigger_name].set_state(trigger_state)
            else:
                self.__triggers[trigger_name] = Trigger(name=trigger_name,state=trigger_state,reset_interval=reset_interval)
            return True
        else:
            return "Invalid trigger object or trigger state."

class Trigger:
    def __init__(self, name="TriggerObject", state=False, reset_interval=None, expiration=None):
        self.__name = name
        self.__reset_interval = reset_interval
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
        return self.__reset_interval

    def expiration(self):
        return self.__expiration

    def set_state(self, state=True):
        if isinstance(state, bool):
            # Checks reset_interval if trigger state is being set to True
            if state == True:
                # If reset interval is configured, set expiration date
                if self.__reset_interval != None:
                    self.__expiration = datetime.now() + self.__reset_interval
            # Set state to True
            self.__state = state
            return [True, self.__state]
        else:
            return [False, "Invalid state supplied."]

    def serialize(self):
        return {
            "name":self.__name,
            "state":self.__state,
            "reset_interval":str(self.__reset_interval),
            "expiration":str(self.__expiration)
        }
