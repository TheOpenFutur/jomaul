class Job:
    # Default initializer
    def __init__(self, config={}):
        self.__config = config
        self.__job_path = self.__config['job_path']
        if 'parameters' in self.__config.keys():
            self.parameters = self.__config['parameters']
        else:
            self.parameters = {}
        if 'required_parameters' in self.__config.keys():
            self.__required_parameters = self.__config['required_parameters']
        else:
            self.__required_parameters = {}

    # Returns the parameters for the targeted Job object
    def get_parameters(self):
        return self.parameters

    def get_path(self):
        return self.__job_path

    def get_config(self):
        return self.__config

    # Runs the main portion of the job, according to the configurations set above
    def run(self, parameters = {}):
        # Adds the new parameters to the parameters dictionary
        for parameter in parameters.keys():
            self.parameters[parameter] = parameters[parameter]
        # Validates required parameters
        for required_parameter in self.__required_parameters.keys():
            if required_parameter not in self.parameters.keys():
                return [False, "The following required parameter is missing: {}".format(required_parameter)]
            if self.__required_parameters[required_parameter] != None and type(self.parameters[required_parameter]) != self.__required_parameters[required_parameter]:
                return [False, "The following parameter is a {}, when it should be a {}: {}".format(type(self.parameters[required_parameter]), self.__required_parameters[required_parameter], required_parameter)]
