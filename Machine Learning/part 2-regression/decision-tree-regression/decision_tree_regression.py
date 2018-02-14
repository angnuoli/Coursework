#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: gjxhlan
"""
# Regression template
# 1. Data Preprocessing

# Import the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Importing the dataset
dataset = pd.read_csv('Position_Salaries.csv')
X = dataset.iloc[:,1:2].values # try to make X as matrix, y as vector
y = dataset.iloc[:,2].values

# Fitting the Decision Tree Regression to the dataset
from sklearn.tree import DecisionTreeRegressor
regressor = DecisionTreeRegressor(random_state = 0)
regressor.fit(X, y)

# Predicting a new result
y_pred = regressor.predict(6.5)

# 3. Visualising the dataset results (for higher resolution and smoother curve)
X_grid = np.arange(min(X), max(X), 0.1)
X_grid = X_grid.reshape((len(X_grid), 1))
plt.scatter(X, y, c='red')
plt.plot(X, regressor.predict(X), color = 'blue')
plt.title('Salary vs Level (Decision Tree Regression)')
plt.xlabel('Level')
plt.ylabel('Salary')
plt.show()

plt.scatter(X, y, c='red')
plt.plot(X_grid, regressor.predict(X_grid), color = 'blue')
plt.title('Salary vs Level (Decision Tree Regression)')
plt.xlabel('Level')
plt.ylabel('Salary')
plt.show()