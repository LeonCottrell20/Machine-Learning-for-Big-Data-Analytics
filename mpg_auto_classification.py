# -*- coding: utf-8 -*-
"""MPG with UAD and stacking.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rU3LZGgFXj2t4e9ngwITHgvmU3ittuQ9
"""


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

"""# Data cleaning and quality check. Using unsupervised anomaly detection to remove any outliers in the data"""

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

"""## PYOD (Python Outlier Detection) for unsupervised anomaly detection techniques"""

from pyod.models.ecod import ECOD
from pyod.models.knn import KNN
from pyod.models.lof import LOF
from pyod.utils.example import visualize

"""### Using the KNN model for outlier detection"""

# Initiate a KNN model
KNN_model = KNN(contamination=0.05)
# Fit the model to the whole dataset
KNN_model.fit(data)
# Find the labels
outlier_labels = KNN_model.labels_
# Find the number of outliers
number_of_outliers = len(outlier_labels[outlier_labels == 1])
print(number_of_outliers)

"""### Using the LOF model for outlier detection"""

# Initiate a KNN model
LOF_model = LOF(contamination=0.05)
# Fit the model to the whole dataset
LOF_model.fit(data)
# Find the labels
outlier_labels = LOF_model.labels_
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

"""### Using a graph to visualise the outliers detected by the algorithms"""

knn_data = model_fit(KNN_model, data)
plot_anom(knn_data)

"""### Removing the data points considered outliers by the KNN model"""

#Removing data points considered anomalies by KNN
knn_data = knn_data.drop(knn_data[knn_data['Predictions'] == 1].index)
knn_data = knn_data.drop(columns=['Predictions'])

LOF_model = LOF()
lof_data = model_fit(LOF_model, data)
plot_anom(lof_data)

"""### Removing the data points considered outliers by the LOF model"""

#Removing data points considered anomalies by LOF
lof_data = lof_data.drop(lof_data[lof_data['Predictions'] == 1].index)
lof_data = lof_data.drop(columns=['Predictions'])

knn_data.head()

mpg_max = knn_data.mpg.max()
mpg_min = knn_data.mpg.min()
print("max:",mpg_max)
print("min:",mpg_min)

"""### Binning the MPG values into mpg_cat, out created class label"""

mpgM = knn_data['mpg'].mean()

knn_data['mpg_cat'] = pd.cut(knn_data['mpg']
                              , bins=[0,mpgM,mpg_max]
                              , labels=[0,1])
knn_data["mpg_cat"].hist()
print(knn_data["mpg_cat"].value_counts())

"""### Viewing the ammount of data points in each catagory with under sampling. only 179 in each"""

# class count
count_class_LH, count_class_UH = knn_data.mpg_cat.value_counts()
# Divide by class
data_class_LH = knn_data[knn_data['mpg_cat']== 0]
data_class_UH = knn_data[knn_data['mpg_cat']== 1]

data_class_LH_under = data_class_LH.sample(count_class_UH)
data_under = pd.concat([data_class_LH_under, data_class_UH], axis=0)

print('Random under-sampling:')
print(data_under.mpg_cat.value_counts())

data_under.mpg_cat.value_counts().plot(kind='bar', title='Count (target)');

"""## SMOTE for over sample

### Using SMOTE, 199 data points are available for each catagory of our class label. This will be invaluable given the small nature of the data set
"""

from imblearn.over_sampling import SMOTE
oversample = SMOTE()

X = knn_data.drop(['mpg_cat'], axis=1)
y = knn_data.mpg_cat

features_X, target_y = oversample.fit_resample(X, y)

print('SMOTE over sampling:')
print(target_y.value_counts())
target_y.value_counts().plot(kind='bar', title='Count (target)');

plt.figure(figsize=(23,5))
sns.heatmap(data=data.corr(), annot=True);

from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import plot_roc_curve
from sklearn.model_selection import StratifiedKFold
import pandas as pd

"""# Principle Componant Analysis (PCA) for feature selection"""

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# initializing standard scaler.
scaler = StandardScaler()

#droping MPG, as it is directly related to mpg_cat
data_under = knn_data.drop(columns=['mpg'])

droped_data = data_under.copy()
output_data = droped_data.loc[:, ['mpg_cat']]
droped_data = droped_data.drop(columns=['mpg_cat'])
# Scaling the PCA
droped_data_scaled = droped_data.copy()
droped_data_scaled[droped_data_scaled.columns] = scaler.fit_transform(droped_data_scaled)

data_under.head()

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

data_under.head()

i = 0
while i < PCA_remove_count:
  x = df.loc[df['value'] <= 7, 'key'].iloc[i]
  data_under = data_under.drop(columns=[x])
  i = i + 1

data_under.head()

from imblearn.over_sampling import SMOTE
oversample = SMOTE()

X = data_under.drop(['mpg_cat'], axis=1)
y = data_under.mpg_cat

features_X, target_y = oversample.fit_resample(X, y)

print('SMOTE over sampling:')
print(target_y.value_counts())
target_y.value_counts().plot(kind='bar', title='Count (target)');

X.head()

y.head()

data_final = data_under.copy()


X = pd.DataFrame(features_X, columns=features_X.columns)



y = pd.DataFrame(target_y)

X.head()

y.head()

print(y.value_counts())

import statsmodels.api as stat
from statsmodels.stats.outliers_influence import variance_inflation_factor 



#VIF calculation
VIFcalc = stat.tools.add_constant(X)
S = pd.Series([variance_inflation_factor(VIFcalc.values, i) for i in range(VIFcalc.shape[1])], index=VIFcalc.columns)
print('Output: \n\n{}\n'.format(S))

#print('Recomended removal:')
#for x in S.index:
 # if S.loc[x]> 10:
 #   print(str(x))
 #   if x != 'const':
 #     data_final = data_final.drop(columns=[str(x)])

X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    train_size=0.80, 
                                                    random_state=1,
                                                    stratify=y)

print('X_train shape', y_train.shape, 'X_test shape', y_test.shape)

print('train_class_one_ratio', np.count_nonzero(y_train==1) / len(y_train))
print('test_class_one_ratio', np.count_nonzero(y_test==1) / len(y_test))

from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import StackingClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.linear_model import Perceptron
from sklearn.linear_model import PassiveAggressiveClassifier

def stacking():
  # Including the different models to be used for stacking, base level L0
	L0 = []
	L0.append(('KNN', KNeighborsClassifier()))
	L0.append(('CART', DecisionTreeClassifier()))
	L0.append(('NB', GaussianNB()))
	L0.append(('SVM', SVC(gamma='auto')))
	L0.append(('LR', LogisticRegression(max_iter=10000)))
	L0.append(('SGDClassifier', SGDClassifier(loss="hinge", penalty="l2", max_iter=10000)))
	L0.append(('RandomForestClassifier', RandomForestClassifier(n_estimators=10)))
	L0.append(('AdaBoostClassifier', AdaBoostClassifier(n_estimators=100)))
	# Define meta learner model as L1
	L1 = LogisticRegression(max_iter=10000)
	# Define the stacking ensemble
	model = StackingClassifier(estimators=L0, final_estimator=L1, cv=10)
	return model

# Spot Check Algorithms for class_label classification
pred_models = []
pred_models.append(('KNN', KNeighborsClassifier()))
pred_models.append(('DecisionTreeClassifier', DecisionTreeClassifier()))
pred_models.append(('GaussianNB', GaussianNB()))
pred_models.append(('SupportVectorMachine', SVC(gamma='auto')))
pred_models.append(('LogisticRegression', LogisticRegression(max_iter=10000)))
pred_models.append(('SGDClassifier', SGDClassifier(loss="hinge", penalty="l2", max_iter=10000)))
pred_models.append(('RandomForestClassifier', RandomForestClassifier(n_estimators=10)))
pred_models.append(('AdaBoostClassifier', AdaBoostClassifier(n_estimators=100)))
pred_models.append(('RandomForestClassifierOPTIMISED', RandomForestClassifier(bootstrap=True, max_depth=110, max_features= 'sqrt', min_samples_leaf=1, min_samples_split=2, n_estimators=1000)))

#Stacking model 
pred_models.append(('Stacking', stacking()))


# evaluate each model, one after another.Uses 5-fold cross validation
results = []
names = []
for name, model in pred_models:
	skf = StratifiedKFold(n_splits=5, random_state=1, shuffle=True)
	cross_val_results = cross_val_score(model, X_train, y_train.values.ravel(), cv=skf, scoring='accuracy')
	results.append(cross_val_results)
	names.append(name)
	print('%s: %f (%f)' % (name, cross_val_results.mean(), cross_val_results.std()))




# Comparison of the different models:

stack = stacking()
stack.fit(X_train, y_train)
y_pred = stack.predict(X_test)
cm2 = confusion_matrix(y_test, y_pred.round())
sns.heatmap(cm2, annot=True, fmt=".0f")

print(classification_report(y_test, y_pred))

from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
stack_roc_auc = roc_auc_score(y_test, stack.predict(X_test))
fpr, tpr, thresholds = roc_curve(y_test, stack.predict_proba(X_test)[:,1])
plt.figure()
plt.plot(fpr, tpr, label='Stacking method (area = %0.2f)' % stack_roc_auc)
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic')
plt.legend(loc="lower right")
plt.savefig('Log_ROC')
plt.show()

RFO = RandomForestClassifier(bootstrap=True, max_depth=110, max_features= 'sqrt', min_samples_leaf=1, min_samples_split=2, n_estimators=1000)
RFO.fit(X_train, y_train)
y_pred = RFO.predict(X_test)
cm2 = confusion_matrix(y_test, y_pred.round())
sns.heatmap(cm2, annot=True, fmt=".0f")

print(classification_report(y_test, y_pred))

from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
RFO_roc_auc = roc_auc_score(y_test, RFO.predict(X_test))
fpr, tpr, thresholds = roc_curve(y_test, RFO.predict_proba(X_test)[:,1])
plt.figure()
plt.plot(fpr, tpr, label='Optimised Random Forest method (area = %0.2f)' % RFO_roc_auc)
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic')
plt.legend(loc="lower right")
plt.savefig('Log_ROC')
plt.show()

nb = GaussianNB()
nb.fit(X_train, y_train)
y_pred = nb.predict(X_test)
cm2 = confusion_matrix(y_test, y_pred.round())
sns.heatmap(cm2, annot=True, fmt=".0f")

print(classification_report(y_test, y_pred))

from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
nb_roc_auc = roc_auc_score(y_test, nb.predict(X_test))
fpr, tpr, thresholds = roc_curve(y_test, nb.predict_proba(X_test)[:,1])
plt.figure()
plt.plot(fpr, tpr, label='Naive Bayes (area = %0.2f)' % nb_roc_auc)
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic')
plt.legend(loc="lower right")
plt.savefig('Log_ROC')
plt.show()

from sklearn import tree
dt = tree.DecisionTreeClassifier()
dt.fit(X_train, y_train)
y_pred = dt.predict(X_test)
cm1 = confusion_matrix(y_test, y_pred.round())
sns.heatmap(cm1, annot=True, fmt=".0f")

print(classification_report(y_test, y_pred))

from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
dt_roc_auc = roc_auc_score(y_test, dt.predict(X_test))
fpr, tpr, thresholds = roc_curve(y_test, dt.predict_proba(X_test)[:,1])
plt.figure()
plt.plot(fpr, tpr, label='Decision tree (area = %0.2f)' % dt_roc_auc)
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic')
plt.legend(loc="lower right")
plt.savefig('Log_ROC')
plt.show()

knn = KNeighborsClassifier()
knn.fit(X_train, y_train)
y_pred = knn.predict(X_test)
cm2 = confusion_matrix(y_test, y_pred.round())
sns.heatmap(cm2, annot=True, fmt=".0f")

print(classification_report(y_test, y_pred))

from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
knn_roc_auc = roc_auc_score(y_test, knn.predict(X_test))
fpr, tpr, thresholds = roc_curve(y_test, knn.predict_proba(X_test)[:,1])
plt.figure()
plt.plot(fpr, tpr, label='K-nearest Neighbor (area = %0.2f)' % knn_roc_auc)
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic')
plt.legend(loc="lower right")
plt.savefig('Log_ROC')
plt.show()

SVM = SVC(gamma='auto')
SVM.fit(X_train, y_train)
y_pred = SVM.predict(X_test)
cm2 = confusion_matrix(y_test, y_pred.round())
sns.heatmap(cm2, annot=True, fmt=".0f")

print(classification_report(y_test, y_pred))

LOGR = LogisticRegression()
LOGR.fit(X_train, y_train)
y_pred = nb.predict(X_test)
cm2 = confusion_matrix(y_test, y_pred.round())
sns.heatmap(cm2, annot=True, fmt=".0f")

print(classification_report(y_test, y_pred))

from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
LOGR_roc_auc = roc_auc_score(y_test, LOGR.predict(X_test))
fpr, tpr, thresholds = roc_curve(y_test, LOGR.predict_proba(X_test)[:,1])
plt.figure()
plt.plot(fpr, tpr, label='Logistical Regression (area = %0.2f)' % LOGR_roc_auc)
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic')
plt.legend(loc="lower right")
plt.savefig('Log_ROC')
plt.show()

SGD = SGDClassifier(loss="hinge", penalty="l2", max_iter=10000)
SGD.fit(X_train, y_train)
y_pred = SGD.predict(X_test)
cm2 = confusion_matrix(y_test, y_pred.round())
sns.heatmap(cm2, annot=True, fmt=".0f")

print(classification_report(y_test, y_pred))

ADA = AdaBoostClassifier(n_estimators=100)
ADA.fit(X_train, y_train)
y_pred = ADA.predict(X_test)
cm2 = confusion_matrix(y_test, y_pred.round())
sns.heatmap(cm2, annot=True, fmt=".0f")

print(classification_report(y_test, y_pred))

from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
ADA_roc_auc = roc_auc_score(y_test, ADA.predict(X_test))
fpr, tpr, thresholds = roc_curve(y_test, ADA.predict_proba(X_test)[:,1])
plt.figure()
plt.plot(fpr, tpr, label='AdaBoost Classifier (area = %0.2f)' % ADA_roc_auc)
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic')
plt.legend(loc="lower right")
plt.savefig('Log_ROC')
plt.show()

RF = RandomForestClassifier(n_estimators=10)
RF.fit(X_train, y_train)
y_pred = RF.predict(X_test)
cm2 = confusion_matrix(y_test, y_pred.round())
sns.heatmap(cm2, annot=True, fmt=".0f")

print(classification_report(y_test, y_pred))

from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
RF_roc_auc = roc_auc_score(y_test, RF.predict(X_test))
fpr, tpr, thresholds = roc_curve(y_test, RF.predict_proba(X_test)[:,1])
plt.figure()
plt.plot(fpr, tpr, label='Random Forest (area = %0.2f)' % RF_roc_auc)
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic')
plt.legend(loc="lower right")
plt.savefig('Log_ROC')
plt.show()

"""## Using best model with sklearn's RandomizedSearchCV, which trys to find the best parameters which yeild the most accurate results
* Step 1: Create random grid of params to use
* Step 2: Uses RandomizedSearchCV with the params we selected to be in the random grid, with 3-fold crossvalidation
* Step 3: Prints out the parameters that had the highest prediction accuracy
"""

from sklearn.model_selection import RandomizedSearchCV

# Tree count
estimator_number = [int(x) for x in np.linspace(start = 200, stop = 2000, num = 10)]
#  # of Features at split
max_features = ['auto', 'sqrt']
# Tree levels
max_depth = [int(x) for x in np.linspace(10, 110, num = 11)]
max_depth.append(None)
# Min # of samples required to split at node
min_samples_split = [2, 5, 10]
# Min # of samples required at leaf nodes
min_samples_leaf = [1, 2, 4]
# Method of selecting samples for training each tree
bootstrap = [True, False]
# Create the random grid
RG = {'n_estimators': estimator_number,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               'bootstrap': bootstrap}
print(RG)

#Sets the model we are testsing diff params on
##rf = RandomForestClassifier()
# Starts random search for the best params
# Uses 100 different combinations, with 3-fold cross validation
##rf_best_params = RandomizedSearchCV(estimator = rf, param_distributions = RG, n_iter = 100, cv = 3, verbose=2, random_state=42, n_jobs = -1)
# Fit
##rf_best_params.fit(X_train, y_train)

##rf_best_params.best_params_

"""## Deep Learning using Keras. 4 node input layer with 8 and 4 node hidden layers"""

from keras.models import Sequential
from keras.layers import Dense
from keras.models import model_from_json

# define the keras model
model = Sequential()
model.add(Dense(8, input_dim=4, activation='relu'))
model.add(Dense(4, activation='relu'))


model.add(Dense(1, activation='sigmoid'))
# compile the keras model (binary_crossentropy)
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
# fit the keras model on the dataset
model.fit(X_train, y_train, epochs=100, batch_size=10)
# evaluate the keras model
_, accuracy = model.evaluate(X_train, y_train)
print('Accuracy: %.2f' % (accuracy*100))



#Saving the model (serialize to JSON)
model_saved = model.to_json()
with open("model.json", "w") as json_file:
    json_file.write(model_saved)
# serialize weights to HDF5
model.save_weights("model.h5")
print('MODEL SAVED')

"""## Loading the Deep Learning model and testing on unseen data"""

# loading model to predict on test set
j_file = open('model.json', 'r')
json = j_file.read()
j_file.close()
model = model_from_json(json)
# load weights into new model
model.load_weights("model.h5")
print("loaded correctly")
 
# evaluate loaded model on test data
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
score = model.evaluate(X_test, y_test, verbose=0)
print("%s: %.2f%%" % (model.metrics_names[1], score[1]*100))
