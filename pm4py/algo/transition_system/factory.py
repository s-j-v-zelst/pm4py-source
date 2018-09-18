from pm4py.algo.transition_system.versions import view_based

VIEW_BASED = "view_based"

VERSIONS = {VIEW_BASED: view_based.apply}

def apply(trace_log, parameters=None, variant="view_based"):
    """
    Find transition system given trace log

    Parameters
    -----------
    trace_log
        Trace log
    parameters
        Possible parameters of the algorithm, including:
            view
            window
            direction

    Returns
    ----------
    ts
        Transition system
    """
    return VERSIONS[variant](trace_log, parameters=parameters)