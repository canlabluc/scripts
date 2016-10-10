#!/usr/local/bin/python

""" Feature Selection on Aging Data
Runs Lasso regression on the aging dataset in order to determine
strong predictors of our interest variable.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn import cross_validation
from sklearn.grid_search import GridSearchCV
from sklearn.linear_model import LassoLarsCV

# Nicely prints coefficients of linear models [0].
# [0]: http://blog.datadive.net/selecting-good-features-part-ii-linear-models-and-regularization/
def prettyprint(coefs, names=None, sort=False, n_coefs=20):
    if names == None:
        names = ["X%s" % x for x in range(len(coefs))]
    lst = zip(coefs, names)
    if sort:
        lst = sorted(lst, key = lambda x:-np.abs(x[0]))
    return " + \n".join("%s * %s" % (round(coef, 3), name) for coef, name in lst)

### Data IO, management, and variable selection
aging      = pd.read_csv('../2015-11/lassomodel/data/madb_intclasses_use.csv', header=0).astype(np.float) # Full dataset
superagers = pd.read_csv('../2015-11/lassomodel/data/super-agers.csv', header=0).astype(np.float)         # Only super-agers
mci        = pd.read_csv('../2015-11/lassomodel/data/mcis.csv', header=0).astype(np.float)                # Only MCIs
train_set  = pd.read_csv('../2015-11/lassomodel/data/train_data.csv', header=0).astype(np.float)          # Remaining set from below
test_set   = pd.read_csv('../2015-11/lassomodel/data/test_data.csv', header=0).astype(np.float)           # Small set with mix of all

# Make all keys upper-case
aging.columns      = map(str.upper, aging.columns)
superagers.columns = map(str.upper, superagers.columns)
mci.columns        = map(str.upper, mci.columns)
train_set.columns  = map(str.upper, train_set.columns)
test_set.columns   = map(str.upper, test_set.columns)

interest = 'RAVLT_DEL'

col = list(aging.columns.values)
col.remove('SUBJECT')
col.remove('RAVLT_DEL')

### Construct training sets and their targets.
X_aging, y_aging = aging[col], aging[interest]
X_sa, y_sa       = superagers[col], superagers[interest]
X_mci, y_mci     = mci[col], mci[interest]
X_train, y_train = train_set[col], train_set[interest]
X_test, y_test   = test_set[col], test_set[interest]

score = 'mean_squared_error'
tuned_params_lasso = [{'alpha': np.linspace(-1, 1, 100),
                       'normalize': [True, False]}]

### ACROSS WHOLE DATASET
### With StratifiedKFold, we're stratifying according to the interest variable.
### This ensures that there will be an even proportion of RAVLT_DEL (or whatever
### the interest variable is) values across all folds.
skf = cross_validation.StratifiedKFold(y_aging, n_folds=6)
model = LassoLarsCV(max_iter=100000, cv=skf).fit( X_aging, y_aging )

# print("Best estimator for WHOLE DATASET: \n{0}\n".format(model.best_estimator_))
print("Percent variance explained: {0}".format(model.score( X_aging, y_aging)))
print("Coefficients found: \n{0}\n".format(prettyprint(model.coef_, col, sort=True)))

# plot coefficient progression
m_log_alphas = -np.log10(model.alphas_)
ax = plt.gca()
plt.plot(m_log_alphas, model.coef_path_.T)
plt.axvline(-np.log10(model.alpha_), linestyle='--', color='k',
            label='alpha CV')
plt.ylabel('Regression Coefficients')
plt.xlabel('-log(alpha)')
plt.title('Regression Coefficients Progression for Lasso Paths')

plt.show()

### ACROSS SUPERAGERS
# regr_cv = GridSearchCV(Lasso(max_iter=100000), tuned_params_lasso, cv=7, scoring=score)
# regr_cv.fit( X_sa, y_sa )
# regr = regr_cv.best_estimator_

# print("Best estimator for SUPER-AGERS: \n{0}\n".format(regr_cv.best_estimator_))
# print("Percent variance explained: {0}".format(regr.score( X_sa, y_sa )))
# print("Coefficients found: \n{0}\n".format(prettyprint(regr.coef_, col, sort=True)))

# ### ACROSS MCIs
# regr_cv = GridSearchCV(Lasso(max_iter=100000), tuned_params_lasso, cv=5, scoring=score)
# regr_cv.fit( X_mci, y_mci )
# regr = regr_cv.best_estimator_

# print("Best estimator for MCIs: \n{0}\n".format(regr_cv.best_estimator_))
# print("Percent variance explained: {0}".format(regr.score( X_mci, y_mci )))
# print("Coefficients found: \n{0}\n".format(prettyprint(regr.coef_, col, sort=True)))

### Using a validation set
# skf = cross_validation.StratifiedKFold(y_train, n_folds=4)
# regr_cv = GridSearchCV(Lasso(), tuned_params_lasso, cv=skf, scoring=score)
# regr_cv.fit( X_train, y_train )
# regr = regr_cv.best_estimator_
#
# print("Best estimator for validation set: \n{0}\n".format(regr))
# print(regr.score( X_test, y_test ))
# print("Coefficients foudns: \n{0}\n".format(prettyprint(regr.coef_, col, sort=True)))
