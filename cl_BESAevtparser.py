""" cl_BESAevtparser
Takes BESA evt files which have been fed through
evtBESAConsolidator.py and produces clean files.

To check that files were correctly processed:
for i in range(len(evt_files)):
    df = pd.read_csv(evt_files[0], sep='\t')
    bad = 0
    for j in range(df.shape[0]):
        if df.iloc[j].Trigger == 'C1':
            bad += 1
        if df.iloc[j].Trigger == 'C2':
            bad -= 1
    if bad != 0:
        print("BAD FILE: {}".format(evt_files[0].split('/')[-1]))
"""

import glob
import os
import sys

import numpy as np
import pandas as pd

import_path = sys.argv[1]
export_path = sys.argv[2]
clean_only  = bool(sys.argv[3])

evt_files = []
for root, dirs, files in os.walk(import_path):
    evt_files += glob.glob(os.path.join(root, '*.evt'))

for i in range(len(evt_files)):
    df = pd.read_csv(evt_files[i], sep='\t')

    if clean_only == True:
        df = df[df.Trigger.isin(['BLINK1', 'ARTFCT1', 'ARTFCT2'])]
        # Add end of blinks:
        blinks = df[df.Trigger.isin(['BLINK1'])]
        for j in range(blinks.shape[0]):
            # 205 sampling points ~ 400 ms
            lat  = blinks.iloc[j].Latency + 205
            trig = 'BLINK2'
            df = df.append({'Latency': lat, 'Trigger': trig}, ignore_index=True)

        # Now we compute the spaces between. To do this, we simply start with adding
        # the first 'clean' marker at the beginning of the end of the first artifact window.
        df = df.sort_values('Latency')
        df = df.set_index(np.arange(0, df.shape[0], 1))
        clean = pd.DataFrame(columns=['Latency', 'Trigger'])

        # First, drop the first part.
        clean_idx = 0
        for j in range(df.shape[0]):
            if df.iloc[j].Trigger == 'ARTFCT2':
                clean_idx = j
                break

        clean = clean.append({'Latency': df.iloc[clean_idx].Latency, 'Trigger': 'C1'}, ignore_index=True)
        df = df.drop(np.arange(0, clean_idx+1, 1))

        # Add spaces between blinks and artifact
        for j in range(df.shape[0]):
            if df.iloc[j].Trigger == 'BLINK1':
                clean = clean.append({'Latency': df.iloc[j].Latency, 'Trigger': 'C2'}, ignore_index=True)
                clean = clean.append({'Latency': df.iloc[j+1].Latency, 'Trigger': 'C1'}, ignore_index=True)
            if df.iloc[j].Trigger == 'ARTFCT1':
                clean = clean.append({'Latency': df.iloc[j].Latency, 'Trigger': 'C2'}, ignore_index=True)
                for k in range(j, df.shape[0]):
                    if df.iloc[k].Trigger == 'ARTFCT2':
                        clean = clean.append({'Latency': df.iloc[k].Latency, 'Trigger': 'C1'}, ignore_index=True)
                        break

        # Get rid of spaces that are less than 2 seconds long
        bad_idx = []
        for j in range(clean.shape[0] - 1):
            if (clean.iloc[j].Trigger == 'C1' and clean.iloc[j+1].Trigger == 'C2') and\
               (clean.iloc[j+1].Latency - clean.iloc[j].Latency < 1024):
               bad_idx.append(j); bad_idx.append(j+1)

        clean = clean.drop(bad_idx)
        clean = clean.set_index(np.arange(0, clean.shape[0], 1))

        if clean.iloc[-1].Trigger == 'C1':
            clean = clean.drop(clean.shape[0] - 1)

    subj_name = evt_files[i].split('/')[-1][:-4]
    clean.to_csv(export_path + '/' + subj_name + '.evt', sep='\t', index=False)
