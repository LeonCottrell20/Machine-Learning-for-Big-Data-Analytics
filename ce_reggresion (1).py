# -*- coding: utf-8 -*-
"""CE reggresion.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qjtZvP0zVV7yZtFklKoX6kaQZQEVnTfm
"""

import os
import numpy as np
import pandas as pd
import sklearn
import matplotlib.pylab as plt
import seaborn as sns
from scipy.stats import norm
from scipy.integrate import quad
from scipy.spatial import distance

from google.colab import files
uploaded = files.upload()

data =  pd.read_csv('concrete.csv')
data_original = data.copy()

data.head()

data.describe()

"""Below shows how to view the cardinality and dimensionality size of the data"""

data.shape

# number 0 represent the rows and 1 is for columns
print('data has a cardinality size {}'.format(data.shape[0]) + 
      ' and dimensionality size {}'.format(data.shape[1]))

"""Checking the columns have the correct classification of data type. """

data.info()

"""## Data Cleaning
Before starting, we need to check the data for any missing values and outliers.
"""

data.isna().sum()

"""## As you can see, there is no NAN (not a number) in the columns.

"""

strength_max = data.strength.max()
strength_min = data.strength.min()
print("max:",strength_max)
print("min:",strength_min)

"""## Outliers
Using histograms and boxplots we can identify any ouliers in the data set.
"""

f, axes = plt.subplots(1, 2, figsize=(23, 6), sharex=True)
sns.distplot(data['slag'], ax = axes[0])
sns.boxplot(data['slag'], ax = axes[1])

"""As we can see, the values above 350 in the slag are outliers. To clean the data we should remove all records of data past this point.



"""

data[data['slag'] > 350]

"""Removing all entries that are above 350.

"""

data = data.drop(data[data['slag'] > 350].index)

f, axes = plt.subplots(1, 2, figsize=(23, 6), sharex=True)
sns.distplot(data['slag'], ax = axes[0])
sns.boxplot(data['slag'], ax = axes[1])

"""And now the outliers in water"""

f, axes = plt.subplots(1, 2, figsize=(23, 6), sharex=True)
sns.distplot(data['water'], ax = axes[0])
sns.boxplot(data['water'], ax = axes[1])

"""Here the outliers are before 122 and after 230."""

data[(data['water'] < 122) | (data['water'] > 230)]

"""So once again, we drop those values from the column."""

data = data.drop(data[(data['water'] < 122) | (data['water'] > 230)].index)

"""Further examples of cleaning; superplastic."""

f, axes = plt.subplots(1, 2, figsize=(23, 6), sharex=True)
sns.distplot(data['superplastic'], ax = axes[0])
sns.boxplot(data['superplastic'], ax = axes[1])

data = data.drop(data[data['superplastic'] > 25].index)
data[data['superplastic'] > 25]

"""cleaning fineagg"""

f, axes = plt.subplots(1, 2, figsize=(23, 6), sharex=True)
sns.distplot(data['fineagg'], ax = axes[0])
sns.boxplot(data['fineagg'], ax = axes[1])

data[(data['fineagg'] < 600) | (data['fineagg'] > 950)]

data = data.drop(data[(data['fineagg'] < 600) | (data['fineagg'] > 950)].index)

"""Cleaning age"""

f, axes = plt.subplots(1, 2, figsize=(23, 6), sharex=True)
sns.distplot(data['age'], ax = axes[0])
sns.boxplot(data['age'], ax = axes[1])

data[data['age'] > 150]

data = data.drop(data[data['age'] > 150].index)

"""## Heatmaps
Heatmaps can also be created. These help with visualizing patterns, and potential corralations within the data set.
https://seaborn.pydata.org/generated/seaborn.heatmap.html
"""

plt.figure(figsize=(23,5))
sns.heatmap(data=data.corr(), annot=True);

corr = data.corr()
corr.style.background_gradient(cmap='coolwarm')

"""## PCA"""

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# initializing standard scaler, to be used for data scaling
scaler = StandardScaler()

drop_data = data.copy()
output_data = drop_data.loc[:, ['strength']]
drop_data = drop_data.drop(columns=['strength'])

# Scaling PCA
drop_data_scaled = drop_data.copy()
drop_data_scaled[drop_data_scaled.columns] = scaler.fit_transform(drop_data_scaled)

# n=1 as we only want to select one component
pca = PCA(n_components=1)

#selecting 3 attributes to get a combination
a_dict = dict()   # dictionary to hold the variance of group of attributes        dict[attributes-name] = 1st PCA comp

# Three attribute group
for i in range (len(drop_data_scaled.columns) - 2):
    for j in range (i+1, len(drop_data_scaled.columns) - 1):
        for k in range (j+1, len(drop_data_scaled.columns) - 0):
            input_cols = [drop_data_scaled.columns[i], drop_data_scaled.columns[j], drop_data_scaled.columns[k]]
            col_str = "" + drop_data_scaled.columns[i] + "," + drop_data_scaled.columns[j] + "," + drop_data_scaled.columns[k]
            pca_strength = pca.fit_transform(drop_data_scaled[input_cols]) # applying PCA
            var = np.round(pca.explained_variance_ratio_, decimals=3) * 100 # variance on the first component
            print(col_str,  "=" , var)
            a_dict[col_str] = var

import operator
# sorting the dictionary
sorted_dict = {k: v for k, v in sorted(a_dict.items(), key=lambda item: item[1])}
single_a_dict = dict()

count = 0

# using the first 35
for key in sorted_dict:  
    temp = key.split(",")  # key split to see attributes
    for val in temp:       # for each attribute, count how many times it is present in the ammount specified
        if val in single_a_dict:
            single_a_dict[val] += 1
        else:
            single_a_dict[val] = 1
    if count == 35:
        break
    count+=1

#Using bargraph to visualise

df = pd.DataFrame([single_a_dict])

plt.xticks(rotation='vertical')
plt.bar(single_a_dict.keys(), single_a_dict.values(), width=0.5, color='g')

df.head()

data_items = single_a_dict.items()
data_list = list(data_items)

df = pd.DataFrame(data_list)

df.head()

df.columns=['key','value']

value_cut_off_point = 10

df.loc[df['value'] <= value_cut_off_point, 'key']

PCA_remove_count = len(df.loc[df['value'] <= value_cut_off_point, 'key'])
print(PCA_remove_count)

data.head()

i = 0
while i < PCA_remove_count:
  x = df.loc[df['value'] <= value_cut_off_point, 'key'].iloc[i]
  data = data.drop(columns=[x])
  i = i + 1

data.head()

"""Creating X axis with features for prediction (indipendant variables) and target y for prediction (dependant variable)"""

data_final = data.copy()


X = pd.DataFrame(data_final, columns=data_final.columns)
X = X.drop(columns=['strength'])


y = pd.DataFrame(data.strength)

"""## Viewing X and y"""

X.head()

y.head()

"""## Creating test and train sets"""

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    train_size=0.80, 
                                                    random_state=1,
                                                    )
#Converting y_train into 1d array
y_train = y_train.values.ravel()

print('X_train shape', y_train.shape, 'X_test shape', y_test.shape)

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.tree import DecisionTreeRegressor

#libraries for evaluation import
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_squared_log_error

# Defining model algorithms for regression
LR_model= LinearRegression()
DTR_model = DecisionTreeRegressor(random_state=0)
RFR_model = RandomForestRegressor()
SVR_model =  SVR()
ETR_model = ExtraTreesRegressor()

#Fitting models on the training set, then predicting on the test set

#Linear Regressor
LR_model.fit(X_train, y_train)
LR_predictions = LR_model.predict(X_test)

#Decision Tree Regressor
DTR_model.fit(X_train, y_train)
DTR_predictions = DTR_model.predict(X_test)

#Random Forest Regressor
RFR_model.fit(X_train, y_train)
RFR_predictions = RFR_model.predict(X_test)

#Support Vector Regressor
SVR_model.fit(X_train, y_train)
SVR_predictions = SVR_model.predict(X_test)

#Extra Trees Regressor
ETR_model.fit(X_train, y_train)
ETR_predictions = ETR_model.predict(X_test)

#Evaluation of models

#Linear Regression
print('Linear Regression:')
#R2 score:
print('Linear regression R2 score: {}'.format(r2_score(y_test,LR_predictions)))
#Mean absolute error:
print('Linear regression Mean Absolute Error score: {}'.format(mean_absolute_error(y_test,LR_predictions)))
#Mean squared error score:
print('Linear regression Mean Squared Error score: {}'.format(mean_squared_error(y_test,LR_predictions)))
#Root mean squared error:
print('Linear regression Root Mean Error score: {}'.format(np.sqrt(mean_squared_error(y_test,LR_predictions))))
#Roor mean squared log error:
print('Linear regression Root Mean Squared Log Error score: {}\n'.format(np.sqrt(mean_squared_log_error(y_test,LR_predictions))))


#Decision Tree Regression
print('Decision Tree Regression:')
#R2 score:
print('Decision tree regression R2 score: {}'.format(r2_score(y_test,DTR_predictions)))
#Mean absolute error:
print('Decision tree regression Mean Absolute Error score: {}'.format(mean_absolute_error(y_test,DTR_predictions)))
#Mean squared error score:
print('Decision tree regression Mean Squared Error score: {}'.format(mean_squared_error(y_test,DTR_predictions)))
#Root mean squared error:
print('Decision tree regression Root Mean Error score: {}'.format(np.sqrt(mean_squared_error(y_test,DTR_predictions))))
#Roor mean squared log error:
print('Decision tree regression Root Mean Squared Log Error score: {}\n'.format(np.sqrt(mean_squared_log_error(y_test,DTR_predictions))))

#Random Forest Regression
print('Random Forest Regression:')
#R2 score:
print('Random forest regression R2 score: {}'.format(r2_score(y_test,RFR_predictions)))
#Mean absolute error:
print('Random forest regression Mean Absolute Error score: {}'.format(mean_absolute_error(y_test,RFR_predictions)))
#Mean squared error score:
print('Random forest regression Mean Squared Error score: {}'.format(mean_squared_error(y_test,RFR_predictions)))
#Root mean squared error:
print('Random forest regression Root Mean Error score: {}'.format(np.sqrt(mean_squared_error(y_test,RFR_predictions))))
#Roor mean squared log error:
print('Random forest regression Root Mean Squared Log Error score: {}\n'.format(np.sqrt(mean_squared_log_error(y_test,RFR_predictions))))

#Support Vector Regression
print('Support Vector Regression:')
#R2 score:
print('Support vector regression R2 score: {}'.format(r2_score(y_test,SVR_predictions)))
#Mean absolute error:
print('Support vector regression Mean Absolute Error score: {}'.format(mean_absolute_error(y_test,SVR_predictions)))
#Mean squared error score:
print('Support vector regression Mean Squared Error score: {}'.format(mean_squared_error(y_test,SVR_predictions)))
#Root mean squared error:
print('Support vector regression Root Mean Error score: {}'.format(np.sqrt(mean_squared_error(y_test,SVR_predictions))))
#Roor mean squared log error:
print('Support vector regression Root Mean Squared Log Error score: {}\n'.format(np.sqrt(mean_squared_log_error(y_test,SVR_predictions))))

#Extra Trees Regression
print('Extra Trees Regression:')
#R2 score:
print('Extra trees regression R2 score: {}'.format(r2_score(y_test,ETR_predictions)))
#Mean absolute error:
print('Extra trees regression Mean Absolute Error score: {}'.format(mean_absolute_error(y_test,ETR_predictions)))
#Mean squared error score:
print('Extra trees regression Mean Squared Error score: {}'.format(mean_squared_error(y_test,ETR_predictions)))
#Root mean squared error:
print('Extra trees regression Root Mean Error score: {}'.format(np.sqrt(mean_squared_error(y_test,ETR_predictions))))
#Roor mean squared log error:
print('Extra trees regression Root Mean Squared Log Error score: {}\n'.format(np.sqrt(mean_squared_log_error(y_test,ETR_predictions))))

#Actual vs Predicted plot for Linear Regressor
fig, ax = plt.subplots()
ax.scatter(y_test, LR_predictions)
ax.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4)
ax.set_title('Linear Regressor\n Actual VS Predicted Values')
ax.set_xlabel('Actual values')
ax.set_ylabel('Predicted values')
plt.show()

#Actual vs Predicted plot for Decision Tree Regressor
fig, ax = plt.subplots()
ax.scatter(y_test, DTR_predictions)
ax.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4)
ax.set_title('Decision Tree Regressor\n Actual VS Predicted Values')
ax.set_xlabel('Actual values')
ax.set_ylabel('Predicted values')
plt.show()

#Actual vs Predicted plot for Decision Tree Regressor
fig, ax = plt.subplots()
ax.scatter(y_test, RFR_predictions)
ax.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4)
ax.set_title('Random forest Regressor\n Actual VS Predicted Values')
ax.set_xlabel('Actual values')
ax.set_ylabel('Predicted values')
plt.show()

#Actual vs Predicted plot for Support Vector Regressor
fig, ax = plt.subplots()
ax.scatter(y_test, SVR_predictions)
ax.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4)
ax.set_title('Support Vector Regressor\n Actual VS Predicted Values')
ax.set_xlabel('Actual values')
ax.set_ylabel('Predicted values')
plt.show()

#Actual vs Predicted plot for Extra Trees Regressor
fig, ax = plt.subplots()
ax.scatter(y_test, ETR_predictions)
ax.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4)
ax.set_title('Extra Trees Regressor\n Actual VS Predicted Values')
ax.set_xlabel('Actual values')
ax.set_ylabel('Predicted values')
plt.show()