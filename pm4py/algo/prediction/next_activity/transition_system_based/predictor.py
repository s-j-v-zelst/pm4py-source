import pm4py
import time

PARAM_KEY_TRANSITION_SYSTEM_DISC_PARAMS = 'param_disc'

class TransitionSystemBasedNextActivityPredictor:

    def __init__(self, trace_log, parameters=None):
        if parameters is None:
            parameters = dict()
            parameters[PARAM_KEY_TRANSITION_SYSTEM_DISC_PARAMS] = pm4py.algo.discovery.transition_system.parameters.DEFAULT_PARAMETERS
        if pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
            parameters[pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = pm4py.entities.log.util.xes.DEFAULT_NAME_KEY
        parameters[PARAM_KEY_TRANSITION_SYSTEM_DISC_PARAMS][pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = parameters[pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]

        self.parameters = parameters
        self.transition_system = pm4py.algo.discovery.transition_system.factory.apply(trace_log, parameters=self.parameters[PARAM_KEY_TRANSITION_SYSTEM_DISC_PARAMS])
        activity_distribution = pm4py.entities.log.util.trace_log.get_event_labels_counted(trace_log,  parameters[pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY])
        summ = sum(activity_distribution.values())
        self.activity_distribution = {k: activity_distribution[k] / summ for k in activity_distribution.keys()}

    def predict(self, prefix):
        '''

        :param prefix: trace of *events*
        :return:
        '''
        window = self.parameters[PARAM_KEY_TRANSITION_SYSTEM_DISC_PARAMS][pm4py.algo.discovery.transition_system.parameters.PARAM_KEY_WINDOW]
        state_seq = prefix[max(0, len(prefix)-window):len(prefix)]
        state_seq_cf = list(map(lambda e : e[self.parameters[pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]], state_seq))
        state = pm4py.algo.discovery.transition_system.versions.view_based.apply_abstr(state_seq_cf, self.parameters[PARAM_KEY_TRANSITION_SYSTEM_DISC_PARAMS])
        s = {'state': s for s in self.transition_system.states if s.name == state}
        s = s['state'] if len(s) > 0 else None
        if s is not None:
            sum = 0
            acts = dict()
            for t in s.outgoing:
                val = t.data[pm4py.entities.transition_system.transition_system.DECORATION_KEY_FREQUENCY]
                acts[t.name] = val if t.name not in acts else val + acts[t.name]
                sum += val
            return {k: acts[k] / sum for k in acts.keys()} if len(acts) > 0 else self.activity_distribution
        return self.activity_distribution








if __name__ == '__main__':
    log = pm4py.entities.log.importer.xes.factory.apply('C:/Users/zelst/Documents/tue/svn/logs/a12_logs/a12f0n00.xes')
    prms = dict()
    prms[PARAM_KEY_TRANSITION_SYSTEM_DISC_PARAMS] = dict(pm4py.algo.discovery.transition_system.parameters.DEFAULT_PARAMETERS)
    prms[PARAM_KEY_TRANSITION_SYSTEM_DISC_PARAMS][pm4py.algo.discovery.transition_system.parameters.PARAM_KEY_DIRECTION] = pm4py.algo.discovery.transition_system.parameters.DIRECTION_BACKWARD
    pred = TransitionSystemBasedNextActivityPredictor(log, prms)
    viz = pm4py.visualization.transition_system.factory.apply(pred.transition_system, parameters={"format":"svg"})
    viz.view()
    print(pred.activity_distribution)
    for trace in log:
        for i in range(1,len(trace)):
            prefix = trace[0:i]
            prefix_pretty = list(map( lambda event : event['concept:name'], prefix))
            print('prefix', prefix_pretty, 'prediction', pred.predict(prefix))
            time.sleep(1)