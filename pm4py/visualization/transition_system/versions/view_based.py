from pm4py.algo.transition_system.versions import view_based
from pm4py.models.transition_system import visualize as ts_viz

def apply(tsys, parameters=None):
    """
    Get visualization of a Transition System

    Parameters
    -----------
    tsys
        Transition system
    parameters
        Optional parameters of the algorithm

    Returns
    ----------
    gviz
        Graph visualization
    """
    gviz = ts_viz.graphviz.visualize(tsys)
    return gviz