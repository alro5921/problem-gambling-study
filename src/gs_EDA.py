import numpy as np
import pandas as pd
import pickle

# 12 months, summary+weekly
#gs_path = f'model/rf_rgrid_output_09-15-13:23.pkl'

# 12 months, summary
gs_path = f'model/rf_rgrid_output_09-15-13:29.pkl'
if __name__ == "__main__":
    with open(gs_path, 'rb') as f:
        gs = pickle.load(f)
    df = pd.DataFrame(gs.cv_results_)
    param_cols = [col for col in df.columns if col[:6] == "param_"]
    df = df[[*param_cols, 'mean_test_score', 'rank_test_score']]
    sorted_df = df.sort_values(by='rank_test_score')
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        pass
        #print(sorted_df[:20])
    rf = gs.best_estimator_
    importances = rf.feature_importances_
    print(importances)