from pm4py.algo.filtering.common.attributes import attributes_common
from pm4py.algo.filtering.common.filtering_constants import CASE_CONCEPT_NAME
from pm4py.algo.filtering.common.filtering_constants import DECREASING_FACTOR
from pm4py.algo.filtering.pandas.pd_filtering_constants import MAX_NO_OF_ACTIVITIES_TO_RETAIN_FOR_DIAGRAM
from pm4py.algo.filtering.pandas.pd_filtering_constants import MIN_NO_OF_ACTIVITIES_TO_RETAIN_FOR_DIAGRAM
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.objects.log.util.xes import DEFAULT_TIMESTAMP_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY
from pm4py.util.constants import PARAM_MOST_COMMON_VARIANT


def apply_numeric_events(df, int1, int2, parameters=None):
    """
    Apply a filter on events (numerical filter)

    Parameters
    --------------
    df
        Dataframe
    int1
        Lower bound of the interval
    int2
        Upper bound of the interval
    parameters
        Possible parameters of the algorithm:
            PARAMETER_CONSTANT_ATTRIBUTE_KEY => indicates which attribute to filter
            positive => keep or remove events?

    Returns
    --------------
    filtered_df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}
    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    positive = parameters["positive"] if "positive" in parameters else True
    if positive:
        return df[(df[attribute_key] >= int1) & (df[attribute_key] <= int2)]
    else:
        return df[(df[attribute_key] < int1) | (df[attribute_key] > int2)]


def apply_numeric(df, int1, int2, parameters=None):
    """
    Filter dataframe on attribute values (filter cases)

    Parameters
    --------------
    df
        Dataframe
    int1
        Lower bound of the interval
    int2
        Upper bound of the interval
    parameters
        Possible parameters of the algorithm:
            PARAMETER_CONSTANT_ATTRIBUTE_KEY => indicates which attribute to filter
            positive => keep or remove traces with such events?

    Returns
    --------------
    filtered_df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}
    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    positive = parameters["positive"] if "positive" in parameters else True
    # stream_filter_key is helpful to filter on cases containing an event with an attribute
    # in the specified value set, but such events shall have an activity in particular.
    stream_filter_key1 = parameters["stream_filter_key1"] if "stream_filter_key1" in parameters else None
    stream_filter_value1 = parameters["stream_filter_value1"] if "stream_filter_value1" in parameters else None
    stream_filter_key2 = parameters["stream_filter_key2"] if "stream_filter_key2" in parameters else None
    stream_filter_value2 = parameters["stream_filter_value2"] if "stream_filter_value2" in parameters else None

    filtered_df_by_ev = df[(df[attribute_key] >= int1) & (df[attribute_key] <= int2)]
    if stream_filter_key1 is not None:
        filtered_df_by_ev = filtered_df_by_ev[filtered_df_by_ev[stream_filter_key1] == stream_filter_value1]
    if stream_filter_key2 is not None:
        filtered_df_by_ev = filtered_df_by_ev[filtered_df_by_ev[stream_filter_key2] == stream_filter_value2]

    i1 = df.set_index(case_id_glue).index
    i2 = filtered_df_by_ev.set_index(case_id_glue).index
    if positive:
        return df[i1.isin(i2)]
    return df[~i1.isin(i2)]


def apply_events(df, values, parameters=None):
    """
    Filter dataframe on attribute values (filter events)

    Parameters
    ----------
    df
        Dataframe
    values
        Values to filter on
    parameters
        Possible parameters of the algorithm, including:
            attribute_key -> Attribute we want to filter
            positive -> Specifies if the filter should be applied including traces (positive=True) or
            excluding traces (positive=False)
    Returns
    ----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}
    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    positive = parameters["positive"] if "positive" in parameters else True
    if positive:
        return df[df[attribute_key].isin(values)]
    else:
        return df[~df[attribute_key].isin(values)]


def apply(df, values, parameters=None):
    """
    Filter dataframe on attribute values (filter traces)

    Parameters
    ----------
    df
        Dataframe
    values
        Values to filter on
    parameters
        Possible parameters of the algorithm, including:
            case_id_glue -> Case ID column in the dataframe
            attribute_key -> Attribute we want to filter
            positive -> Specifies if the filter should be applied including traces (positive=True) or
            excluding traces (positive=False)
    Returns
    ----------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    case_id_glue = parameters[
        PARAMETER_CONSTANT_CASEID_KEY] if PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    positive = parameters["positive"] if "positive" in parameters else True

    return filter_df_on_attribute_values(df, values, case_id_glue=case_id_glue, attribute_key=attribute_key,
                                         positive=positive)


def apply_auto_filter(df, parameters=None):
    """
    Apply auto filter on activity values

    Parameters
    ------------
    df
        Dataframe
    parameters
        Possible parameters of the algorithm, including:
            activity_key -> Column containing the activity
            decreasingFactor -> Decreasing factor that should be passed to the algorithm

    Returns
    ------------
    df
        Filtered dataframe
    """
    if parameters is None:
        parameters = {}

    most_common_variant = parameters[PARAM_MOST_COMMON_VARIANT] if PARAM_MOST_COMMON_VARIANT in parameters else None

    if most_common_variant is None:
        most_common_variant = []

    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY
    decreasing_factor = parameters[
        "decreasingFactor"] if "decreasingFactor" in parameters else DECREASING_FACTOR

    if len(df) > 0:
        activities = get_attribute_values(df, activity_key)
        alist = attributes_common.get_sorted_attributes_list(activities)
        thresh = attributes_common.get_attributes_threshold(alist, decreasing_factor)

        return filter_df_keeping_activ_exc_thresh(df, thresh, activity_key=activity_key, act_count0=activities,
                                                  most_common_variant=most_common_variant)
    return df


def get_attribute_values(df, attribute_key, parameters=None):
    """
    Return list of attribute values contained in the specified column of the CSV

    Parameters
    -----------
    df
        Pandas dataframe
    attribute_key
        Attribute for which we want to known the values and the count
    parameters
        Possible parameters of the algorithm

    Returns
    -----------
    attributes_values_dict
        Attributes in the specified column, along with their count
    """
    if parameters is None:
        parameters = {}
    str(parameters)
    attributes_values_dict = dict(df[attribute_key].value_counts())
    # print("attributes_values_dict=",attributes_values_dict)
    return attributes_values_dict


def filter_df_on_attribute_values(df, values, case_id_glue="case:concept:name", attribute_key="concept:name",
                                  positive=True):
    """
    Filter dataframe on attribute values

    Parameters
    ----------
    df
        Dataframe
    values
        Values to filter on
    case_id_glue
        Case ID column in the dataframe
    attribute_key
        Attribute we want to filter
    positive
        Specifies if the filtered should be applied including traces (positive=True) or excluding traces
        (positive=False)

    Returns
    ----------
    df
        Filtered dataframe
    """
    if values is None:
        values = []
    filtered_df_by_ev = df[df[attribute_key].isin(values)]
    i1 = df.set_index(case_id_glue).index
    i2 = filtered_df_by_ev.set_index(case_id_glue).index
    if positive:
        return df[i1.isin(i2)]
    return df[~i1.isin(i2)]


def filter_df_keeping_activ_exc_thresh(df, thresh, act_count0=None, activity_key="concept:name",
                                       most_common_variant=None):
    """
    Filter a dataframe keeping activities exceeding the threshold

    Parameters
    ------------
    df
        Pandas dataframe
    thresh
        Threshold to use to cut activities
    act_count0
        (If provided) Dictionary that associates each activity with its count
    activity_key
        Column in which the activity is present

    Returns
    ------------
    df
        Filtered dataframe
    """
    if most_common_variant is None:
        most_common_variant = []

    if act_count0 is None:
        act_count0 = get_attribute_values(df, activity_key)
    act_count = [k for k, v in act_count0.items() if v >= thresh or k in most_common_variant]
    if len(act_count) < len(act_count0):
        df = df[df[activity_key].isin(act_count)]
    return df


def filter_df_keeping_spno_activities(df, activity_key="concept:name", max_no_activities=25):
    """
    Filter a dataframe on the specified number of attributes

    Parameters
    -----------
    df
        Dataframe
    activity_key
        Activity key in dataframe (must be specified if different from concept:name)
    max_no_activities
        Maximum allowed number of attributes

    Returns
    ------------
    df
        Filtered dataframe
    """
    activity_values_dict = dict(df[activity_key].value_counts())
    activity_values_ordered_list = []
    for act in activity_values_dict:
        activity_values_ordered_list.append([act, activity_values_dict[act]])
    activity_values_ordered_list = sorted(activity_values_ordered_list, key=lambda x: (x[1], x[0]), reverse=True)
    # keep only a number of attributes <= max_no_activities
    activity_values_ordered_list = activity_values_ordered_list[
                                   0:min(len(activity_values_ordered_list), max_no_activities)]
    activity_to_keep = [x[0] for x in activity_values_ordered_list]

    if len(activity_to_keep) < len(activity_values_dict):
        df = df[df[activity_key].isin(activity_to_keep)]
    return df


def get_kde_numeric_attribute(df, attribute, parameters=None):
    """
    Gets the KDE estimation for the distribution of a numeric attribute values

    Parameters
    -------------
    df
        Pandas dataframe
    attribute
        Numeric attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph


    Returns
    --------------
    x
        X-axis values to represent
    y
        Y-axis values to represent
    """
    if parameters is None:
        parameters = {}

    max_no_of_points_to_sample = parameters[
        "max_no_of_points_to_sample"] if "max_no_of_points_to_sample" in parameters else 100000
    red_df = df.dropna(subset=[attribute])
    if len(red_df) > max_no_of_points_to_sample:
        red_df = red_df.sample(n=max_no_of_points_to_sample)
    values = list(red_df[attribute])

    return attributes_common.get_kde_numeric_attribute(values, parameters=parameters)


def get_kde_numeric_attribute_json(df, attribute, parameters=None):
    """
    Gets the KDE estimation for the distribution of a numeric attribute values
    (expressed as JSON)

    Parameters
    --------------
    df
        Pandas dataframe
    attribute
        Numeric attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph

    Returns
    --------------
    json
        JSON representing the graph points
    """
    values = list(df.dropna(subset=[attribute])[attribute])

    return attributes_common.get_kde_numeric_attribute_json(values, parameters=parameters)


def get_kde_date_attribute(df, attribute=DEFAULT_TIMESTAMP_KEY, parameters=None):
    """
    Gets the KDE estimation for the distribution of a date attribute values

    Parameters
    -------------
    df
        Pandas dataframe
    attribute
        Date attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph


    Returns
    --------------
    x
        X-axis values to represent
    y
        Y-axis values to represent
    """
    if parameters is None:
        parameters = {}
    
    max_no_of_points_to_sample = parameters[
        "max_no_of_points_to_sample"] if "max_no_of_points_to_sample" in parameters else 100000
    red_df = df.dropna(subset=[attribute])
    if len(red_df) > max_no_of_points_to_sample:
        red_df = red_df.sample(n=max_no_of_points_to_sample)
    date_values = list(red_df[attribute])
    return attributes_common.get_kde_date_attribute(date_values, parameters=parameters)


def get_kde_date_attribute_json(df, attribute=DEFAULT_TIMESTAMP_KEY, parameters=None):
    """
    Gets the KDE estimation for the distribution of a date attribute values
    (expressed as JSON)

    Parameters
    --------------
    df
        Pandas dataframe
    attribute
        Date attribute to analyse
    parameters
        Possible parameters of the algorithm, including:
            graph_points -> number of points to include in the graph

    Returns
    --------------
    json
        JSON representing the graph points
    """
    values = list(df.dropna(subset=[attribute])[attribute])

    return attributes_common.get_kde_date_attribute_json(values, parameters=parameters)
