from getData import *


def pullStats(years:list):
    '''Get game stats from the CFB Data API for the given years'''
    stats = []
    kick = []

    for year in years:
        for week in np.arange(0,20):
        #for c in confs:
            try:
                stats = stats + getData('games/teams', {'year': year, 'week':week},output='json')
                kick = kick + getData('games/players', {'year': year, 'week':week, 'category':'kicking'},output='json') #temp*
            except:
                pass
    return stats, kick #Output STATS as json style data to be processed

def prepStats(stats:json, kick:json):
    '''Cleans the data from the pullStats function and creates a DF'''
    reslist = []
    for y in stats:
        
        #display(y['id'])
        for team in y['teams']:
            res = {}
            #display(team['school'])
            k = [x['category'] for x in team['stats']]
            v = [x['stat'] for x in team['stats']]
            
            res['id'] = y['id']
            res['school'] = team['school']
            for key,value in zip(k,v):
                res[key] = value
            reslist.append(res)

    reslist2 = []
    for y in kick:
        
        #display(y['id'])
        for team in y['teams']:
            #res = {}
            #get all kickers
            try:
                aths = [x['athletes'] for x in team['categories'][0]['types'] if x['name']=='FG'][0]
                #display(aths)

                #loop through kickers to get stats
                for x in aths:
                    res = {}
                    n = x['stat'].find("/")
                    #print(x)
                    make = x['stat'][:n]
                    att = x['stat'][n+1:]

                    res['id'] = y['id']
                    res['school'] = team['school']
                    res['FGs'] = int(make)
                    res['FGAtt'] = int(att)
                    #for key,value in zip(k,v):
                    #    res['FG'] = value
                    reslist2.append(res)
            except: pass

    #Merge the data together

    return pd.merge(pd.DataFrame(reslist),pd.DataFrame(reslist2),how='left',on=['id','school'])
    #return reslist,reslist2 #Output formatted STATS (can be converted to json)


    #Probably Need a 2nd cleaning function
def prepStats2(stats):
    '''Calculates Efficiency Metrics'''
    stats=stats
    stats[['completions','passingAttempts']] = stats['completionAttempts'].str.split('-', expand=True)
    stats['ypp'] = stats['totalYards'].astype(float) / (stats['rushingAttempts'].astype(float) + stats['passingAttempts'].astype(float))

    stats[['compl','passAtts']] = stats['completionAttempts'].str.split('-',expand=True).astype(float)
    stats[['3rdSuc','3rdOcc']] = stats['thirdDownEff'].str.split('-',expand=True).astype(float)
    stats['fourthDownEff']= stats['fourthDownEff'].str.replace('--','-').fillna('0-0')
    stats[['4thSuc','4thOcc']] = stats['fourthDownEff'].str.split('-',expand=True).astype(float, errors='ignore')

    stats['havoc']= stats[['passesIntercepted','fumblesRecovered','sacks','qbHurries','passesDeflected','tacklesForLoss']].fillna(0).astype(float).sum(axis=1)

    stats['playsTotal'] = stats['passAtts']+stats['rushingAttempts'].astype(float)

    stats[['yardsPerPass','yardsPerRushAttempt']] = stats[['yardsPerPass','yardsPerRushAttempt']].astype(float)


    #Add in FG stats
    #stats = stats.merge(kick,how='left',on=['id','school'])

    stats['TDRatio']=(stats['rushingTDs'].astype(float)+stats['passingTDs'].astype(float))/stats['playsTotal']
    stats['TurnoverRatio']=stats['turnovers'].astype(float)/stats['playsTotal']
    stats['MCRatio']=(stats['3rdOcc']+stats['4thOcc'])/stats['playsTotal']
    stats['FailedConvRatio']= ((stats['3rdOcc']+stats['4thOcc']) - (stats['3rdSuc']+stats['4thSuc']))/stats['playsTotal']

    stats['HavocRatio'] = stats['havoc']/stats['playsTotal']

    stats['FGAttRatio'] = stats['FGAtt']/stats['playsTotal']
    stats['FGRatio'] = stats['FGs']/stats['playsTotal']
    stats['FDRatio'] = stats['firstDowns'].astype(float)/stats['playsTotal']

    stats['ypp'] = stats['totalYards'].astype(float) / (stats['playsTotal'].astype(float))

    #FirstDown Ratio, Special Teams? (non-play yards), Style: Aggression, Dominance, Run/Pass
    #print('ran2')
    stats.replace(np.inf,np.nan,inplace=True)
    return stats