import pandas as pd
import numpy as np
import results
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from sklearn.svm import LinearSVC


plt.style.use('seaborn-poster')

file_name = 'btc_eur_3600.csv'
df_primary = pd.read_csv(r'C:\Users\flore\.spyder-py3\trading_bot\btc_eur_3600_290418.csv')

### 
# Normalisation
# This allows to have all our data on the same scale. To this end it is relevant to compare different chandelier together
def add_columns(df_primary):
    df_primary['bdb_high_n'] = df_primary['bdb_high'] / df_primary['opening_price']
    df_primary['bdb_low_n'] = df_primary['bdb_low'] / df_primary['opening_price']
    df_primary['high_price_n'] = df_primary['high_price'] / df_primary['opening_price']
    df_primary['low_price_n'] = df_primary['low_price'] / df_primary['opening_price']
    df_primary['macd_n'] = df_primary['macd'] / df_primary['opening_price']
    df_primary['macd_derivative_n'] = df_primary['macd_n'] - df_primary['macd_n'].shift(1)
    df_primary['variation'] = (df_primary['closing_price'] - df_primary['opening_price']) / df_primary['opening_price'] * 100


    df_primary['macd-1'] = df_primary['macd_n'].shift(1)
    df_primary['macd-2'] = df_primary['macd_n'].shift(2)
    df_primary['macd-3'] = df_primary['macd_n'].shift(3)

    df_primary['var-1'] = df_primary['variation'].shift(1)
    df_primary['var-2'] = df_primary['variation'].shift(2)

    # MACD is one of the most important indicator in stock prices classic analysis, we are creating its derivate, and its 
    # second derivate to see if there is a correlation with the stock prices
    df_primary['macd_second_derivative_n'] = df_primary['macd_derivative_n'] - df_primary['macd_derivative_n'].shift(1)
    df_primary['macd_historic'] = df_primary['macd_n'] + df_primary['macd_n'].shift(2)
    df_primary['product_macd'] = df_primary["macd_n"]*df_primary['macd_derivative_n']

    # Volatility
    df_primary['volatility'] = df_primary['high_price_n'] - df_primary['low_price_n']
    df_primary['derivate_volatility'] = df_primary['volatility'] - df_primary['volatility'].shift(1)
    df_primary['derivate_volume'] = df_primary['volume'] - df_primary['volume'].shift(1)

    # Stochastique
    df_primary['stochastic_derivative'] = df_primary['stochastic'] - df_primary['stochastic'].shift(1)
    df_primary['product_stochastic'] = df_primary["stochastic"]*df_primary['stochastic_derivative']
    # Redudancy variables dropped
    cols = ['bdb_high_n', 'bdb_low_n', 'macd_n', 'macd_derivative_n', 'closing_price', 'variation', 'opening_price', 
            'high_price_n', 'low_price_n', 'macd-1', 'macd-2', 'macd-3', 'var-1','var-2', 'macd_second_derivative_n',
           'product_macd', 'volatility', 'derivate_volatility', 'derivate_volume', 'stochastic_derivative', 'product_stochastic','macd_historic']
    df_primary = df_primary[cols]
    df_primary['closing_price'] = df_primary['closing_price'].shift(1)
    return(df_primary)

# Trend Label, which is rolling on a 24h window and put a 1 (buy) or a -1 (sell) when we are on the maximum of those 24 hours    
# 0 if this is not a maximum. 3-classes classification
def local_extrema_label(window_array):
    if window_array[0] == max(window_array):
        return -1
    elif window_array[0] == min(window_array):
        return 1
    else:
        return 0   

def label_creation(df_train, window_length=12):

    df_train['label_trend_3_classes'] = df_train['closing_price'].rolling(window=window_length,center=False
                                    ).apply(func=local_extrema_label
                                    ).shift(-window_length+1)


    label = df_train['label_trend_3_classes'].values.tolist()
    new_label = []
    high_trend = True

    #binarization

    for i in range(len(label)):

        if label[i] in (0,1) and high_trend:
            new_label.append(1)
        elif label[i] == -1 and high_trend:
            high_trend = False
            new_label.append(0)

        elif label[i] in (0,-1) and not high_trend:
            new_label.append(0)
        elif label[i] == 1 and not high_trend:
            high_trend = True
            new_label.append(1)

    df_train = pd.concat([df_train, pd.DataFrame(new_label, columns = ['label_trend_2_classes'])], axis = 1)
    df_train.dropna(inplace=True)    
    df_train_label = df_train['label_trend_2_classes']
    return(df_train, df_train_label)

def feature_selection(df):
    cols = ['bdb_high_n', 'bdb_low_n', 'macd_n', 'macd_derivative_n',
           'high_price_n', 'low_price_n', 'macd-1', 'macd-2', 'macd-3',
           'var-1', 'var-2', 'macd_second_derivative_n', 'product_macd',
           'volatility', 'derivate_volatility', 'derivate_volume',
           'stochastic_derivative', 'product_stochastic']
    return(df[cols])


df_train = add_columns(df_primary)
df_train, df_train_label = label_creation(df_train)
df_train_features = feature_selection(df_train)



### PCA & Standard Scaler Fitting/dumping


X_train = np.array(df_train_features)
y_train = np.array(df_train_label)

from sklearn.preprocessing import StandardScaler

#StandardScaler fitting
scaler = StandardScaler()
scaler.fit(X_train)

X_train = scaler.transform(X_train)

# StandardScaler parameters
mean = scaler.mean_
std = scaler.var_

# Save of those two parameters lists
pickle.dump(mean, open( "mean.p", "wb" ))
pickle.dump(std, open("std.p", "wb"))

from sklearn.decomposition import PCA

# PCA creation and fitting
pca = PCA(0.95)
pca = pca.fit(X_train)

#Classic PCA
X_train = pca.transform(X_train)

# PCA Saving
pickle.dump(pca, open( "pca.p", "wb" ))


### Algorithm fitting and dumping


# MLA fitting
clf = LinearSVC(C=10, max_iter=1000, random_state=0)
clf = clf.fit(X_train, y_train)

# MLA fit saved
pickle.dump(clf, open( "clf.p", "wb" ))

clf.score(X_train, y_train)