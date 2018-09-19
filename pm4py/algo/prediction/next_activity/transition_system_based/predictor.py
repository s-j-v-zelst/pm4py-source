import pm4py


class TransitionSystemBasedNextActivityPredictor:

    def __init__(self, trace_log, parameters=None):
        if parameters is None:
            parameters = pm4py.algo.transition_system.parameters.DEFAULT_PARAMETERS
        if pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
            parameters[pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = pm4py.log.util.xes.DEFAULT_NAME_KEY
        self.transition_system = pm4py.algo.transition_system.factory.apply(trace_log, parameters=parameters)
        self.activity_distribution = pm4py.log.util.trace_log.get_event_labels_counted(trace_log, pm4py.log.util.xes.DEFAULT_NAME_KEY)






if __name__ == '__main__':
    log = pm4py.log.importer.xes.factory.apply('C:/Users/bas/Documents/tue/svn/private/logs/a32_logs/a32f0n05.xes')
    pred = TransitionSystemBasedNextActivityPredictor(log)
    print(pred.activity_distribution)