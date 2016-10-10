""" cl_BESAevtparser
Compiles BESA evt Code and Trigger columns
into single event list.

Usage:
    $ python cl_BESAevtparser.py import_path exportpath
    $ # Example:
    $ python cl_BESAevtparser.py /raw-evt-data/ /clean-evt-data/
"""

import os
import sys
import glob
import pandas as pd

import_path = sys.argv[1]
export_path = sys.argv[2]

print(import_path)
print(export_path)

evt_files = []
for root, dirs, files in os.walk(import_path):
    evt_files += glob.glob(os.path.join(root, '*.evt'))

print(evt_files)

for i in range(len(evt_files)):
    df = pd.read_csv(evt_files[i], sep='\t', skiprows=2)
    df.columns = ['Tmu', 'Code', 'TriNo', 'Comment']
    df.TriNo   = list(map(lambda x: int(x), list(df.TriNo)))
    df.Tmu     = round(df.Tmu / 10**6) * 512

    triggers = []
    latencies = []
    for j in range(df.shape[0]):

        event = df.iloc[j, :]

        latency = event.Tmu
        if event.Code == 11:
            trigger = 'BLINK1'
        elif event.Code == 21:
            trigger = 'ARTFCT1'
        elif event.Code == 22:
            trigger = 'ARTFCT2'
        else:
            if event.TriNo == 11:
                trigger = 'FIXATION'
            elif event.TriNo == 21:
                trigger = 'GO_PROMPT'
            elif event.TriNo == 22:
                trigger = 'NOGO_PROMPT'
            elif event.TriNo == 255:
                trigger = 'START'
            elif event.TriNo == 1:
                trigger = 'RESPONSE'
            elif event.TriNo == 32:
                trigger = 'GO_RESPONSE'
            elif event.TriNo == 33:
                trigger = 'NOGO_REPONSE'
            else:
                print('ERROR: {}'.format(event))
                # print(event)
                trigger = event[1]
        triggers.append(trigger)
        latencies.append(latency)
    df_new = pd.DataFrame(data={'Latency': latencies, 'TriNo': triggers})
    print("PRINTING...")
    print("EXPORTPATH: " + evt_files[i][:-4] + '_fixed.evt')
    df_new.to_csv(evt_files[i][:-4] + '_fixed.evt', sep='\t')
