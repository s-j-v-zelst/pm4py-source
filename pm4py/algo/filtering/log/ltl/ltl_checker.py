from pm4py.objects.conversion.log import factory as log_conv_factory
from pm4py.objects.log.log import EventLog
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY, DEFAULT_RESOURCE_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY, PARAMETER_CONSTANT_RESOURCE_KEY

POSITIVE = "positive"


def A_eventually_B(log, A, B, parameters=None):
    """
    Applies the A eventually B rule

    Parameters
    ------------
    log
        Log
    A
        A attribute value
    B
        B attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - If True, returns all the cases containing A and B and in which A was eventually followed by B
        - If False, returns all the cases not containing A or B, or in which an instance of A was not eventually
        followed by an instance of B

    Returns
    ------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    if not isinstance(log, EventLog):
        log = log_conv_factory.apply(log, variant=log_conv_factory.TO_EVENT_LOG, parameters=parameters)

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    positive = parameters[POSITIVE] if POSITIVE in parameters else True

    new_log = EventLog()

    for trace in log:
        occ_A = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == A]
        occ_B = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == B]

        if len(A) > 0 and len(occ_B) > 0 and occ_A[-1] < occ_B[-1]:
            if positive:
                new_log.append(trace)
        elif not positive:
            new_log.append(trace)

    return new_log


def A_eventually_B_eventually_C(log, A, B, C, parameters=None):
    """
    Applies the A eventually B eventually C rule

    Parameters
    ------------
    log
        Log
    A
        A attribute value
    B
        B attribute value
    C
        C attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - If True, returns all the cases containing A, B and C and in which A was eventually followed by B and B was eventually followed by C
        - If False, returns all the cases not containing A or B or C, or in which an instance of A was not eventually
        followed by an instance of B or an instance of B was not eventually followed by C

    Returns
    ------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    if not isinstance(log, EventLog):
        log = log_conv_factory.apply(log, variant=log_conv_factory.TO_EVENT_LOG, parameters=parameters)

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    positive = parameters[POSITIVE] if POSITIVE in parameters else True

    new_log = EventLog()

    for trace in log:
        occ_A = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == A]
        occ_B = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == B]
        occ_C = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == C]

        if len(occ_A) > 0 and len(occ_B) > 0 and len(occ_C) > 0 and occ_A[-1] < occ_B[-1] < occ_C[-1]:
            if positive:
                new_log.append(trace)
        elif not positive:
            new_log.append(trace)

    return new_log


def A_next_B_next_C(log, A, B, C, parameters=None):
    """
    Applies the A next B next C rule

    Parameters
    ------------
    log
        Log
    A
        A attribute value
    B
        B attribute value
    C
        C attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - If True, returns all the cases containing A, B and C and in which A was directly followed by B and B was directly followed by C
        - If False, returns all the cases not containing A or B or C, or in which none instance of A was directly
        followed by an instance of B and B was directly followed by C

    Returns
    ------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    if not isinstance(log, EventLog):
        log = log_conv_factory.apply(log, variant=log_conv_factory.TO_EVENT_LOG, parameters=parameters)

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    positive = parameters[POSITIVE] if POSITIVE in parameters else True

    new_log = EventLog()

    for trace in log:
        occ_A = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == A]
        occ_B = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == B]
        occ_C = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == C]

        found = False

        for a in occ_A:
            for b in occ_B:
                for c in occ_C:
                    if (b-a) == 1 and (c-b) == 1:
                        found = True

        if found:
            if positive:
                new_log.append(trace)
        elif not positive:
            new_log.append(trace)

    return new_log


def four_eyes_principle(log, A, B, parameters=None):
    """
    Verifies the Four Eyes Principle given A and B

    Parameters
    -------------
    log
        Log
    A
        A attribute value
    B
        B attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - if True, then filters all the cases containing A and B which have empty intersection between the set
          of resources doing A and B
        - if False, then filters all the cases containing A and B which have no empty intersection between the set
          of resources doing A and B

    Returns
    --------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    if not isinstance(log, EventLog):
        log = log_conv_factory.apply(log, variant=log_conv_factory.TO_EVENT_LOG, parameters=parameters)

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    resource_key = parameters[
        PARAMETER_CONSTANT_RESOURCE_KEY] if PARAMETER_CONSTANT_RESOURCE_KEY in parameters else DEFAULT_RESOURCE_KEY
    positive = parameters[POSITIVE] if POSITIVE in parameters else True

    new_log = EventLog()

    for trace in log:
        occ_A = set([trace[i][resource_key] for i in range(len(trace)) if
                     attribute_key in trace[i] and resource_key in trace[i] and trace[i][attribute_key] == A])
        occ_B = set([trace[i][resource_key] for i in range(len(trace)) if
                     attribute_key in trace[i] and resource_key in trace[i] and trace[i][attribute_key] == B])

        if len(occ_A) > 0 and len(occ_B) > 0:
            inte = occ_A.intersection(occ_B)

            if not positive and len(inte) > 0:
                new_log.append(trace)
            elif positive and len(inte) == 0:
                new_log.append(trace)

    return new_log


def attr_value_different_persons(log, A, parameters=None):
    """
    Checks whether an attribute value is assumed on events done by different resources

    Parameters
    ------------
    log
        Log
    A
        A attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
            - if True, then filters all the cases containing occurrences of A done by different resources
            - if False, then filters all the cases not containing occurrences of A done by different resources

    Returns
    -------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    if not isinstance(log, EventLog):
        log = log_conv_factory.apply(log, variant=log_conv_factory.TO_EVENT_LOG, parameters=parameters)

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    resource_key = parameters[
        PARAMETER_CONSTANT_RESOURCE_KEY] if PARAMETER_CONSTANT_RESOURCE_KEY in parameters else DEFAULT_RESOURCE_KEY
    positive = parameters[POSITIVE] if POSITIVE in parameters else True

    new_log = EventLog()

    for trace in log:
        occ_A = set([trace[i][resource_key] for i in range(len(trace)) if
                     attribute_key in trace[i] and resource_key in trace[i] and trace[i][attribute_key] == A])
        if len(occ_A) > 1:
            if positive:
                new_log.append(trace)
        elif not positive:
            new_log.append(trace)

    return new_log
