#I want to be able to run a function that
#pulls the data, prepares the data

from getData import *



#Pull the Data
def pullGames(years:list):
    '''Pull games for a given list of years'''
    #Get Games
    getgames = pd.DataFrame()

    for year in years:
        getgames = pd.concat([getgames,getData('games', {'year': year})])
    
    return getgames #return the data for each game

#Prepare the Data
def prepGames(df:pd.DataFrame):
    '''Cleans the data from the pullGames function'''
    games = df
    gamesdf = games.sort_values(by='start_date', ascending=True)

    #FBS AND FCS GAMES
    gamesdf = gamesdf[gamesdf['home_division'].isin(['fbs','fcs']) | gamesdf['away_division'].isin(['fbs','fcs'])]


    #FIX GAME DATES
    #Remove Kickoff Time
    gamesdf['start_date'] = pd.to_datetime(gamesdf['start_date'])
    gamesdf['start_date'] = gamesdf['start_date'].dt.strftime('%m/%d/%Y')
    gamesdf['start_date'] = pd.to_datetime(gamesdf['start_date'])

    return gamesdf #return the data for each game (cleaned)

