from pm4py.algo import transition_system as ts


class Predictor:



    def train(self, trace_log, parameters=None):
        if parameters is None:
            parameters = ts.parameters.DEFAULT_PARAMETERS

<<<<<<< Updated upstream
        self.
=======
        self.transition_system = ts.factory.apply(trace_log, parameters=parameters)



>>>>>>> Stashed changes


