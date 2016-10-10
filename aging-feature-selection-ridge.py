#!/usr/local/bin/python

""" Feature Selection on Aging Data
Runs Ridge regression on the aging dataset in order to determine
strong predictors of our interest variable.
"""

import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn import cross_validation
from sklearn.grid_search import GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso
from sklearn.linear_model import Ridge
from sklearn.linear_model import RidgeCV

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

col = col[:30] # Remove all EEG features

### Construct training sets and their targets.
X_aging, y_aging = aging[col], aging[interest]
X_sa, y_sa       = superagers[col], superagers[interest]
X_mci, y_mci     = mci[col], mci[interest]
X_train, y_train = train_set[col], train_set[interest]
X_test, y_test   = test_set[col], test_set[interest]

score = 'mean_squared_error'
alpha_params = np.linspace(-10, 10, 100)
tuned_params_ridge = [{'alpha': np.linspace(-1, 1, 100),
                     }]


### ACROSS WHOLE DATASET
### With StratifiedKFold, we're stratifying according to the interest variable.
### This ensures that there will be an even proportion of RAVLT_DEL (or whatever
### the interest variable is) values across all folds.
skf = cross_validation.StratifiedKFold(y_aging, n_folds=6)
ridge_cv = GridSearchCV(Ridge(max_iter=100000), tuned_params_ridge, cv=skf)
ridge_cv.fit( X_aging, y_aging )
ridge = ridge_cv.best_estimator_

print("WHOLE DATASET //////////////////////////")
# ridge = RidgeCV(alphas=alpha_params, cv=7, scoring=score)
# ridge.fit( X_aging, y_aging )
ols = LinearRegression()
ols.fit( X_aging, y_aging )
print("RIDGE REGRESSION")
print(ridge)
print("Percent variance explained: {0}".format(ridge.score( X_aging, y_aging )))
print("Coefficients found: \n{0}\n".format(prettyprint(ridge.coef_, col, sort=True)))
print("ORDINARY LEAST SQUARES")
print(ols)
print("Percent variance explained: {0}".format(ols.score( X_aging, y_aging )))
print("Coefficients found: \n{0}\n".format(prettyprint(ols.coef_, col, sort=True)))
print("WHOLE DATASET //////////////////////////")

print("SUPER AGERS //////////////////////////")
ridge = RidgeCV(alphas=alpha_params, cv=7, scoring=score)
ridge.fit( X_sa, y_sa )
ols = LinearRegression()
ols.fit( X_sa, y_sa )
print("RIDGE REGRESSION")
print("Percent variance explained: {0}".format(ridge.score( X_sa, y_sa )))
print("Coefficients found: \n{0}\n".format(prettyprint(ridge.coef_, col, sort=True)))
print("ORDINARY LEAST SQUARES")
print("Percent variance explained: {0}".format(ols.score( X_sa, y_sa )))
print("Coefficients found: \n{0}\n".format(prettyprint(ols.coef_, col, sort=True)))
print("SUPER AGERS //////////////////////////")

print("MCIS //////////////////////////")
ridge = RidgeCV(alphas=alpha_params, cv=7, scoring=score)
ridge.fit( X_mci, y_mci )
ols = LinearRegression()
ols.fit( X_mci, y_mci )
print("RIDGE REGRESSION")
print("Percent variance explained: {0}".format(ridge.score( X_mci, y_mci )))
print("Coefficients found: \n{0}\n".format(prettyprint(ridge.coef_, col, sort=True)))
print("ORDINARY LEAST SQUARES")
print("Percent variance explained: {0}".format(ols.score( X_mci, y_mci )))
print("Coefficients found: \n{0}\n".format(prettyprint(ols.coef_, col, sort=True)))
print("MCIS //////////////////////////")

### Using a validation set
# skf = cross_validation.StratifiedKFold(y_train, n_folds=4)
# regr_cv = GridSearchCV(Lasso(), tuned_params_ridge, cv=skf, scoring=score)
# regr_cv.fit( X_train, y_train )
# regr = regr_cv.best_estimator_
#
# print("Best estimator for validation set: \n{0}\n".format(regr))
# print(regr.score( X_test, y_test ))
# print("Coefficients foudns: \n{0}\n".format(prettyprint(regr.coef_, col, sort=True)))
