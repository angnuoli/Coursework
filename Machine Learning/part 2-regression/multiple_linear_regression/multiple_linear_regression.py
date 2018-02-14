#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: gjxhlan
"""

# Multiple linear regression

# Data Preprocessing
# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Importing the dataset
dataset = pd.read_csv('50_Startups.csv')
X = dataset.iloc[:,:-1].values
y = dataset.iloc[:,-1].values

# Encoding categorical data
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
labelencoder_X = LabelEncoder()
X[:, 3] = labelencoder_X.fit_transform(X[:, 3])
onehotencoder = OneHotEncoder(categorical_features = [3])
X = onehotencoder.fit_transform(X).toarray()

# Avoiding the Dummy Variable Trap
X = X[:, 1:]

# Splitting the dataset into the Training set and Test set
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)

# Fitting Multiple Linear Regression to the training set
from sklearn.linear_model import LinearRegression
regressor = LinearRegression()
regressor.fit(X_train, y_train)

# Predicting the test set result
y_pred = regressor.predict(X_test)

# Building the optimal model using Backward Elimination
import statsmodels.formula.api as sm
def backwardElimination(x, s1):
  numVars = len(x[0])
  for i in range(0, numVars):
    regressor_OLS = sm.OLS(y,x).fit()
    maxVar = max(regressor_OLS.pvalues).astype(float)
    if maxVar > s1:
      for j in range(0, len(regressor_OLS.pvalues)):
        if (regressor_OLS.pvalues[j] == maxVar):
          np.delete(x, j, 1)
  regressor_OLS.summary()
  return x

X = np.append(np.ones((50, 1)).astype(int), X, 1)
X_opt = X[:, [0,1,2,3,4,5]]
SL = 0.05
X = backwardElimination(X_opt, SL)

# =============================================================================
# regressor_OLS = sm.OLS(endog = y, exog = X_opt).fit()
# regressor_OLS.summary()
# X_opt = X[:, [0,1,3,4,5]]
# regressor_OLS = sm.OLS(endog = y, exog = X_opt).fit()
# regressor_OLS.summary()
# X_opt = X[:, [0,3,4,5]]
# regressor_OLS = sm.OLS(endog = y, exog = X_opt).fit()
# regressor_OLS.summary()
# X_opt = X[:, [0,3,5]]
# regressor_OLS = sm.OLS(endog = y, exog = X_opt).fit()
# regressor_OLS.summary()
# X_opt = X[:, [0,5]]
# regressor_OLS = sm.OLS(endog = y, exog = X_opt).fit()
# regressor_OLS.summary()
# =============================================================================
