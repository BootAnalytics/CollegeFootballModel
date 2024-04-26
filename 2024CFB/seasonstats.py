from gamePrep import *
from getStats import *

def getSeasonStats(year):
    '''These are all the steps needed to get games and stats for each season'''
    games = pullGames([year])
    stat = pullStats([year])
    stats2 = prepStats(stat[0],stat[1])
    newstats = prepStats2(stats2)

    statgames = games.reset_index(drop=True).merge(newstats, how='left', left_on=['id','home_team'],right_on=['id','school'])\
        .merge(newstats, how='left', left_on=['id','away_team'],right_on=['id','school'], suffixes=('_home','_away'))

    statgames = statgames.dropna(subset=['school_home']).assign(win_home = lambda x: np.where(x['home_points']>x['away_points'],1,0)).assign(win_away = lambda x: np.where(x['away_points']>x['home_points'],1,0))
    return statgames
