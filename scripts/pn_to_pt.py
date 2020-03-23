import copy
import time
import datetime
import os

from pm4py.objects.petri import petrinet
from pm4py.objects.petri import utils as pn_util
from pm4py.objects.petri.importer import factory as pnml_import
from pm4py.objects.process_tree import pt_operator
from pm4py.objects.process_tree import util as pt_util
from pm4py.visualization.petrinet import factory as pn_viz
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


def check_singleton_pre_set(elems):
    for x in elems:
        if len(pn_util.pre_set(x)) > 1 or len(pn_util.pre_set(x)) == 0:
            return False
    return True


def check_singleton_post_set(elems):
    for x in elems:
        if len(pn_util.post_set(x)) > 1 or len(pn_util.post_set(x)) == 0:
            return False
    return True


def binary_loop_detection(net):
    trans_set_1 = copy.copy(net.transitions)
    trans_set_2 = copy.copy(net.transitions)
    for t1 in trans_set_1:
        for t2 in trans_set_2:
            if t1 != t2:
                pre_t1 = pn_util.pre_set(t1)
                if not check_singleton_post_set(pre_t1):
                    continue
                post_t1 = pn_util.post_set(t1)
                if not check_singleton_pre_set(post_t1):
                    continue
                pre_t2 = pn_util.pre_set(t2)
                inter1 = pre_t2 & post_t1
                if len(inter1) < len(pre_t2) or len(inter1) < len(post_t1):
                    continue
                post_t2 = pn_util.post_set(t2)
                inter2 = post_t2 & pre_t1
                if len(inter2) < len(post_t2) or len(inter2) < len(pre_t1):
                    continue
                # pattern was found
                t = generate_new_binary_transition(t1, t2, pt_operator.Operator.LOOP, net)
                net.transitions.add(t)
                # reduce
                for a in t1.in_arcs:
                    pn_util.add_arc_from_to(a.source, t, net)
                for a in t1.out_arcs:
                    pn_util.add_arc_from_to(t, a.target, net)
                pn_util.remove_transition(net, t1)
                pn_util.remove_transition(net, t2)
                return net
    return None


def check_pre_sets_equal(elems):
    for x in elems:
        for y in pn_util.pre_set(x):
            for xx in elems:
                if y not in pn_util.pre_set(xx):
                    return False
    return True


def check_post_sets_equal(elems):
    for x in elems:
        for y in pn_util.post_set(x):
            for xx in elems:
                if y not in pn_util.post_set(xx):
                    return False
    return True


def binary_parallel_detection(net):
    trans_set_1 = copy.copy(net.transitions)
    trans_set_2 = copy.copy(net.transitions)
    for t1 in trans_set_1:
        for t2 in trans_set_2:
            if t1 != t2:
                pre_t1 = pn_util.pre_set(t1)
                if not check_singleton_post_set(pre_t1):
                    continue
                post_t1 = pn_util.post_set(t1)
                if not check_singleton_pre_set(post_t1):
                    continue
                pre_t2 = pn_util.pre_set(t2)
                if not check_singleton_post_set(pre_t2):
                    continue
                post_t2 = pn_util.post_set(t2)
                if not check_singleton_pre_set(post_t2):
                    continue
                if not check_pre_sets_equal(pre_t1 | pre_t2):
                    continue
                if not check_post_sets_equal(post_t1 | post_t2):
                    continue
                # pattern was found
                t = generate_new_binary_transition(t1, t2, pt_operator.Operator.PARALLEL, net)
                net.transitions.add(t)
                # reduce
                for a in t1.in_arcs:
                    pn_util.add_arc_from_to(a.source, t, net)
                for a in t1.out_arcs:
                    pn_util.add_arc_from_to(t, a.target, net)
                for a in t2.in_arcs:
                    pn_util.add_arc_from_to(a.source, t, net)
                for a in t2.out_arcs:
                    pn_util.add_arc_from_to(t, a.target, net)
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
    trans_set_1 = copy.copy(net.transitions)
    trans_set_2 = copy.copy(net.transitions)
    for t1 in trans_set_1:
        for t2 in trans_set_2:
            if t1 != t2:
                post_t1 = pn_util.post_set(t1)
                pre_t2 = pn_util.pre_set(t2)
                if post_t1 != pre_t2:
                    continue
                if not (check_singleton_pre_set(post_t1) and check_singleton_post_set(post_t1)):
                    continue
                t = generate_new_binary_transition(t1, t2, pt_operator.Operator.SEQUENCE, net)
                net.transitions.add(t)
                for a in t1.in_arcs:
                    pn_util.add_arc_from_to(a.source, t, net)
                for a in t2.out_arcs:
                    pn_util.add_arc_from_to(t, a.target, net)
                for p in post_t1:
                    pn_util.remove_place(net, p)
                pn_util.remove_transition(net, t1)
                pn_util.remove_transition(net, t2)
                return net
    return None


def transform_pn_to_pt(net):
    stop = False
    while not stop:
        stop = True
        # pn_viz.view(pn_viz.apply(net, parameters={"format": "svg"}))
        # time.sleep(1)
        stop = binary_choice_detection(net) is None
        if not stop:
            continue
        stop = binary_sequence_detection(net) is None
        if not stop:
            continue
        stop = binary_parallel_detection(net) is None
        if not stop:
            continue
        stop = binary_loop_detection(net) is None
        if not stop:
            continue

    if len(net.transitions) == 1:
        pt_str = list(net.transitions)[0].label
        pt = pt_util.parse(pt_str)
        return pt


if __name__ == "__main__":
    i = 1
    f = open('C:/Users/zelst/Documents/papers/2020_van_zelst_pn_pt_algo/experiments/tria_40_50_60_bordered_2.csv',
             'w+')
    f.write('run, places, transitions, time_ms, rediscovered\n')
    while i <= 50000:
        pt = pt_util.fold(pt_gen.apply(parameters={'min': 40, 'mode': 50, 'max': 60}))
        net, i_m, f_m = pt_conv.apply(pt, variant=pt_conv.TO_PETRI_NET_TRANSITION_BORDERED)
        plcs = len(net.places)
        trs = len(net.transitions)
        start = datetime.datetime.now()
        ptx = transform_pn_to_pt(net)
        end = datetime.datetime.now()
        ptx = pt_util.fold(ptx)
        elapsed = end - start
        if elapsed.seconds > 0:
            print(str(i)+': more than one sec!')
        if pt_util.structurally_language_equal(pt, ptx):
            el = elapsed.seconds * 1000000 + elapsed.microseconds
            f.write(str(i) + ', ' + str(plcs) + ', ' + str(trs) + ', ' + str(
                el) + ', ' + 'T' + '\n')
            # print(i)
        else:
            #f.write(str(i) + ', ' + str(plcs) + ', ' + str(trs) + ', ' + str(
            #    elapsed.microseconds) + ', ' + 'F' + '\n')
            print('error')
            pt_viz.view(pt_viz.apply(pt, parameters={"format": "svg"}))
            pt_util.fold(pt)
            time.sleep(1)
            pt_viz.view(pt_viz.apply(ptx, parameters={"format": "svg"}))
            break
        i += 1

    '''
    pnml_path = os.path.join('..', "tests", "input_data", "running-example-book-simple.pnml")
    # pnml_path = 'C:/Users/zelst/rwth/bas/Documents/tue/svn/private/logs/a12_logs/reference.apnml'
    # pnml_path = 'C:/Users/zelst/rwth/bas/Documents/tue/svn/private/logs/a22_logs/a22f0n00_ref.apnml'
    # pnml_path = 'C:/Users/zelst/rwth/bas/Documents/tue/svn/private/logs/a32_logs/a32f0n00_reference.apnml'
    # pnml_path = 'C:/Users/zelst/rwth/bas/Documents/tue/svn/private/logs/a42_logs/a42f00n00_ref.apnml'
    # pnml_path = 'C:/Users/zelst/Desktop/abcd_acbd_aed.pnml'
    # pnml_path = 'C:/Users/zelst/Desktop/running-example.pnml'
    net, i_m, f_m = pnml_import.apply(pnml_path)

    #pt = pt_gen.apply(parameters={'min': 250, 'mode':350, 'max':450})
    # pt = pt_gen.apply()
    # pt_str = '->(\'a\',*(\'a\',\'b\'),\'c\')'
    # pt = pt_util.parse(pt_str)
    # pt_viz.view(pt_viz.apply(pt, parameters={"format": "svg"}))
    # time.sleep(1)
    # pt = pt_util.fold(pt)
    # pt_viz.view(pt_viz.apply(pt, parameters={"format": "svg"}))
    # time.sleep(1)
    # net, i_m, f_m = pt_conv.apply(pt)
    # pn_viz.view(pn_viz.apply(net, parameters={"format": "svg"}))
    # time.sleep(1)
    ptx = transform_pn_to_pt(net)
    pt_viz.view(pt_viz.apply(ptx, parameters={"format": "svg"}))
    time.sleep(1)
    ptx = pt_util.reduce_tau_leafs(ptx)
    pt_viz.view(pt_viz.apply(ptx, parameters={"format": "svg"}))
    time.sleep(1)
    ptx = pt_util.fold(ptx)
    pt_viz.view(pt_viz.apply(ptx, parameters={"format": "svg"}))
    # print(pt == ptx)
    '''
