
DEMO_RENAME = {"USERID": "user_id", "RG_case" : "rg", "CountryName" : "country",
              "LanguageName" : "language", "Gender" : "gender", "YearofBirth" : "birth_year",
              "Registration_date" : "registration_date", "First_Deposit_Date" : "first_deposit_date"}

GAMBLING_RENAME = {"UserID": "user_id", "Date" : "date", "ProductType" : "product_type",
              "Turnover" : "turnover", "Hold" : "hold", "NumberofBets" : "num_bets"}

RG_RENAME = {"UserID": "user_id", "RGsumevents" : "events", "RGFirst_Date" : "first_date", 
             "Event_type_first" : "event_type_first", 
             "RGLast_date" : "last_date", "Interventiontype_first" : "inter_type_first"}

HAS_HOLD_DATA = [1,2,4,8,17]

ALL_PRODUCTS = [1,2,3,4,5,6,7,8,9,10,14,15,16,17,19,20,21,22,23,24,25]

EVENT_CODE_DICT = {1: "Family Intervention", 2 : "acc close/open from RG", 3 : "Cancelled outpayment", 
                   4: "Manually Lowered Limit", 6: "Heavy Complainer", 7: "Requested pay method block",
                   8: "Reported as Minor", 9: "Request partial block", 10: "Reported Problem", 
                   11: "high deposit", 12 : "Two RG events on the day", 13: "Event unknown"}

INTERVENTION_CODE_DICT = {-1: "Intevention Unknown", 1: "Advice", 2: "Reopen", 
                          3: "Consumer request not technically possible", 4: "Block (pending invest)",
                          5: "VIP Deposit Change", 6: "Partial Block (incomplete)", 7: "Advice To 3rd Party",
                          8: "Partial Block", 9: "Inpayment not blocked", 10 : "Inpayment blocked",
                          11: "Higher deposit denied", 12 : "Higher Deposit Accepted", 13 : "Daily/weekly deposit changed", 
                          14: "Full Block", 15 : "Betting Limit Change", 16: "Remains Blocked", 
                          17 : "Blocked and Reimbursed", 18: "Requested Partial Block Not Possible"}

WEIGHTS = {1: 1.0, 2: 1.8293792046408552, 3: 0.03651375851416145, 
    4: 1.8820888336251267, 5: 0.0006019609096146426, 6: 0.438983651931958, 
    7: 0.04849395136604638, 8: 5.319030501466609, 9: 6.829378229015394e-05, 
    10: 5.552475722779929, 14: 0.17252082594500304, 15: 1.4943747874965794, 
    16: 3.902501845151654e-06, 17: 0.018900304248800105, 19: 0.04700904941396618, 
    20: 0.0030951717759359052, 21: 1.8049071033826397e-05, 22: 0.00021219853783012118, 
    23: 0.002884436676297716, 24: 2.536626199348575e-05, 25: 0.0003814695553635742}

DEMO_PATH = 'data/demographic.csv'
RG_PATH = 'data/rg_information.csv'
GAM_PATH = 'data/gambling.csv'

