from pm4py.entities.log import util as log_util
from pm4py.entities.transition_system import transition_system as ts
import collections
from pm4py.util import constants
from pm4py.algo.discovery.transition_system.parameters import *
import pm4py

'''
TODO: when adding performance statistics to the transition system, just create sequences of events, and apply the control-flow 
abstraction on top of the sequence when we are effectively creating the states 
'''

def apply(trace_log, parameters=None):
    if parameters is None:
        parameters = {}
    for parameter in DEFAULT_PARAMETERS:
        if not parameter in parameters:
            parameters[parameter] = DEFAULT_PARAMETERS[parameter]
    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else log_util.xes.DEFAULT_NAME_KEY
    transition_system = ts.TransitionSystem()
    control_flow_log = log_util.trace_log.project_traces(trace_log, activity_key)
    l = (list(map(lambda t: __compute_view_sequence(t, parameters), control_flow_log)))
    for vs in l:
        __construct_state_path(vs, transition_system, parameters)
    return transition_system


def __construct_state_path(view_sequence, transition_system, parameters):
    for i in range(0, len(view_sequence) - 1):
        sf = {'state': s for s in transition_system.states if s.name == view_sequence[i][0]}
        sf = __decorate_state(sf['state'] if len(sf) > 0 else ts.TransitionSystem.State(view_sequence[i][0]), parameters)
        st = {'state': s for s in transition_system.states if s.name == view_sequence[i + 1][0]}
        st = __decorate_state(st['state'] if len(st) > 0 else ts.TransitionSystem.State(view_sequence[i + 1][0]), parameters)
        t = {'t': t for t in sf.outgoing if t.name == view_sequence[i][1] and t.from_state == sf and t.to_state == st}
        if len(t) == 0:
            t = ts.TransitionSystem.Transition(view_sequence[i][1], sf, st)
            sf.outgoing.add(t)
            st.incoming.add(t)
        else:
            t = t['t']
        t = __decorate_transition(t, parameters)
        transition_system.states.add(sf)
        transition_system.states.add(st)
        transition_system.transitions.add(t)


def __decorate_state(state, parameters):
    if pm4py.algo.discovery.transition_system.parameters.PARAM_KEY_DECORATION in parameters:
        if pm4py.algo.discovery.transition_system.parameters.DECORATION_ARC_FREQUENCY in parameters[
            pm4py.algo.discovery.transition_system.parameters.PARAM_KEY_DECORATION]:
            if pm4py.entities.transition_system.transition_system.DECORATION_KEY_FREQUENCY in state.data:
                state.data[pm4py.entities.transition_system.transition_system.DECORATION_KEY_FREQUENCY] += 1
            else:
                state.data[pm4py.entities.transition_system.transition_system.DECORATION_KEY_FREQUENCY] = 1
    return state


def __decorate_transition(transition, parameters):
    if pm4py.algo.discovery.transition_system.parameters.PARAM_KEY_DECORATION in parameters:
        if pm4py.algo.discovery.transition_system.parameters.DECORATION_ARC_FREQUENCY in parameters[
            pm4py.algo.discovery.transition_system.parameters.PARAM_KEY_DECORATION]:
            if pm4py.entities.transition_system.transition_system.DECORATION_KEY_FREQUENCY in transition.data:
                transition.data[pm4py.entities.transition_system.transition_system.DECORATION_KEY_FREQUENCY] += 1
            else:
                transition.data[pm4py.entities.transition_system.transition_system.DECORATION_KEY_FREQUENCY] = 1
    return transition

def __compute_view_sequence(trace, parameters):
    view_sequences = list()
    for i in range(0, len(trace) + 1):
        if parameters[PARAM_KEY_DIRECTION] == DIRECTION_FORWARD:
            view_sequences.append((apply_abstr(trace[i:i + parameters[PARAM_KEY_WINDOW]], parameters),
                                   trace[i] if i < len(trace) else None))
        else:
            view_sequences.append((apply_abstr(trace[max(0, i - parameters[PARAM_KEY_WINDOW]):i], parameters),
                                   trace[i] if i < len(trace) else None))
    return view_sequences


def apply_abstr(seq, parameters):
    case = {
        VIEW_SEQUENCE: list,
        VIEW_MULTI_SET: collections.Counter,
        VIEW_SET: set
    }
    return case[parameters[PARAM_KEY_VIEW]](seq) if len(seq) > 0 else case[parameters[PARAM_KEY_VIEW]]()
