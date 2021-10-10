import requests
import pandas as pd

# get NHL teams
r = requests.get('https://statsapi.web.nhl.com/api/v1/teams')
# convert to DataFrame
teams = pd.DataFrame(r.json()['teams']).set_index('id')

players = pd.DataFrame()
all_stats = pd.DataFrame()
# get roster for each team
for link in teams.link:
    # get team info
    r_team = requests.get('https://statsapi.web.nhl.com' + link, params={'expand': 'team.roster'})
    # get roster
    roster = r_team.json()['teams'][0]['roster']['roster']

    # convert roster to DataFrame
    for person in roster:
        # get player info
        player = pd.Series(person['person'])
        # add position
        player.loc['position'] = person['position']['type']
        player.loc['position_code'] = person['position']['code']
        # add team
        player.loc['team'] = r.json()['teams'][0]['name']

        # get stats
        r_player = requests.get('https://statsapi.web.nhl.com' + player.link + '/stats', params={'stats': 'gameLog',
                                                                                                 'season': '20202021'})
        games = r_player.json()['stats'][0]['splits']
        for game in games:
            stats = pd.Series(game['stat'])
            stats['opponent'] = game['opponent']['name']
            stats['team'] = game['team']['name']
            stats['date'] = game['date']
            stats['isHome'] = game['isHome']
            stats['player'] = player.fullName
            stats['position'] = player['position']
            # TODO: add fantasy points
            all_stats = all_stats.append(stats, ignore_index=True)

        # append to players
        players = players.append(player, ignore_index=True)

# convert id to int
players['id'] = players.id.astype('int')
# make id the index
players.set_index('id', inplace=True)

if __name__ == '__main__':
    stats.to_csv('stats.csv', index=False)
    players.to_csv('players.csv', index=False)
