
DEMO_RENAME = {"USERID": "user_id", "RG_case" : "rg", "CountryName" : "country",
              "LanguageName" : "language", "Gender" : "gender", "YearofBirth" : "birth_year",
              "Registration_date" : "registration_date", "First_Deposit_Date" : "first_deposit_date"}

GAMBLING_RENAME = {"UserID": "user_id", "Date" : "date", "ProductType" : "product_type",
              "Turnover" : "turnover", "Hold" : "hold", "NumberofBets" : "num_bets"}

RG_RENAME = {"UserID": "user_id", "RGsumevents" : "events", "RGFirst_Date" : "first_date", 
             "Event_type_first" : "event_type_first", 
             "RGLast_date" : "last_date", "Interventiontype_first" : "inter_type_first"}

HAS_HOLD_DATA = [1,2,4,8,17]

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