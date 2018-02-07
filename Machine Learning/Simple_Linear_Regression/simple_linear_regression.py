#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 23:09:27 2018

@author: gjxhlan
"""

# Data Preprocessing
# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Importing the dataset
dataset = pd.read_csv('Salary_Data.csv')
year = dataset.iloc[:,:-1].values
salary = dataset.iloc[:,1].values

# Splitting the dataset into the Training set and Test set
from sklearn.model_selection import train_test_split
year_train, year_test, salary_train, salary_test = train_test_split(year, salary, test_size = 1/3, random_state = 0)

# Train the model
# Fitting Simple Linear Regression to the training set
from sklearn.linear_model import LinearRegression
regressor = LinearRegression()
regressor.fit(year_train, salary_train)

# Predicting the test set results
salary_pred = regressor.predict(year_test)

# Visualising the training set results
plt.scatter(year_train, salary_train, c = 'red')
plt.plot(year_train, regressor.predict(year_train), color = 'blue')
plt.title('Salary vs Experience (Training set)')
plt.xlabel('Years of Experience')
plt.ylabel('Salary')
plt.show()

# Visualising the predicting set results
plt.scatter(year_test, salary_test, c = 'red')
plt.plot(year_train, regressor.predict(year_train), color = 'blue')
plt.title('Salary vs Experience (Test set)')
plt.xlabel('Years of Experience')
plt.ylabel('Salary')
plt.show()