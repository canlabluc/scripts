""" evtBESAConsolidator
Compiles BESA evt Code and Trigger columns
into single event list.

Usage:
    $ python cl_BESAevtparser.py import_path exportpath end_blinks
    $ # Example:
    $ python cl_BESAevtparser.py /raw-evt-data/ /clean-evt-data/ true
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

for i in range(len(evt_files)):
    df = pd.read_csv(evt_files[i], sep='\t')
    df.columns = ['Tmu', 'Code', 'Trigger', 'Comment']
    df.Trigger   = list(map(lambda x: int(x) if len(x) < 3 and x != '-' else -1, list(df.Trigger)))
    df['Latency'] = round((df.Tmu / 10**6) * 512)

    print(df.head())

    triggers = []
    latencies = []
    for j in range(df.shape[0]):

        # Grab current event and event latency
        event = df.iloc[j, :]
        latency = event.Latency

        # CHECK BESA CODES
        if event.Code == 41:
            trigger = 'INVALID'
        elif event.Code == 11:
            trigger = 'BLINK1'
        elif event.Code == 21:
            trigger = 'ARTFCT1'
        elif event.Code == 22:
            trigger = 'ARTFCT2'
        else:
            # CHECK TRIGGERS
            if event.Trigger == 11:
                trigger = 'FIXATION'
            elif event.Trigger == 21:
                trigger = 'GO_PROMPT'
            elif event.Trigger == 22:
                trigger = 'NOGO_PROMPT'
            elif event.Trigger == 255:
                trigger = 'START'
            elif event.Trigger == 1:
                trigger = 'RESPONSE' # Passed when subject responds or at end of 900s if no response
            elif event.Trigger == 32:
                trigger = 'INCORRECT_RESPONSE'
            elif event.Trigger == 33:
                trigger = 'NO_RESPONSE'
            else:
                print('ERROR {}: \n\tLatency: {}\n\tCode: {}\n\tTrigger: {}\n\tComment: {}'.format(\
                      evt_files[i].split('/')[-1], event.Latency, event.Code, event.Trigger, event.Comment))
                trigger = event[1]
        if trigger != 'INVALID':
            triggers.append(trigger)
            latencies.append(latency)
    df_new = pd.DataFrame(data={'Latency': latencies, 'Trigger': triggers})
    subj_name = evt_files[i].split('/')[-1][:-4]
    print("PRINTING...")
    print("EXPORTPATH: " + export_path + subj_name + '.evt')
    df_new.to_csv(export_path + '/' + subj_name + '.evt', sep='\t', index=False)
