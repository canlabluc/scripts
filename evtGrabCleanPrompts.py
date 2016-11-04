import glob
import os
import sys

import numpy as np
import pandas as pd

# 1. Grab all prompt-related data -- prompts and responses
# 2. Filter out responses which are incorrect:
#       - GO_PROMPT -> RESPONSE -> NO_RESPONSE
#       - NOGO_PROMPT -> RESPONSE -> INCORRECT_RESPONSE
# 3. Filter out prompts/responses which do not have 600 ms of open
#    space post-stimulus.

importpath_conso = sys.argv[1]
importpath_clean = sys.argv[2]
exportpath       = sys.argv[3]

evt_files = []
for root, dirs, files in os.walk(importpath_conso):
    evt_files += glob.glob(os.path.join(root, '*.evt'))

for i in range(len(evt_files)):
    subj_name = evt_files[i].split('/')[-1][:-4]
    df      = pd.read_csv(importpath_conso + subj_name + '.evt', sep='\t')
    cleandf = pd.read_csv(importpath_clean + subj_name + '.evt', sep='\t')
    df = df[df.Trigger.isin(['GO_PROMPT', 'NOGO_PROMPT', 'RESPONSE', \
                             'INCORRECT_RESPONSE', 'NO_RESPONSE'])]
    df = df.set_index(np.arange(0, df.shape[0], 1))

    # Filter out incorrect responses
    bad_idx = []
    for i in range(df.shape[0] - 3):
        if df.iloc[i].Trigger == 'GO_PROMPT' and (df.iloc[i+2].Trigger == 'NO_RESPONSE' or
                                                  df.iloc[i+2].Trigger == 'INCORRECT_RESPONSE'):
            bad_idx.append(i); bad_idx.append(i+1); bad_idx.append(i+2)
        if df.iloc[i].Trigger == 'NOGO_PROMPT' and df.iloc[i+2].Trigger == 'INCORRECT_RESPONSE':
            bad_idx.append(i); bad_idx.append(i+1); bad_idx.append(i+2)
    df = df.drop(df.index[bad_idx])
    df = df.set_index(np.arange(0, df.shape[0], 1))

    # Filter out prompts/responses which are not contained in clean segments
    bad_idx = []
    for i in range(df.shape[0] - 3):
        if df.iloc[i].Trigger == 'GO_PROMPT' or df.iloc[i].Trigger == 'NOGO_PROMPT':
            # 1. Check that it's inside of a clean segment
            latency = df.iloc[i].Latency
            if not cleandf[cleandf.Latency < latency].tail(1).Trigger.all() == 'C1':
                bad_idx.append(i); bad_idx.append(i+1)
    df = df.drop(df.index[bad_idx])
    df = df.set_index(np.arange(0, df.shape[0], 1))

    # Filter out prompts/responses which do not have 600ms of post-stimulus clean space
    bad_idx = []
    for i in range(df.shape[0] - 3):
        if df.iloc[i].Trigger == 'GO_PROMPT' or df.iloc[i].Trigger == 'NOGO_PROMPT':
            latency = df.iloc[i].Latency
            end_clean_seg = cleandf[cleandf.Latency > latency].iloc[0].Latency
            if not end_clean_seg - latency < 308: # 0.6s * 512 = 307.2 points
                bad_idx.append(i); bad_idx.append(i+1)
    df = df.drop(df.index[bad_idx])
    df = df.set_index(np.arange(0, df.shape[0], 1))

    df.to_csv(exportpath + '/' + subj_name + '.evt', sep='\t', index=False)
