import os
import difflib
import copy
import sys

from pm4py import util
from pm4py.algo.conformance import alignments as ali
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_MODEL_COST_FUNCTION
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_SYNC_COST_FUNCTION
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_TRACE_COST_FUNCTION
from pm4py.objects import log as log_lib
from pm4py.objects import petri as petri
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.conversion.log import factory as log_conv


def align(trace, net, im, fm, model_cost_function, sync_cost_function):
    trace_costs = list(map(lambda e: 1000, trace))
    params = dict()
    params[util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = log_lib.util.xes.DEFAULT_NAME_KEY
    params[PARAM_MODEL_COST_FUNCTION] = model_cost_function
    params[PARAM_TRACE_COST_FUNCTION] = trace_costs
    params[PARAM_SYNC_COST_FUNCTION] = sync_cost_function
    return ali.factory.apply_trace(trace, net, im, fm, parameters=params,
                                   version=ali.factory.VERSION_STATE_EQUATION_A_STAR)


def costs(alignment):
    return sum(map(lambda m: 0 if m[0] != '>>' and (m[1] != '>>' or m[1] is None) else 1, alignment))

def generate_exact_matching(matches):
    res = list()
    for m in matches[0:-1]:
        i = m[0]
        j = m[1]
        res.append((i, j))
        k = m[2]
        while k > 1:
            i += 1
            j += 1
            res.append((i, j))
            k -= 1
    return res


def get_model_based_moves_explaining_x_labels(alignment, start, x):
    fragment = list()
    i = start
    k = 0
    while k < x and i < len(alignment):
        move = alignment[i]
        if move[0] == '>>':
            fragment.append(copy.deepcopy(move))
        else:
            fragment.append(('>>', copy.deepcopy(move[1])))
            k += 1
        i += 1
    return fragment


def synthesize_approximate_alignment(seed, trace, seed_alignment, matches):
    synth = list()
    i = j = k = 0
    matching_exact = generate_exact_matching(matches)
    while seed_alignment[k][0] == '>>':
        synth.append(copy.deepcopy(seed_alignment[k]))
        k += 1
    for match_pair in matching_exact:
        if i < match_pair[0]:
            fragment = get_model_based_moves_explaining_x_labels(seed_alignment, k, match_pair[0]-i)
            synth.extend(fragment)
            i = match_pair[0]
            k += len(fragment)

        while j < match_pair[1]:
            synth.append((trace[j], '>>'))
            j += 1

        synth.append(copy.deepcopy(seed_alignment[k]))
        k += 1
        while k < len(seed_alignment) and seed_alignment[k][0] == '>>':
            synth.append(copy.deepcopy(seed_alignment[k]))
            k += 1
        i += 1
        j += 1
    if i < len(seed):
        synth.extend(get_model_based_moves_explaining_x_labels(seed_alignment, k, sys.maxsize))
    while j < len(trace):
        synth.append((trace[j], '>>'))
        j += 1

    return synth


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")
    pnml_path = os.path.join("..", "tests", "input_data", "running-example.pnml")

    # log_path = 'C:/Users/bas/Documents/tue/svn/private/logs/a32_logs/a32f0n05.xes'
    # pnml_path = 'C:/Users/bas/Documents/tue/svn/private/logs/a32_logs/a32.pnml'

    log = xes_importer.import_log(log_path)
    # log = log_conv.apply(log, parameters=None, variant=log_conv.TO_EVENT_STREAM)
    net, marking, fmarking = petri.importer.factory.apply(
        pnml_path)

    model_cost_function = dict()
    sync_cost_function = dict()
    for t in net.transitions:
        if t.label is not None:
            model_cost_function[t] = 1000
            sync_cost_function[t] = 0
        else:
            model_cost_function[t] = 1

    #print(ali.factory.apply(log, net, marking, fmarking))

    seed = log[0]
    seed_str = list(map(lambda e: e['concept:name'], seed))
    seed_alignment = ali.factory.apply(seed, net, marking, fmarking)
    for i in range(1, len(log)):
        trace_str = list(map(lambda e: e['concept:name'], log[i]))
        seq_match = difflib.SequenceMatcher(None, seed_str, trace_str)
        matches = seq_match.get_matching_blocks()
        approx = synthesize_approximate_alignment(seed_str, trace_str, seed_alignment['alignment'], matches)
        opt = ali.factory.apply(log[i], net, marking, fmarking)
        print('trace: ' + str(trace_str))
        print('opt: ' + str(opt['alignment']))
        print('approx: ' + str(approx))
        print('error: ' + str(costs(approx)) + ' - ' + str(costs(opt)) + ' = ' + str(costs(approx) - costs(opt)))


if __name__ == '__main__':
    execute_script()
