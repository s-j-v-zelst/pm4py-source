import copy
import time
import datetime
import os

from pm4py.objects.petri import petrinet
from pm4py.objects.petri import utils as pn_util
from pm4py.objects.petri.importer import factory as pnml_import
from pm4py.objects.process_tree import pt_operator
from pm4py.objects.process_tree import util as pt_util
from pm4py.visualization.petrinet import factory as petri_viz
from pm4py.visualization.process_tree import factory as pt_viz
from pm4py.algo.simulation.tree_generator import factory as pt_gen
from pm4py.objects.conversion.process_tree import factory as pt_conv

# random string to identify transitions that are added to the net by the algorithm (ugly is king)
TRANSITION_PREFIX = 'qioqhacaoijdsafdqhjsalkj;nvas'


def generate_label_for_transition(t):
    return 'tau' if t.label is None else '\'' + t.label + '\'' if not t.name.startswith(
        TRANSITION_PREFIX) else t.label


def generate_new_binary_transition(t1, t2, operator, net):
    t = petrinet.PetriNet.Transition(TRANSITION_PREFIX + str(datetime.datetime.now()))
    t.label = str(operator) + '(' + generate_label_for_transition(
        t1) + ', ' + generate_label_for_transition(t2) + ')'
    return t


def binary_loop_detection(net):
    trans_set_1 = copy.copy(net.transitions)
    trans_set_2 = copy.copy(net.transitions)
    for t1 in trans_set_1:
        for t2 in trans_set_2:
            if t1 != t2:
                pre_t1 = pn_util.pre_set(t1)
                post_t1 = pn_util.post_set(t1)
                pre_t2 = pn_util.pre_set(t2)
                post_t2 = pn_util.post_set(t2)
                if len(pre_t1) == 1 and len(post_t1) == 1 and len(pre_t2) == 1 and len(post_t2) == 1 and len(list(pre_t1)[0].out_arcs) == 1 and pre_t1 == post_t2 and len(
                        pre_t2) == 1 and len(list(pre_t2)[0].in_arcs) == 1 and pre_t2 == post_t1:
                    t = petrinet.PetriNet.Transition(TRANSITION_PREFIX + str(datetime.datetime.now()))
                    t.label = str(pt_operator.Operator.LOOP) + '(' + generate_label_for_transition(
                        t1) + ', ' + generate_label_for_transition(t2)  + ')'
                    net.transitions.add(t)
                    for a in t1.in_arcs:
                        pn_util.add_arc_from_to(a.source, t, net)
                    for a in t1.out_arcs:
                        pn_util.add_arc_from_to(t, a.target, net)
                    pn_util.remove_transition(net, t1)
                    pn_util.remove_transition(net, t2)
                    return net
    return None


def binary_parallel_detection(net):
    trans_set_1 = copy.copy(net.transitions)
    trans_set_2 = copy.copy(net.transitions)
    for t1 in trans_set_1:
        for t2 in trans_set_2:
            if t1 != t2:
                pre_t1 = pn_util.pre_set(t1)
                pre_t2 = pn_util.pre_set(t2)
                if len(pre_t1) == 1 and len(pre_t2) == 1 and pre_t1 != pre_t2:
                    post_t1 = pn_util.post_set(t1)
                    post_t2 = pn_util.post_set(t2)
                    if len(post_t1) == 1 and len(post_t2) == 1 and post_t1 != post_t2:
                        pre_pre_1 = pn_util.pre_set(list(pre_t1)[0])
                        pre_pre_2 = pn_util.pre_set(list(pre_t2)[0])
                        post_post_1 = pn_util.post_set(list(post_t1)[0])
                        post_post_2 = pn_util.post_set(list(post_t2)[0])
                        if pre_pre_1 == pre_pre_2 and post_post_1 == post_post_2:
                            t = generate_new_binary_transition(t1, t2, pt_operator.Operator.PARALLEL, net)
                            net.transitions.add(t)
                            for a in t1.in_arcs:
                                pn_util.add_arc_from_to(a.source, t, net)
                            for a in t1.out_arcs:
                                pn_util.add_arc_from_to(t, a.target, net)
                            for a in copy.copy(t2.in_arcs):
                                pn_util.remove_place(net, a.source)
                            for a in copy.copy(t2.out_arcs):
                                pn_util.remove_place(net, a.target)
                            pn_util.remove_transition(net, t1)
                            pn_util.remove_transition(net, t2)
                            return net
    return None


def binary_choice_detection(net):
    trans_set_1 = copy.copy(net.transitions)
    trans_set_2 = copy.copy(net.transitions)
    for t1 in trans_set_1:
        for t2 in trans_set_2:
            if t1 != t2:
                pre_t1 = pn_util.pre_set(t1)
                pre_t2 = pn_util.pre_set(t2)
                if pre_t1 == pre_t2:
                    post_t1 = pn_util.post_set(t1)
                    post_t2 = pn_util.post_set(t2)
                    if post_t1 == post_t2:
                        t = generate_new_binary_transition(t1, t2, pt_operator.Operator.XOR, net)
                        net.transitions.add(t)
                        for a in t1.in_arcs:
                            pn_util.add_arc_from_to(a.source, t, net)
                        for a in t1.out_arcs:
                            pn_util.add_arc_from_to(t, a.target, net)
                        pn_util.remove_transition(net, t1)
                        pn_util.remove_transition(net, t2)
                        return net
    return None


def binary_sequence_detection(net):
    plcs = copy.copy(net.places)
    for p in plcs:
        if len(p.in_arcs) == 1 and len(p.out_arcs) == 1:
            src = list(p.in_arcs)[0].source
            trgt = list(p.out_arcs)[0].target
            if len(src.out_arcs) == 1 and len(trgt.in_arcs) == 1:
                t = generate_new_binary_transition(src, trgt, pt_operator.Operator.SEQUENCE, net)
                net.transitions.add(t)
                for a in src.in_arcs:
                    pn_util.add_arc_from_to(a.source, t, net)
                for a in trgt.out_arcs:
                    pn_util.add_arc_from_to(t, a.target, net)
                pn_util.remove_transition(net, src)
                pn_util.remove_transition(net, trgt)
                pn_util.remove_place(net, p)
                return net
    return None


def transform_pn_to_pt(net, i_m):
    stop = False
    while not stop:
        stop = True
        petri_viz.view(petri_viz.apply(net, parameters={"format": "svg"}))
        time.sleep(1)
        stop = binary_loop_detection(net) is None
        if not stop:
            continue
        stop = binary_sequence_detection(net) is None
        if not stop:
            continue
        stop = binary_choice_detection(net) is None
        if not stop:
            continue
        stop = binary_parallel_detection(net) is None
        if not stop:
            continue

    if len(net.transitions) == 1:
        pt_str = list(net.transitions)[0].label
        pt = pt_util.parse(pt_str)
        pt_viz.view(pt_viz.apply(pt, parameters={"format": "svg"}))
        time.sleep(1)


if __name__ == "__main__":
    # pnml_path = os.path.join('..', "tests", "input_data", "running-example.pnml")
    # pnml_path = 'C:/Users/zelst/rwth/bas/Documents/tue/svn/private/logs/a12_logs/reference.apnml'
    # pnml_path = 'C:/Users/zelst/rwth/bas/Documents/tue/svn/private/logs/a22_logs/a22f0n00_ref.apnml'
    # pnml_path = 'C:/Users/zelst/rwth/bas/Documents/tue/svn/private/logs/a32_logs/a32f0n00_reference.apnml'
    # pnml_path = 'C:/Users/zelst/rwth/bas/Documents/tue/svn/private/logs/a42_logs/a42f00n00_ref.apnml'
    # pnml_path = 'C:/Users/zelst/Desktop/abcd_acbd_aed.pnml'
    # net, i_m, f_m = pnml_import.apply(pnml_path)

    pt = pt_gen.apply(parameters={'min': 7, 'mode':10, 'max':12})
    pt_viz.view(pt_viz.apply(pt, parameters={"format": "svg"}))
    time.sleep(1)
    net, i_m, f_m = pt_conv.apply(pt)


    transform_pn_to_pt(net, i_m)
