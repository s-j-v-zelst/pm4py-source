import pm4py


class Predictor:

    def train(self, trace_log, parameters=None):
        if parameters is None:
            parameters = pm4py.algo.transition_system.parameters.DEFAULT_PARAMETERS
        self.transition_system = pm4py.algo.transition_system.factory.apply(trace_log, parameters=parameters)






if __name__ == '__main__':
    log = pm4py.log.importer.xes.factory.apply('C:/Users/bas/Documents/tue/svn/private/logs/a32_logs/a32f0n05.xes')
    pred = Predictor()
    pred.train(log)