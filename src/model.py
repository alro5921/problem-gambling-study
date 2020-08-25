import numpy as np
import pandas as pd
from featurizing import featurize
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix 
import pipeline 

demo_df = pipeline.demo_pipeline()
rg_df = pipeline.rg_pipeline()

if __name__ == '__main__':
    n_app_mask = rg_df['event_type_first'] != 2
    non_appeals = rg_df[n_app_mask]
    user_ids = non_appeals.index[:100]
    X, y = featurize(user_ids)
    X_train, X_test, y_train, y_test = train_test_split(X,y)
    regressor = RandomForestClassifier()
    regressor.fit(X_train,y_train)
    y_pred = regressor.predict(X_test)
    #print("positive_sams:", sum(y_test)/len(y_test))
    #print("Correct:", sum(y_pred == y_test)/len(y_test))
    #for pred, test in zip(y_pred,y_test):
    #    print(pred, test)
    print(confusion_matrix(y_pred,y_test))