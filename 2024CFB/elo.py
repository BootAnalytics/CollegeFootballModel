import pandas as pd
import numpy as np

def setupELOData(stat,df):
    #Create the dataframe that will be input for dualELO()
    inputdf = df.copy().query("~((win_home==0)&(win_away==0))")
    if stat == 'ypp':
        inputdf['predict_home'] = models[stat].predict(sm.add_constant(inputdf[f'{stat}_home']))
        inputdf['predict_away'] = models[stat].predict(sm.add_constant(inputdf[f'{stat}_away']))
    elif stat == 'HavocRatio':
        inputdf['predict_home'] = models[stat].predict(sm.add_constant(inputdf[[f'{stat}_away','ypp_home']]))
        inputdf['predict_away'] = models[stat].predict(sm.add_constant(inputdf[[f'{stat}_home','ypp_away']]))
    else:
        inputdf['predict_home'] = models[stat].predict(sm.add_constant(inputdf[[f'{stat}_home','ypp_home']]))
        inputdf['predict_away'] = models[stat].predict(sm.add_constant(inputdf[[f'{stat}_away','ypp_away']]))
        #inputdf['predict_home'] = inputdf.apply(lambda row: adj_win(row[f'{stat}_home'],stat,row['win_home']),axis=1)
        #inputdf['predict_away'] = inputdf.apply(lambda row: adj_win(row[f'{stat}_away'],stat,row['win_away']),axis=1)
    
    return inputdf

#Rebalance the Exponent Adjustment
def get_expected_stat(rating, opp_rating):
    exp = (opp_rating - rating)/400
    return 1 / (1 + 10**exp)

#k = amount of adjustment
def get_new_stats(home_rating, away_rating, margin,k=30):
    k = k
    threshold=.85
    '''NEW FORMULATION'''
    home_score = margin
    
    #get pregame expected home score
    expected_home_score = get_expected_stat(home_rating, away_rating)


    #kmod = (min(home_rating,away_rating)/(home_rating+away_rating))*2
    #k=k*kmod


    ### Calculate NEW OFFSET VALUES
    #Only Occurs when EXPECTED_HOME_SCORE or EXPECTED_AWAY_SCORE is above threshold (80%)
    #Only calculate on one side (otherwise both teams would just be passing points)
    #PENALTY VERSION - Only "losing team" gets docked points
    #if (expected_home_score > threshold)&(margin>expected_home_score):
    #    overage_away=(margin-expected_home_score)*k/2
    #    overage_home=0
    #elif (expected_home_score < (1-threshold))&(margin<expected_home_score):
    #    overage_home=(margin-expected_home_score)*k/2
    #    overage_away=0
    #else: overage_away,overage_home=0,0

    #if (margin > threshold):
    #    overage=(margin-threshold)*k
    #elif (margin < (1-threshold)):
    #    overage=(margin-threshold)*k
    #else: overage=0

    #print(margin, expected_home_score, overage)

    ###
    
    #calculate NEW home score
    new_home_score = home_rating + k * (home_score - expected_home_score) #+ overage_home#/2

    
    #Repeat the above for the away team
    away_score = 1 - home_score
    expected_away_score = get_expected_stat(away_rating, home_rating)
    new_away_score = away_rating + k * (away_score - expected_away_score) #- overage_away#/2
    
    #return a tuple
    try:
        return (round(new_home_score), round(new_away_score))
    except:
        print(home_rating,away_rating,margin)
        print(expected_home_score,new_home_score,expected_away_score,new_away_score)
        return (round(new_home_score), round(new_away_score))



def dualELO(inputdf,k=30):
    k=k
    statgames = inputdf.copy().dropna(subset=['predict_home','predict_away'])
    
    # dict object to hold current Offense & Defense Elo rating for each team
    #teamsStat = dict()
    offStat = dict()
    defStat = dict()


    # dict object to hold check through each iteration
    #complete_check = dict()
    checkStat = []

    #object to hold daily rankings
    daily = []

    #**I ONLY WANT TO USE RECURSION WITHIN THE SEASON*** SO I NEED TO SPLIT THE LOOP FOR EACH SEASON
    for season in statgames['season'].unique():
        for date in statgames[statgames['season']==season]['start_date'].unique():
            #Get all games prior to most recent date
            #convert to dictionary
            stats = statgames[(statgames['start_date']<=date)&(statgames['season']==season)].to_dict('records')

            confs = ['FBS Independents', 'American Athletic', 'Mountain West', 'Big Ten', 'Big 12','Mid-American', 'Sun Belt','SEC', 'ACC', 'Pac-12', 'Conference USA']

            # dict object to hold current Elo rating for each team
            #teams = dict()
            #dict object to check how the expected vs actual works out
            #check = []

            # loop through games in order
            for stat in stats:

                #HOME OFFENSE VS AWAY DEFENSE*************
                # get current rating for home team
                if stat['home_team'] in offStat:
                    home_off_elo = offStat[stat['home_team']]
                elif stat['home_conference'] in confs:
                    # if no rating, set initial rating to 1500 for FBS teams
                    home_off_elo = 1500
                else:
                    # otherwise, set initial rating to 1200 for non-FBS teams
                    home_off_elo = 1200

                # get current rating for away team
                if stat['away_team'] in defStat:
                    away_def_elo = defStat[stat['away_team']]
                elif stat['away_conference'] in confs:
                    # if no rating, set initial rating to 1500 for FBS teams
                    away_def_elo = 1500
                else:
                    # otherwise, set initial rating to 1200 for non-FBS teams
                    away_def_elo = 1200


                #HOME DEFENSE VS AWAY OFFENSE*************
                # get current rating for home team
                if stat['home_team'] in defStat:
                    home_def_elo = defStat[stat['home_team']]
                elif stat['home_conference'] in confs:
                    # if no rating, set initial rating to 1500 for FBS teams
                    home_def_elo = 1500
                else:
                    # otherwise, set initial rating to 1200 for non-FBS teams
                    home_def_elo = 1200

                # get current rating for away team
                if stat['away_team'] in offStat:
                    away_off_elo = offStat[stat['away_team']]
                elif stat['away_conference'] in confs:
                    # if no rating, set initial rating to 1500 for FBS teams
                    away_off_elo = 1500
                else:
                    # otherwise, set initial rating to 1200 for non-FBS teams
                    away_off_elo = 1200

                #Now we've assigned 4 Variables: home_off_elo,away_def_elo,home_def_elo,home_away_elo

                # Now assign two margin variables
                try:
                    home_margin = stat['predict_home'] #Win% of Home Team
                    away_margin = stat['predict_away'] #Win% of Away Team
                except:
                    print(stat[['predict_home','predict_away']])


                # Need to create 2 sets of ELO updates
                #try:
                new_elos1 = get_new_stats(home_off_elo, away_def_elo, home_margin,k)
                new_elos2 = get_new_stats(away_off_elo, home_def_elo, away_margin,k)
                #except:
                #    print(home_off_elo,away_off_elo,home_def_elo,away_def_elo)

                # set pregame elos on game dict
                stat['pregame_home_off_elo'] = home_off_elo
                stat['pregame_away_def_elo'] = away_def_elo
                stat['pregame_home_def_elo'] = home_def_elo
                stat['pregame_away_off_elo'] = away_off_elo

                #add in expected game_control
                #stat['expected_game_control'] = get_expected_stat(home_elo, away_elo)
                #stat['ball_control'] = margin

                # set postgame elos on game dict
                stat['postgame_home_off_elo'] = new_elos1[0]
                stat['postgame_away_def_elo'] = new_elos1[1]
                stat['postgame_home_def_elo'] = new_elos2[1]
                stat['postgame_away_off_elo'] = new_elos2[0]

                # set current elo values in teams dict
                offStat[stat['home_team']] = new_elos1[0]
                defStat[stat['away_team']] = new_elos1[1]
                defStat[stat['home_team']] = new_elos2[1]
                offStat[stat['away_team']] = new_elos2[0]


                #populate the check dictionary
                #**Only populate the checker if it is the "CURRENT" week's games (last date in each loop)
                #Iteration Date is the "current date"
                same = stat['start_date'] == date

                checkStat.append({'season': stat['season'],
                              'game_date': stat['start_date'],
                              'iteration_date':date,
                              'current': same,
                              'home_team': stat['home_team'],
                              'away_team': stat['away_team'],
                              'home_points': stat['home_points'],
                              'away_points': stat['away_points'],

                              'pregame_home_off': stat['pregame_home_off_elo'],
                              'pregame_away_def': stat['pregame_away_def_elo'],
                              'pregame_home_def': stat['pregame_home_def_elo'],
                              'pregame_away_off': stat['pregame_away_off_elo'],
                              'postgame_home_off': stat['postgame_home_off_elo'],
                              'postgame_away_def': stat['postgame_away_def_elo'],
                              'postgame_home_def': stat['postgame_home_def_elo'],
                              'postgame_away_off': stat['postgame_away_off_elo'],


                              'home_division': stat['home_division'],
                              'away_division': stat['away_division'],
                              'neutral_site': stat['neutral_site'],
                             'week':stat['week'],
                              'id':stat['id'],

                             'home_expected':get_expected_stat(home_off_elo, away_def_elo),
                             'away_expected':get_expected_stat(away_off_elo, home_def_elo),

                             'home_actual':home_margin,
                             'away_actual':away_margin
                                })
    return offStat,defStat,checkStat,daily
