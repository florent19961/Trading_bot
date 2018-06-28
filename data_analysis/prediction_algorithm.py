import pandas as pd
import numpy as np
import results
import matplotlib.pyplot as plt
import seaborn as sns
import machine_learning_fitting

# Ce input_df doit contenir la ligne qu'on souhaite prédire (on veut un DATAFRAME)
#['timestamp' 'date' 'length' 'low_price' 'high_price' 'opening_price'
# 'closing_price' 'volume' 'bdb_low' 'bdb_high' 'mme12' 'mme26' 'stochastic'
# 'macd']
# et ceci sous


def prediction(input_df):
    
    ### 1st step 
    ##Vector transformation

    #On ajoute les colonnes nécessaires à l'analyse
    complete_df = Machine_learning_fitting.add_columns(input_df)

    # On sélectionne seulement les valeurs utiles dans notre dataframe
    selected_df = Machine_learning_fitting.feature_selection(complete_df)

    # On convertit notre dataframe en numpy array
    array_selected = np.array(selected_df)

    ### 2nd step
    ## Standard_Scaler and PCA

    # Standard Scaler's parameters loading
    mean_loaded = pickle.load(open("mean.p", "rb"))
    std_loaded = pickle.load(open( "std.p", "rb"))

    # Standard Scaler's reconstruction
    scaler = StandardScaler(copy=False)
    scaler.mean_ = mean_loaded
    scaler.std_ = std_loaded

    # fit_transform data
    X_scale = scaler.fit_transform(array_selected)

    # PCA Loading
    pca_pck = pickle.load( open( "pca.p", "rb" ) )

    # Transformation test and train data from PCA loaded
    X = pca_pck.transform(X_scale)

    ### 3rd step
    ## Prediction
    
    clf = pickle.load( open( "clf.p", "rb" ) )
    prediction = clf.predict(X)
    
    return(prediction)