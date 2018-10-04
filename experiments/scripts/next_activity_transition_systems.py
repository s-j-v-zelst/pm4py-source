import re, codecs, random, math, textwrap
from collections import defaultdict, deque, Counter
import operator
from sys import argv
from os import listdir
from os.path import join
import pm4py



if __name__ == "__main__":

    # for reproducibility
    random.seed(22)

    logs_path = "C:/Users/zelst/github/taxxer/rnnalpha/data"
    for log_file in listdir(logs_path):
        if log_file.endswith('.xes.gz'):
            print(log_file)
            log = pm4py.entities.log.importer.xes.factory.apply(join(logs_path,log_file))
            for i in range(3):
                print('before shuffle',  log[0])
                random.shuffle(log)
                print('after shuffle', log[0])
            print(len(log))


