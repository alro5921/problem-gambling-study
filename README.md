# problem-gambling-study

## Background

Problem gambling is sad, For example:


This user lost nearly 30000 Euros over the course of five year,s I would like to see early warning indicators before people lose all their money/jobs.

## Dataset

Datasets were provided by the The Transparency Project.  They compiled a sample of 4000 subscribers from European online gambling website bwin. Half of these subscribers were flagged by the company’s Responsible Gaming (RG) system between November 2008 and November 2009, and the other half were controls matched to a flagged subscriber's deposit date. Three tables were provided: Demographic information of the subscribers, the gambling history of each subscriber, and the information associated with the Responsible Gaming intervention on each flagged user.

For the sake of brevity, I'll be referring to subscribers who had some Responsible Gaming intervention as *RG-flagged Users* and subscribers who haven't as *Non-RG Users*.

Note: I standardized the variance names and data types of each of the tables below from their raw ()

### Demographic Information

This table contained demographic information on each subscriber.

| Variable name     | Data type | Value                              |
|-------------------|-----------|-------------------------------------------------------|
| user_id    | Integer      | Loan identifier - Primary key                         |
| rg_case              | Boolean      | Borrower name                                         |
| country_name              | Text      | Borrower city                                         |
| language             | Text      | Borrower state                                        |
| gender               | Text      | Borrower zip code                                     |
| registration_date              | Date      | Bank (lender) name                                    |
| first_deposit_date        | Date      | Bank (lender) state                                   |

167 non-RG users subscribers lacked a birth year and a registration date, which I filled in with the average non-

### Gambling Behavior

This table has the gambling behavior of between May 2000 and November 2010. Each row contains a user's gambling behavior with a product on a given day, and include information such as the number of bets placed and the amount gambled and lost (the `turnover` and `hold` respectively) that day on that activity.

| Variable name     | Data type | Description                             |
|-------------------|-----------|-------------------------------------------------------|
| user_id    | Integer      | Subscriber's ID.                        |
| date              | Date      | Date of associated data.                                         |
| product_type              | Integer      | ID of the product type                                         |
| turnover             | Number      | Total stakes on the given day and product (in Euros)                                     |
| hold               | Number      | Total amount lost on the given day and product in (Euros). A negative number indicates won money.                                      |
| num_bets              | Integer      | Number of "bets" placed on the given day and product.                                 |

Each rows represented a user’s gambling behavior with a product (fixed-odds betting, live action-betting, poker etc) on a given day, and includes #bets placed and the amount gambled&lost (turnover&hold) that day.

The `turnover` is somewhat misleading when the stakes are not all or nothing and repeated; if a game reports

Five most frequently played products (in terms of at least one bet placed a day):

| Product    | Days in Use| Average bets per Day | Average Hold per day (Euros)
|-------------------|-----------|-----------------|--------------------------------------|
| Sportsbook: Fixed Odds    | 399,000    | 6.2                        | 7.3
| Sportsbook: Live Action             | 332,000      | 13.4   | 21.0
| Poker             | 127,000      | 110.7          | Unknown (see below)
| Casino Chartwell   | 38,000      | 335.6     | 50.0
| Minigames    | 26,000      | 125.8      | Unknown (see below)
| Casino Boss media 2     | 21,000  | 240.2   | 50.2

Unfortunately, many of the products lacked turnover and hold data because of a "data storage" error. This accounted for roughly 20% of the rows lacked actual monetary loss data, although activity was preserved.

The activity level "number of bets" implies varies wildly between products; we'd expect more individual "bets" from an online poker player, who could play dozens of hands an hour, than a fixed-odds sports better placing a handful of bets on a game. I attempt standardize across products by weighting each product to its average bets per day, which lets me do a more meaningful total activity metric than something that'd otherwise be dominated by e.g Casino Chartwell or Poker activity.

### Responsible Gaming Intervention Information

This table held the the information on the Responsible Gambling interventions for the flagged subscribers.

| Variable name     | Data type | Description                             |
|-------------------|-----------|-------------------------------------------------------|
| user_id    | Integer      | Subscriber's ID.                       |
| events    | Integer      | Number of RG events the userhad.                       |
| first_date              | Date      | Date of the user's first RG event.                                         |
| last_date             | Integer      | Date of the user's last RG event.                                       |
| event_type_first             | Number      | The ID of the type of RG event.                                  |
| inter_type_first               | Number      | The ID of the type of intervention from bwin.                       |

The events and the interventions varied, here's the four most frequent events 

 | Events/Outcome             | Frequency |
 |---------------------|-------------:|
 | __Previous RG Appeal__ |      932        |
 |    Account Reopen        |        572 |
 |    Appeal Denied          |        274 | 
 |    Full(er) Block         |        75 | 
 | __RG Problem__       |      334        |  
 |    Full Block       |        193 |  
 |    Advice from bwin           |        132 |
 | __Requested Deposit Limit Change__      |     308      |             
 |    Max Deposit Lowered       |        304 |
 | __Requested (Partial) Block__           |      274       |
 |    Block Approved      |   137 |
 |    Block Partially Done           |        106 |
 |    Requested Block Impossible           |        26 |

The previous RG appeals are problematic for this analysis; they dealt with RG interventions that happened *before* November 2008, which means the RG-flagged user's behavior that lead to a ban didn't actually correspond with the recorded date (and would in fact be zero if it was a full ban!):

![](images/RG_reopen.png)

I end up discarding these rows, which unfortunately accounts for almost half my RG users.

I also only have detailed data on the _first_ Responsible Gaming intervention in the timeframe; I can't 

## Data Analysis

### Weekend Periodicity

There appears to be weekend periodicity. Both because of the work week and because sports events, Primier Soccer in particular, are scheduled on the weekend. 

![](images/weekend_period.png)

(Suprisingly not maybe!). Perhaps we think problem gamblers are more likely to play on weekdays, as opposed to weekends?

## EDA 

### Gambling Quantity

As we would expect, an RG-flagged user is significantly more active per gambling day than 

|            |   turnover |      hold | weighted_bets |
|-----------:|-----------:|----------:|--------------:|
|     Non-RG |  88.747338 |  6.101446 |      2.633354 |
| RG-Flagged | 390.073958 | 19.300520 |      5.747101 |

### Product Type

Of note is that RG-flagged users played much proportionally more _live-action_ sports betting than _fixed-odds_ betting.

|              | Fixed Odds | Live Action | Fixed-Live Ratio |   |
|--------------|------------|-------------|-------|---|
| *RG Users*     | 0.372887   | 0.362723    | **1.03**  |   |
| *Non RG Users* | 0.568620   | 0.220037    | **2.59**  |   |

So it seems worthwhile to specifically track Live Action activity, or at least keep track of how much fixed gambling to live action gambling a patron does.

## Modelling

Our ultimate goal is to have useful predictive power about whether a user will experience or request an RG in the future, hopefully in a timeframe that's useful. Here the goal is to predict whether there's an RG event a year out, given the previous two years of data.

Our model will be using the following features, seperated into summary features of the user and time series features that use the specific day-to-day/week-to-week features. 

* Summary and Demographic Features
    * User age
    * The maximium hold in a single day 
    * Fixed-Odds to Live-Action Sports betting ratio 
* Time Series Features
    * Weekly Hold
    * Rolling Average of the Weekly Hold
    * Weekly (Weighted) Bets

### Making the Frames

Recall that the Responsible Gaming inteventions are only between November 2008 and November 2009. I split this period with 4 cutoffs of three months; if there's an RG event within the next year of that cutoff, the frame is labelled positive. The year itself looks back in

### Sampling

The initial dataset was balanced between RG-flagged and non-RG users. But the positive and negative frames have become significantly unbalanced:

* We've discarded over half of our RG set because of "Reopen" codes. 
* All frames created from a non-RG user are going to be negative class, while frames from an RG user are going to be a mix of positive and negative class.
* We're discarding a frame if it has an RG event in it, further cutting our positive frame.

Naively applying our framing process to all valid entries creates roughly 20000 negative frames and 4000 positive frames. Obviously we want to balance those, so I undersample the negative frames to match the 4000 positive frames.

### Model

With the features and resampled data, I fit a Random Forest Model to . I use a randomized grid search for hyperparameter tuning:



Partially for convinence, but also because it's difficult to make intervention calls without enough data, I restrict my predictions to users who've registered within my lookback window.

### Interpretation

How do we use this model? That depends entirely on what planned early intervention we want to do. Are we simply sending the subscriber a non-compulsory email about gambling addiction and availiable interventions+resources? There we can accept a relatively large false positive rate. Are we taking a more drastic account action, such as a deposit limit or w/e? We'd want a much lower false positive rate.




The profit matrix depends entirely on the planned early intervention. Are we simply sending the subscriber a non-compulsory email about gambling addiction and availiable interventions+resources? There we can accept a relatively large false positive rate. Are we taking a more drastic account action, such as a deposit limit or w/e? We'd want a much lower false positive rate.

### Limitations

I discarded the "reopen" tickets, but in many cases the prior ban date can be pretty easily inferred by a rather sudden drop in activity!

I'm confident I could make a large portion of these dropped datapoints useful.

This of course comes from a casino's POV, who I'm not saying are biased here buuut. Also most of these are self-reported, the casino itself didn't do much actual p I'm not saying the casino didn't have the best interest of its patrons at heart.

I would very much like to run more models, LSTM in particular would be very interesting.