""" Feature Selection on Aging Data
Runs Lasso regression on the aging dataset in order to determine
strong predictors of our interest variable.
"""

#!/usr/local/bin/python
import numpy as np
import pandas as pd
import csv as csv
from sklearn import metrics
from sklearn import cross_validation
from sklearn.grid_search import GridSearchCV
from sklearn.linear_model import Lasso

# Nicely prints coefficients of linear models [0]
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
col = list(aging.columns.values)
col.remove('Subject')
col.remove('Class')
col.remove('Education')
col.remove('Sex_numberic')
col.remove(interest)

X_aging, y_aging = aging[col], aging[interest]
X_sa, y_sa       = superagers[col], superagers[interest]
X_mci, y_mci     = mci[col], mci[interest]
X_train, y_train = train_set[col], train_set[interest]
X_test, y_test   = test_set[col], test_set[interest]

### Stratify according to interest variable.
score = 'mean_squared_error'
tuned_params_lasso = [{'alpha': np.linspace(-1, 1, 100),
                       'normalize': [True, False]}]

### ACROSS WHOLE DATASET
skf = cross_validation.StratifiedKFold(y_aging, n_folds=6)
regr_cv = GridSearchCV(Lasso(max_iter=100000), tuned_params_lasso, cv=skf)
regr_cv.fit( X_aging, y_aging )
regr = regr_cv.best_estimator_

print("Best estimator for WHOLE DATASET: \n{0}\n".format(regr_cv.best_estimator_))
print("Percent variance explained: {0}".format(regr.score( X_aging, y_aging)))
print("Coefficients found: \n{0}\n".format(prettyprint(regr.coef_, col, sort=True)))

### ACROSS SUPERAGERS
regr_cv = GridSearchCV(Lasso(max_iter=100000), tuned_params_lasso, cv=7, scoring=score)
regr_cv.fit( X_sa, y_sa )
regr = regr_cv.best_estimator_

print("Best estimator for SUPER-AGERS: \n{0}\n".format(regr_cv.best_estimator_))
print("Percent variance explained: {0}".format(regr.score( X_sa, y_sa )))
print("Coefficients found: \n{0}\n".format(prettyprint(regr.coef_, col, sort=True)))

### ACROSS MCIs
regr_cv = GridSearchCV(Lasso(max_iter=100000), tuned_params_lasso, cv=5, scoring=score)
regr_cv.fit( X_mci, y_mci )
regr = regr_cv.best_estimator_

print("Best estimator for MCIs: \n{0}\n".format(regr_cv.best_estimator_))
print("Percentage variance explained: {0}".format(regr.score( X_mci, y_mci )))
print("Coefficients found: \n{0}\n".format(prettyprint(regr.coef_, col, sort=True)))

# ### Using a validation set
# skf = cross_validation.StratifiedKFold(y_train, n_folds=4)
# regr_cv = GridSearchCV(Lasso(max_iter=100000), tuned_params_lasso, cv=skf, scoring=score)
# regr_cv.fit( X_train, y_train )
# regr = regr_cv.best_estimator_

# print("Best estimator for validation set: \n{0}\n".format(regr))
# print(regr.score( X_test, y_test ))
# print("Coefficients foudns: \n{0}\n".format(prettyprint(regr.coef_, col, sort=True)))
