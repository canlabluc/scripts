#!/usr/local/bin/python

""" Feature Selection on Aging Data
Runs Ridge regression on the aging dataset in order to determine
strong predictors of our interest variable.
"""

import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.linear_model import LinearRegression

# Nicely prints coefficients of linear models [0].
# [0]: http://blog.datadive.net/selecting-good-features-part-ii-linear-models-and-regularization/
def prettyprint(coefs, names=None, sort=False, n_coefs=20):
    if names == None:
        names = ["X%s" % x for x in range(len(coefs))]
    lst = zip(coefs, names)
    if sort:
        lst = sorted(lst, key = lambda x:-np.abs(x[0]))
    return " + \n".join("%s * %s" % (round(coef, 3), name) for coef, name in lst)

### Data IO and variable selection
aging      = pd.read_csv('../2015-11/lassomodel/data/madb_intclasses_use.csv', header=0).astype(np.float) # Full dataset
superagers = pd.read_csv('../2015-11/lassomodel/data/super-agers.csv', header=0).astype(np.float)         # Only super-agers
mci        = pd.read_csv('../2015-11/lassomodel/data/mcis.csv', header=0).astype(np.float)                # Only MCIs
train_set  = pd.read_csv('../2015-11/lassomodel/data/train_data.csv', header=0).astype(np.float)          # Remaining set from below
test_set   = pd.read_csv('../2015-11/lassomodel/data/test_data.csv', header=0).astype(np.float)           # Small set with mix of all

interest = 'RAVLT_DEL'
# col = list(aging.columns.values)[38:] # for EEG features only
col = list(aging.columns.values);
# Remove all long-term memory measures, since these will automatically be strong predictors
# if our interest variable is a long-term memory measure such as LM_1 or LM_2
col.remove('Subject')
col.remove('Class')
col.remove('Education')
col.remove('Sex_numberic')
col.remove('LM_2')
col.remove('LM_1') ;
col.remove('RAVLT_DEL')

### Construct training sets and their targets.
X_aging, y_aging = aging[col], aging[interest]
X_sa, y_sa       = superagers[col], superagers[interest]
X_mci, y_mci     = mci[col], mci[interest]
X_train, y_train = train_set[col], train_set[interest]
X_test, y_test   = test_set[col], test_set[interest]

### Model
clf = LinearRegression()
clf.fit( X_sa, y_sa )
# clf.fit( X_mci, y_mci )

# print("Best estimator for SUPER-AGERS: \n{0}\n".format(clf.best_estimator_))
print("Percent variance explained: {0}".format(clf.score( X_sa, y_sa )))
print("Coefficients found: \n{0}\n".format(prettyprint(clf.coef_, col, sort=True)))
