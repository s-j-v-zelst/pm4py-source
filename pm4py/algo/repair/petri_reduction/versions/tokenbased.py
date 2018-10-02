from pm4py.entities import petri

def apply(net, parameters=None):
    """
    Apply petri_reduction on the Petrinet removing hidden transitions
    that are unused according to token-based replay

    Parameters
    -----------
    net
        Petri net
    parameters
        Parameters of the algorithm, including:
            aligned_traces -> Result of alignment according to token-based replay
    Returns
    -----------
    net
        Reduced Petri net
    """
    if parameters is None:
        parameters = {}

    aligned_traces = parameters["aligned_traces"]

    enabledTransInAtLeastOneTrace = set()

    for trace in aligned_traces:
        for trans in trace["actTrans"]:
            enabledTransInAtLeastOneTrace.add(trans)

    transitions = list(net.transitions)
    for trans in transitions:
        if trans.label is None:
            if not trans in enabledTransInAtLeastOneTrace:
                net = petri.utils.remove_transition(net, trans)

    return net