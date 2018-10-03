from pm4py.algo.discovery.transition_system.versions import view_based

VIEW_BASED = "view_based"

VERSIONS = {VIEW_BASED: view_based.apply}


def apply(trace_log, parameters=None, variant=VIEW_BASED):
    """
    Find transition system given trace log

    Parameters
    -----------
    trace_log
        Trace log
    parameters
        Possible parameters of the algorithm, including:

    variant which variant to use

    Returns
    ----------
    ts
        Transition system
    """
    return VERSIONS[variant](trace_log, parameters=parameters)