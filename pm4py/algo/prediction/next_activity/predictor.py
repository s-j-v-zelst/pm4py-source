from pm4py.algo import transition_system as ts


class Predictor:



    def train(self, trace_log, parameters=None):
        if parameters is None:
            parameters = ts.parameters.DEFAULT_PARAMETERS

        self.


