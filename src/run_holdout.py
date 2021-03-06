from pipeline import get_demo_df, get_gam_df, get_rg_df
from processing.features import SUMMARY_NAMES, DAILY_NAMES, WEEKLY_NAMES
from processing.preprocessing import preprocessing
from model import predict

if __name__ == '__main__':
        print("Running on holdout!")
        sleep(10)
        HOLD_DEMO_PATH = 'data/holdout/demographic.csv'
        HOLD_RG_PATH = 'data/holdout/rg_information.csv'
        HOLD_GAM_PATH = 'data/holdout/gambling.csv'
        hold_demo = get_demo_df(HOLD_DEMO_PATH)
        hold_rg = get_rg_df(HOLD_RG_PATH)
        hold_gam = get_gam_df(HOLD_GAM_PATH)
        dfs = [hold_demo, hold_rg, hold_gam]
        #model = 
        #features = S 
        X, y, user_ids = preprocessing(months=months, features=features, dfs=dfs)
        predict(model, X, y, user_ids, store_name="holdout" store=True)