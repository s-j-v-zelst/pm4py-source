from scripts import pn_to_pt as transform
import pandas as pd
import os
from pm4py.objects.petri.importer import factory as pn_im
import copy
from pm4py.visualization.petrinet import factory as pn_viz
from pm4py.objects.process_tree import util as pt_util
from pm4py.visualization.process_tree import factory as pt_viz

MODELS = 'C:/Users/zelst/Documents/papers/2020_van_zelst_pn_pt_algo/experiments/model_collection/experiment/models/'
SOUNDNESS_INFO = 'C:/Users/zelst/Documents/papers/2020_van_zelst_pn_pt_algo/experiments/model_collection/experiment/soundness.csv'
RESULTS_FOLDER = 'C:/Users/zelst/Documents/papers/2020_van_zelst_pn_pt_algo/experiments/model_collection/experiment/results_1'

soundness = pd.read_csv(SOUNDNESS_INFO, sep=';')

directory = os.fsencode(MODELS)
i = 0
s = 0
ns = 0
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith('.pnml'):
        row = soundness[soundness['process'] == os.path.splitext(filename)[0]]
        if len(row) > 0:
            print(filename)
            net, im, fm = pn_im.apply(MODELS + filename)
            pn_viz.view(pn_viz.apply(net, im, fm, parameters={"format": "svg"}))
            ptwf = transform.transform_pn_to_pt(copy.deepcopy(net))
            if len(ptwf.transitions) == 1:
                pt_str = list(net.transitions)[0].label
                pt = pt_util.parse(pt_str)
                pt_viz.view(pt_viz.apply(pt, parameters={"format": "svg"}))
                if row['is_Sound'].values[0] == 'YES':
                    print('TP')
                else:
                    print('FP')
            else:
                pn_viz.view(pn_viz.apply(ptwf, parameters={"format": "svg"}))
                if row['is_Sound'].values[0] == 'NO':
                    print('TN')
                else:
                    print('FN')

            print(str(len(net.places)))
            print(row['P_red'].values[0])

            # print(filename)
            # print(os.path.splitext(filename)[0])
            # print(row)
            i += 1
            # print(str(row['is_Sound'].values[0]))
            if row['is_Sound'].values[0] == 'YES':
                s += 1
            elif row['is_Sound'].values[0] == 'NO':
                ns += 1

print(i)
print(s)
print(ns)
