import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))
import random
from os import listdir
from os.path import join
import pm4py
from sklearn.metrics import brier_score_loss
import time


def compute_average_brier_score(predictor, test_log):
    brier_scores = list()
    for trace in test_log:
        for i in range(0, len(trace)):
            prefix = trace[0:i]
            prediction = predictor.predict(prefix)

            gt = trace[i][pm4py.entities.log.util.xes.DEFAULT_NAME_KEY]
            y = list()
            y_hat = list()
            for i in range(0, len(acts)):
                y.append(1 if acts[i] == gt else 0)
                y_hat.append(prediction[acts[i]] if acts[i] in prediction else 0)

            brier_score = brier_score_loss(y, y_hat)
            brier_scores.append(brier_score)
            # prefix_pretty = list(map(lambda event: event['concept:name'], prefix))
            # print('prefix:', prefix_pretty, 'ground truth:', gt, 'prediction:', predictor.predict(prefix))
            # print('y', y, 'y_hat', y_hat)
            # print('brier', brier_score)
            # time.sleep(1)
    avg_brier = sum(brier_scores) / len(brier_scores)
    # print(log_file, run, total_brier)
    return avg_brier


if __name__ == "__main__":

    # for reproducibility
    random.seed(22)

    logs_path = os.path.join("..", "data")
    out_path = os.path.join("..", 'output')
    for log_file in listdir(logs_path):
        if log_file.endswith('.xes.gz'):
            print(log_file)
            time.sleep(1)
            log = pm4py.entities.log.importer.xes.factory.apply(join(logs_path, log_file))
            for run in range(3):
                random.shuffle(log)
                activity_distribution = pm4py.entities.log.util.trace_log.get_event_labels_counted(log,
                                                                                                   pm4py.entities.log.util.xes.DEFAULT_NAME_KEY)
                acts = list(activity_distribution.keys())
                elems_per_fold = int(round(len(log) / 3))
                train = log[:2 * elems_per_fold]
                test = log[2 * elems_per_fold:]

                random.shuffle(train)
                n_val_traces = int(round(len(train) * 0.2))
                val_selection = train[:n_val_traces]
                train_selection = train[n_val_traces:]

                prms_default = dict()
                prms_default[
                    pm4py.algo.prediction.next_activity.transition_system_based.predictor.PARAM_KEY_TRANSITION_SYSTEM_DISC_PARAMS] = dict(
                    pm4py.algo.discovery.transition_system.parameters.DEFAULT_PARAMETERS)
                prms_default[
                    pm4py.algo.prediction.next_activity.transition_system_based.predictor.PARAM_KEY_TRANSITION_SYSTEM_DISC_PARAMS][
                    pm4py.algo.discovery.transition_system.parameters.PARAM_KEY_DIRECTION] = pm4py.algo.discovery.transition_system.parameters.DIRECTION_BACKWARD

                prm_list = list()
                briers_list = list()
                for window in range(1, 6):
                    if window > 1:
                        for view in pm4py.algo.discovery.transition_system.parameters.VIEWS:
                            print('window', window, 'view', view)
                            prms = dict(prms_default)
                            prms_disc = dict(prms[
                                pm4py.algo.prediction.next_activity.transition_system_based.predictor.PARAM_KEY_TRANSITION_SYSTEM_DISC_PARAMS])
                            prms_disc[pm4py.algo.discovery.transition_system.parameters.PARAM_KEY_WINDOW] = window
                            prms_disc[pm4py.algo.discovery.transition_system.parameters.PARAM_KEY_VIEW] = view
                            prms[
                                pm4py.algo.prediction.next_activity.transition_system_based.predictor.PARAM_KEY_TRANSITION_SYSTEM_DISC_PARAMS] = prms_disc
                            prm_list.append(prms)
                            predictor = pm4py.algo.prediction.next_activity.transition_system_based.predictor.TransitionSystemBasedNextActivityPredictor(
                                train_selection, prms)
                            briers_list.append(compute_average_brier_score(predictor, val_selection))
                            print(prm_list)
                            print(briers_list)
                    else:
                        print('window', window)
                        prms = dict(prms_default)
                        prms_disc = dict(prms[
                            pm4py.algo.prediction.next_activity.transition_system_based.predictor.PARAM_KEY_TRANSITION_SYSTEM_DISC_PARAMS])
                        prms_disc[pm4py.algo.discovery.transition_system.parameters.PARAM_KEY_WINDOW] = window
                        prms_disc[
                            pm4py.algo.discovery.transition_system.parameters.PARAM_KEY_VIEW] = pm4py.algo.discovery.transition_system.parameters.VIEW_SET
                        prms[
                            pm4py.algo.prediction.next_activity.transition_system_based.predictor.PARAM_KEY_TRANSITION_SYSTEM_DISC_PARAMS] = prms_disc
                        prm_list.append(prms)
                        predictor = pm4py.algo.prediction.next_activity.transition_system_based.predictor.TransitionSystemBasedNextActivityPredictor(
                            train_selection, prms)
                        briers_list.append(compute_average_brier_score(predictor, val_selection))
                        print(prm_list)
                        print(briers_list)

                print(log_file, min(briers_list), briers_list.index(min(briers_list)))
                best_prms = prm_list[briers_list.index(min(briers_list))]
                print(log_file, best_prms)
                predictor = pm4py.algo.prediction.next_activity.transition_system_based.predictor.TransitionSystemBasedNextActivityPredictor(
                    train, best_prms)
                avg_brier = compute_average_brier_score(predictor, test)
                print(log_file, 'brier:', avg_brier)
                file_path = os.path.join(out_path, (log_file + '.csv'))
                if not os.path.isfile(file_path):
                    f = open(file_path, 'a')
                    f.write('run\tbrier\tparams\n')
                f = open(file_path, 'a')
                f.write(str(run) + '\t' + str(avg_brier) + '\t' + str(best_prms)+ '\n')
