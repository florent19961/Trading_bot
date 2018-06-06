def macd(data_row, seuil_a = -0.05, seuil_b = 0.0019, seuil_c = 0.014, seuil_d = -0.0225):
        
    macd = data_row['macd_n']
    macd_derivative = data_row['macd_derivative_n']
    macd_historic = data_row['macd_historic']

    if macd >= seuil_a:
        if macd_derivative > seuil_b and macd_historic > seuil_c:
            return 1
        else:
            if macd_historic <= seuil_d:
                return -1
            else:
                return 0
    else:
        return -1
    
def bdb_high(data_row, seuil_bdb_high=0.941):
        
    bdb_high = data_row['bdb_high_n']
    if bdb_high < seuil_bdb_high:
        return -1
    else:
        return 0    

def bdb_low(data_row, seuil_bdb_low=1.02788):
        
    bdb_low = data_row['bdb_low_n']
    if bdb_low > seuil_bdb_low:
        return 1
    else:
        return 0
    
def decision_vector(data_row):
    macd_decision = data_row['macd_decision']
    bdb_low_decision = data_row['bdb_low_decision']
    bdb_high_decision = data_row['bdb_high_decision']
    #print(bdb_high_decision,bdb_low_decision)
    if bdb_low_decision == 0 and bdb_high_decision == 0:
        return macd_decision
    elif bdb_low_decision == 1: 
        return 1
    elif bdb_high_decision == -1:
        return -1

#how to use it
#df['bdb_high_decision'] =  df.apply(bdb_high, args = (seuil_bdb_high,), axis = 1)#0.941
#df['bdb_low_decision'] =  df.apply(bdb_low, args = (seuil_bdb_low,), axis = 1)#1.049
#df['macd_decision'] = df.apply(macd, args = (-0.5, 0.0019, 0.014, -0.0225), axis = 1)
#df['decision_vector'] = df.apply(decision_vector, axis = 1)