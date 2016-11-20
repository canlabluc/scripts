#!/usr/local/bin/python3
""" cl_BESACleanSegments
Takes evt files that have been preprocessed using cl_evtBESAPreprocessor.py and
produces evt files that only mark off clean segments in the recording using the
'C1' and 'C2' codes to mark the beginning and end of clean segments, respectively.

Usage:
    $ ./cl_BESACleanSegments.py importpath exportpath

Inputs:
    importpath: Path to directory containing pre-processed evt files.
    exportpath: Path to directory in which to save clean evt files.

Notes:
    cl_BESACleanSegments takes files that have been preprocessed, and look like:

    >>> df.head()
       Latency  Trigger
    0     17.0  ARTFCT1
    1   1107.0   BLINK1
    2   1918.0   BLINK1
    3   2454.0   BLINK1
    4   2813.0   BLINK1

    And outputs dataframes that look like:

    >>> df.head()
    Latency Trigger
    0  207252.0      C1
    1  210038.0      C2
    2  210243.0      C1
    3  211669.0      C2
    4  211874.0      C1

    To check that files were correctly processed, run the following Python
    script:

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

evt_files = []
for root, dirs, files in os.walk(import_path):
    evt_files += glob.glob(os.path.join(root, '*.evt'))

for i in range(len(evt_files)):
    df = pd.read_csv(evt_files[i], sep='\t')
    df = df[df.Trigger.isin(['BLINK1', 'ARTFCT1', 'ARTFCT2'])]
    # Add end of blinks (400ms after BLINK1):
    blinks = df[df.Trigger.isin(['BLINK1'])]
    for j in range(blinks.shape[0]):
    # 400ms ~ 205 sampling points
    lat  = blinks.iloc[j].Latency + 205
    trig = 'BLINK2'
    df = df.append({'Latency': lat, 'Trigger': trig}, ignore_index=True)
    df = df.sort_values('Latency')
    df = df.set_index(np.arange(0, df.shape[0], 1))

    # We're going to construct a dataframe that only contains event codes
    # marking clean segments of the recording. We start with creating an empty
    # dataframe with columns for Latency and Trigger.
    clean = pd.DataFrame(columns=['Latency', 'Trigger'])

    # Drop all recording data prior to the beginning of trials.
    clean_idx = 0
    for j in range(df.shape[0]):
    if df.iloc[j].Trigger == 'ARTFCT2':
    clean_idx = j
    break
    clean = clean.append({'Latency': df.iloc[clean_idx].Latency,
                         'Trigger': 'C1'}, ignore_index=True)
    df = df.drop(np.arange(0, clean_idx+1, 1))

    # Grab all segments of recording that occur between blinks and artifacts.
    # These segments are added to the clean dataframe.
    for j in range(df.shape[0]):
    if df.iloc[j].Trigger == 'BLINK1':
    clean = clean.append({'Latency': df.iloc[j].Latency,
                          'Trigger': 'C2'}, ignore_index=True)
    clean = clean.append({'Latency': df.iloc[j+1].Latency,
                          'Trigger': 'C1'}, ignore_index=True)
    if df.iloc[j].Trigger == 'ARTFCT1':
    clean = clean.append({'Latency': df.iloc[j].Latency,
                          'Trigger': 'C2'}, ignore_index=True)
    for k in range(j, df.shape[0]):
    if df.iloc[k].Trigger == 'ARTFCT2':
    clean = clean.append({'Latency': df.iloc[k].Latency,
                          'Trigger': 'C1'}, ignore_index=True)
    break

    # Of the clean segments that were grabbed, drop all which are shorter than
    # two seconds.
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
