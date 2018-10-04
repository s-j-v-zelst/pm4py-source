import re, codecs, random, math, textwrap
from collections import defaultdict, deque, Counter
import operator
from sys import argv
from os import listdir
from os.path import join
import pm4py
from sklearn.metrics import brier_score_loss

import time

if __name__ == "__main__":

    # for reproducibility
    random.seed(22)

    logs_path = "C:/Users/zelst/github/taxxer/rnnalpha/data"
    for log_file in listdir(logs_path):
        if log_file.endswith('.xes.gz'):
            print(log_file)
            log = pm4py.entities.log.importer.xes.factory.apply(join(logs_path,log_file))
            for run in range(3):
                random.shuffle(log)
                activity_distribution = pm4py.entities.log.util.trace_log.get_event_labels_counted(log, pm4py.entities.log.util.xes.DEFAULT_NAME_KEY)
                acts = list(activity_distribution.keys())
                elems_per_fold = int(round(len(log) / 3))
                train = log[:2 * elems_per_fold]
                test = log[2 * elems_per_fold:]

                #random.shuffle(train)
                #n_val_traces = int(round(len(train) * 0.2))
                #val_selection = train[:n_val_traces]
                #train_selection = train[n_val_traces:]

                #TODO here we have to loop over the parameters and select the best model
                prms = dict()
                prms[
                    pm4py.algo.prediction.next_activity.transition_system_based.predictor.PARAM_KEY_TRANSITION_SYSTEM_DISC_PARAMS] = dict(
                    pm4py.algo.discovery.transition_system.parameters.DEFAULT_PARAMETERS)
                prms[
                    pm4py.algo.prediction.next_activity.transition_system_based.predictor.PARAM_KEY_TRANSITION_SYSTEM_DISC_PARAMS][
                    pm4py.algo.discovery.transition_system.parameters.PARAM_KEY_DIRECTION] = pm4py.algo.discovery.transition_system.parameters.DIRECTION_BACKWARD
                predictor = pm4py.algo.prediction.next_activity.transition_system_based.predictor.TransitionSystemBasedNextActivityPredictor(
                    train, prms)


                brier_scores = list()
                for trace in test:
                    for i in range(0, len(trace)):
                        prefix = trace[0:i]
                        prediction = predictor.predict(prefix)

                        gt = trace[i][pm4py.entities.log.util.xes.DEFAULT_NAME_KEY]
                        y = list()
                        y_hat = list()
                        for i in range(0, len(acts)):
                            y.append(1 if acts[i] == gt else 0)
                            y_hat.append(prediction[acts[i]] if acts[i] in prediction else 0)

                        brier_score = brier_score_loss(y,y_hat)
                        brier_scores.append(brier_score)
                        prefix_pretty = list(map(lambda event: event['concept:name'], prefix))
                        #print('prefix:', prefix_pretty, 'ground truth:', gt, 'prediction:', predictor.predict(prefix))
                        #print('y', y, 'y_hat', y_hat)
                        #print('brier', brier_score)
                        #time.sleep(1)
                total_brier = sum(brier_scores) / len(brier_scores)
                print(log_file, run, total_brier)
