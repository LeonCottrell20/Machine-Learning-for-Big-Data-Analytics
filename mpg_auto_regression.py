# -*- coding: utf-8 -*-
"""MPG_auto regression.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rpiNzO8mzBUMrlqcDmq2esBlitcpTcxp
"""

!pip install pyod
import os
import numpy as np
import pandas as pd
import sklearn
import matplotlib.pylab as plt
import seaborn as sns
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from tensorflow import keras

data = pd.read_csv('http://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data', sep='\s+')

data.columns=['mpg','cylinders','displacement','horsepower','weight','acceleration','model year','origin','car name']

data.head()

data.describe()

data.info()

data = data.drop(columns=['car name'])

data.horsepower.unique()

data[data['horsepower']== '?']

data.horsepower = pd.to_numeric(data.horsepower.replace('?', np.nan))

data.isna().sum()

data = data.copy()

data = data.interpolate(method="linear")

data.isnull().sum()

data_final = data.copy()

#X = pd.DataFrame(data_final, columns=data_final.columns)
#X = X.drop(columns=['mpg', 'cylinders', 'displacement', 'horsepower', 'acceleration', 'model year', 'origin' ])
X = pd.DataFrame(data_final.weight)
y = pd.DataFrame(data_final.mpg)

# split into train test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)

from pyod.models.knn import KNN
from pyod.utils.example import visualize

# Initiate a KNN model
KNN_model = KNN(contamination=0.05)
# Fit the model to the whole dataset
KNN_model.fit(data)
# Find the labels
outlier_labels = KNN_model.labels_
# Find the number of outliers
number_of_outliers = len(outlier_labels[outlier_labels == 1])
print(number_of_outliers)

def model_fit(model, data, column='mpg'):
    
    anom_data = data.copy()
    data_to_predict = anom_data[column].to_numpy().reshape(-1, 1)
    predictions = model.fit_predict(data_to_predict)
    anom_data['Predictions'] = predictions
    
    return anom_data

def plot_anom(anom_data, x='weight', y='mpg'):

    # categories will be having values from 0 to n
    # for each values in 0 to n it is mapped in colormap
    categories = anom_data['Predictions'].to_numpy()
    colormap = np.array(['g', 'r'])

    f = plt.figure(figsize=(12, 4))
    f = plt.scatter(anom_data[x], anom_data[y], c=colormap[categories])
    f = plt.xlabel(x)
    f = plt.ylabel(y)
    f = plt.xticks(rotation=90)
    plt.show()

knn_data = model_fit(KNN_model, data)
plot_anom(knn_data)

#Removing data points considered anomalies by KNN
knn_data = knn_data.drop(knn_data[knn_data['Predictions'] == 1].index)
knn_data = knn_data.drop(columns=['Predictions'])

"""# Principle Componant Analysis (PCA) for feature selection"""

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# initializing standard scaler.
scaler = StandardScaler()

#droping MPG, as it is directly related to mpg_cat


droped_data = knn_data.copy()
output_data = droped_data.loc[:, ['mpg']]
droped_data = droped_data.drop(columns=['mpg'])
# Scaling the PCA
droped_data_scaled = droped_data.copy()
droped_data_scaled[droped_data_scaled.columns] = scaler.fit_transform(droped_data_scaled)

knn_data.head()

# Selecting one component
pca = PCA(n_components=1)

#selecting 3 attributes to get a combination
a_dict = dict()   # dictionary to hold the variance of group of attributes        dict[attributes-name] = 1st PCA comp

# Three attribute group
for i in range (len(droped_data_scaled.columns) - 2):
    for j in range (i+1, len(droped_data_scaled.columns) - 1):
        for k in range (j+1, len(droped_data_scaled.columns) - 0):
            input_cols = [droped_data_scaled.columns[i], droped_data_scaled.columns[j], droped_data_scaled.columns[k]]
            col_str = "" + droped_data_scaled.columns[i] + "," + droped_data_scaled.columns[j] + "," + droped_data_scaled.columns[k]
            pca_strength = pca.fit_transform(droped_data_scaled[input_cols]) # applying the PCA
            variance = np.round(pca.explained_variance_ratio_, decimals=3) * 100 # variance on the first component
            print(col_str,  "=" , variance)
            a_dict[col_str] = variance

import operator
# sorting the dictionary
sorted_dict = {k: v for k, v in sorted(a_dict.items(), key=lambda item: item[1])}
single_a_dict = dict()

count = 0

# using the first 100
for key in sorted_dict:  
    temp = key.split(",")  # key split to see attributes
    for val in temp:       # for each attribute, count how many times it is present in the ammount specified
        if val in single_a_dict:
            single_a_dict[val] += 1
        else:
            single_a_dict[val] = 1
    if count == 20:
        break
    count+=1

#Using bargraph to visualise

df = pd.DataFrame([single_a_dict])


plt.xticks(rotation='vertical')
plt.bar(single_a_dict.keys(), single_a_dict.values(), width=0.5, color='g')
value_counts = len(single_a_dict)

df.head()

data_items = single_a_dict.items()
data_list = list(data_items)

df = pd.DataFrame(data_list)

df.head()

df.columns=['key','value']

value_cut_off_point = 7

df.loc[df['value'] <= value_cut_off_point, 'key']

PCA_remove_count = len(df.loc[df['value'] <= 7, 'key'])
print(PCA_remove_count)

knn_data.head()

i = 0
while i < PCA_remove_count:
  x = df.loc[df['value'] <= 7, 'key'].iloc[i]
  knn_data = knn_data.drop(columns=[x])
  i = i + 1

knn_data.head()

"""## VIF to detect any multicollinearity within dimensionally reduced data set"""

import statsmodels.api as stat
from statsmodels.stats.outliers_influence import variance_inflation_factor 

#VIF calculation
VIFcalc = stat.tools.add_constant(knn_data)
S = pd.Series([variance_inflation_factor(VIFcalc.values, i) for i in range(VIFcalc.shape[1])], index=VIFcalc.columns)
print('Output: \n\n{}\n'.format(S))

"""Creating X axis with features for prediction (indipendant variables) and target y for prediction (dependant variable)"""

data_final = knn_data.copy()


X = pd.DataFrame(data_final, columns=data_final.columns)
X = X.drop(columns=['mpg'])


y = pd.DataFrame(data_final.mpg)

"""## Viewing X and y"""

X.head()

y.head()

"""## Creating test and train sets"""

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

#Logistical Regression
print('Logistical Regression:')
#R2 score:
print('Logistical regression R2 score: {}'.format(r2_score(y_test,LR_predictions)))
#Mean absolute error:
print('Logistical regression Mean Absolute Error score: {}'.format(mean_absolute_error(y_test,LR_predictions)))
#Mean squared error score:
print('Logistical regression Mean Squared Error score: {}'.format(mean_squared_error(y_test,LR_predictions)))
#Root mean squared error:
print('Logistical regression Root Mean Error score: {}'.format(np.sqrt(mean_squared_error(y_test,LR_predictions))))
#Roor mean squared log error:
print('Logistical regression Root Mean Squared Log Error score: {}\n'.format(np.sqrt(mean_squared_log_error(y_test,LR_predictions))))


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

"""## Actual VS Predicted plot for models created"""

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