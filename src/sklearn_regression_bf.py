from sklearn.pipeline import Pipeline
from sklearn import linear_model
from sklearn import preprocessing

def sklearn_regression_bf(X_test, X_train, y_train, deg=2):
    '''Computes linear regression with basis functions but without regularization using the sklearn library
       on the training set and returns weights and testset predictions.
    
       Inputs:
         X_test: (n_observations, n_features), numpy array with predictor values of the test set
         X_train: (n_observations, n_features), numpy array with predictor values of the training set
         y_train: (n_observations,) numpy array with true target values for the training set
         deg: int, degree of basis function polynomial
         
       Outputs:
         weights: The weight vector for the regerssion model including the offset
         y_pred: The predictions on the TEST set
         
       Note:
         The sklearn library automatically takes care of adding a column for the offset.
    '''
    
    # Set up pipiline
    model = Pipeline([('poly', preprocessing.PolynomialFeatures(degree=deg)),
                      ('linear', linear_model.LinearRegression())])
    
    # Fit linear model to the transformed training data
    model = model.fit(X_train, y_train)
    
    # Obtain the weights estimated
    weights = model.named_steps['linear'].coef_
    
    # Make prediction using the trained model
    y_pred = model.predict(X_test)
    
    return weights, y_pred
