import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import pm4py
import time

def execute_script():
    #logPath = "C:/Users/bas/Documents/tue/svn/private/logs/ilp_test_2_abcd_acbd.xes"
    logPath = os.path.join("..","tests","inputData","running-example.xes")
    log = pm4py.entities.log.importer.xes.factory.apply(logPath)
    prms = dict()
    prms[pm4py.algo.prediction.next_activity.transition_system_based.predictor.PARAM_KEY_TRANSITION_SYSTEM_DISC_PARAMS] = dict(
        pm4py.algo.discovery.transition_system.parameters.DEFAULT_PARAMETERS)
    prms[pm4py.algo.prediction.next_activity.transition_system_based.predictor.PARAM_KEY_TRANSITION_SYSTEM_DISC_PARAMS][
        pm4py.algo.discovery.transition_system.parameters.PARAM_KEY_DIRECTION] = pm4py.algo.discovery.transition_system.parameters.DIRECTION_BACKWARD
    pred = pm4py.algo.prediction.next_activity.transition_system_based.predictor.TransitionSystemBasedNextActivityPredictor(log, prms)
    viz = pm4py.visualization.transition_system.factory.apply(pred.transition_system, parameters={"format": "svg"})
    viz.view()
    print(pred.activity_distribution)
    for trace in log:
        for i in range(0, len(trace)):
            prefix = trace[0:i]
            prefix_pretty = list(map(lambda event: event['concept:name'], prefix))
            print('prefix', prefix_pretty, 'prediction', pred.predict(prefix))
            time.sleep(1)

if __name__ == '__main__':
    execute_script()
