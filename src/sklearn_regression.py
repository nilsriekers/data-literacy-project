from sklearn import linear_model

def sklearn_regression(X_test, X_train, y_train):
    '''Computes OLS weights for linear regression without regularization using the sklearn library on the training set and 
       returns weights and testset predictions.
    
       Inputs:
         X_test: (n_observations, n_features), numpy array with predictor values of the test set 
         X_train: (n_observations, n_features), numpy array with predictor values of the training set
         y_train: (n_observations,) numpy array with true target values for the training set
         
       Outputs:
         weights: The weight vector for the regerssion model including the offset
         y_pred: The predictions on the TEST set
          
         
       Note:
         The sklearn library automatically takes care of adding a column for the offset.     
    
    '''
    
    # Instantiate LinearRegression object
    lm = linear_model.LinearRegression()
    # Fit linear model to the training data
    lm.fit(X_train, y_train)
    
    # Obtain the weights estimated
    weights = lm.coef_
    
    # Make prediction using the trained model
    y_pred = lm.predict(X_test)
    
    return weights, y_pred
