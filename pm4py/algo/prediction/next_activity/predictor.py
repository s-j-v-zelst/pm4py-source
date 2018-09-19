import pm4py


class Predictor:



    def train(self, trace_log, parameters=None):
        if parameters is None:
            parameters = pm4py.algo.ts.parameters.DEFAULT_PARAMETERS
        self.transition_system = ts.factory.apply(trace_log, parameters=parameters)
        self.activity_distribution =






